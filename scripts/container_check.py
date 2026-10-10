"""Exercise a disposable Compose deployment; never touch the student's deployment volume."""

import argparse
import json
import os
import subprocess
import time
import uuid
from urllib.error import URLError
from urllib.request import Request, urlopen


def http(url, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    with urlopen(
        Request(url, data=data, method=method, headers={"Content-Type": "application/json"}),
        timeout=5,
    ) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    env = os.environ | {"TASK_API_IMAGE": args.image, "API_PORT": "0"}
    command = [
        "docker",
        "compose",
        "-p",
        "taskcheck-" + uuid.uuid4().hex[:10],
        "-f",
        "compose.yaml",
    ]

    def compose(*arguments, capture=False):
        return subprocess.run(
            command + list(arguments), env=env, check=True, text=True, capture_output=capture
        )

    def endpoint():
        mapping = compose("port", "api", "8000", capture=True).stdout.strip()
        return "http://" + mapping

    def ready(url):
        deadline = time.monotonic() + 45
        while True:
            try:
                health = http(url + "/health")
                assert health == {"status": "ok", "version": args.version}, health
                return
            except URLError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Container readiness timed out") from None
                time.sleep(0.5)

    try:
        compose("up", "-d", "--wait", "--wait-timeout", "60")
        url = endpoint()
        ready(url)
        task = http(url + "/tasks", "POST", {"title": "Container persistence check"})
        saved = task | {"completed": True}
        assert http(url + f"/tasks/{task['id']}", "PATCH", {"completed": True}) == saved
        # Recreate the container, so the test depends on the volume, not writable image layers.
        compose("up", "-d", "--force-recreate", "--wait", "--wait-timeout", "60")
        url = endpoint()
        ready(url)
        assert http(url + f"/tasks/{task['id']}") == saved
        assert saved in http(url + "/tasks?completed=true")
        print("Container health, HTTP operations and volume persistence passed.")
    except BaseException:
        subprocess.run(command + ["logs", "--no-color"], env=env, check=False)
        raise
    finally:
        # Only the randomly named test stack/data created by this script is removed.
        compose("down", "--volumes", "--remove-orphans")


if __name__ == "__main__":
    main()
