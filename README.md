# Task-tracking API — DD2482 2026

Project by Hasan Kalzi and Love Lingren. FastAPI validates task requests; SQLite
persists tasks. GitHub Actions checks changes and delivers tested versioned
images. Ansible provisions a separate Ubuntu VM and applies the delivered image.

Public repository: https://github.com/Hasan-Kalzi/task-tracking-project-devops

## Run and test

Use Python 3.12. In Windows Git Bash, use the environment's Python explicitly:

```bash
py -3.12 -m venv .venv &&
./.venv/Scripts/python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock &&
./.venv/Scripts/python.exe -m pip check &&
./.venv/Scripts/python.exe -m ruff check app tests scripts &&
./.venv/Scripts/python.exe -m ruff format --check app tests scripts &&
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open [API documentation](http://localhost:8000/docs) or
[health](http://localhost:8000/health). Stop the server with Ctrl+C.
Local Python stores its database in ignored `data/tasks.db`.

On Linux/WSL, keep a separate environment under the Linux home directory.
With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed:

```bash
"$HOME/.local/bin/uv" venv --python 3.12.14 --managed-python --seed .venv &&
./.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock &&
./.venv/bin/python -m pip check
```

On an Ubuntu 24.04 system with Python 3.12 and its venv package installed,
`python3.12 -m venv .venv` is also supported.
Use `./.venv/bin/python` for the equivalent tests and server commands.
Ansible is included only on non-Windows platforms.

## Docker

Use Docker Engine with Compose, or Docker Desktop with Linux containers.
Run from the repository root:

```bash
TASK_API_IMAGE=task-api:dev docker compose -f compose.yaml -f compose.build.yaml build --pull &&
TASK_API_IMAGE=task-api:dev docker compose -p task-api -f compose.yaml up -d --wait --wait-timeout 60 &&
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

The container runs as UID/GID 10001, drops capabilities and has a read-only root
filesystem. SQLite writes to the named volume at `/data/tasks.db`.
Stop with `docker compose -p task-api -f compose.yaml down`; keep the volume.

Verify HTTP behaviour and persistence in an isolated disposable stack:

```bash
./.venv/Scripts/python.exe scripts/container_check.py --image task-api:dev --version dev
```

On Linux use `./.venv/bin/python`. The check creates/completes a task, forces
container recreation, verifies saved data and removes only its own test volume.

## CI and delivery

CI runs Ruff, 25 behavioural tests, Ansible syntax checks, Compose validation,
an image build and container/persistence checks. The tag-triggered delivery
workflow repeats validation through `bash scripts/checks.sh VERSION`, then saves
the exact tested image. It publishes four assets after successful checks:

- `image.tar.gz`: tested Linux/amd64 Docker image;
- `task-api-VERSION-deployment.tar.gz`: tracked configuration and documentation;
- `release.json`: source commit, version, image ID and platform;
- `SHA256SUMS`: checksums for the three delivered files.

After review and merge, push an immutable tag such as `v0.1.0`.
The release starts as a draft and becomes public after its assets upload.
A publication failure may leave a draft to inspect; tags are never moved.
Delivery prepares an artefact; VM deployment is a separate manual invocation.

Run the full gate from a fresh Linux clone with Docker available:

```bash
source .venv/bin/activate &&
bash scripts/checks.sh dev
```

See [architecture](docs/architecture.md), [infrastructure setup](docs/infrastructure.md),
[release/deployment/rollback runbook](docs/runbook.md),
[recorded evidence](docs/evidence.md) and [AI assistance](docs/ai-use.md).
The [report draft](docs/report-draft.md) requires actual release/VM results and final
2–3-page formatting before submission.

This is a single-instance prototype without authentication or TLS. Use synthetic
data and loopback access. The deployment target is a separate Ubuntu 24.04 x86_64
VM; WSL is the development controller. The VM prerequisite and manual rollback
are documented in the runbook.
