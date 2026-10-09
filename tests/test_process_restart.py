"""Use real HTTP and a new server process, not just a second TestClient."""

import json
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from urllib.error import URLError
from urllib.request import Request, urlopen


def request(url, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    with urlopen(
        Request(url, data=data, method=method, headers={"Content-Type": "application/json"}),
        timeout=2,
    ) as response:
        return json.load(response)


@contextmanager
def server(tmp_path):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = os.environ | {"DATABASE_PATH": str(tmp_path / "persistent.db"), "APP_VERSION": "test"}
    with (tmp_path / "server.log").open("a") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            env=env,
            stdout=log,
            stderr=log,
        )
        url = f"http://127.0.0.1:{port}"
        try:
            deadline = time.monotonic() + 15
            while True:
                if process.poll() is not None:
                    raise AssertionError((tmp_path / "server.log").read_text())
                try:
                    request(url + "/health")
                    break
                except URLError:
                    if time.monotonic() >= deadline:
                        raise AssertionError("Server did not become ready") from None
                    time.sleep(0.1)
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def test_persistence_across_process_restart(tmp_path):
    with server(tmp_path) as url:
        task = request(url + "/tasks", "POST", {"title": "Survive a real restart"})
        request(url + f"/tasks/{task['id']}", "PATCH", {"completed": True})
    with server(tmp_path) as url:
        saved = request(url + f"/tasks/{task['id']}")
        assert saved == task | {"completed": True}
