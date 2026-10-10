# Task-tracking API — DD2482 2026

Project by Hasan Kalzi and Love Lingren. This repository provides a FastAPI API with
SQLite persistence, input validation, automated behavioural tests and Docker Compose packaging.

The API supports creating, listing, retrieving and completing tasks. Tests also check
storage failures and persistence across a real server-process restart.

## Run and test

Use Python 3.12. In Windows Git Bash:

```bash
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
./.venv/Scripts/python.exe -m ruff check app tests scripts
./.venv/Scripts/python.exe -m ruff format --check app tests scripts
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On Linux/WSL create the environment with `python3.12 -m venv .venv` and use
`./.venv/bin/python` in place of `./.venv/Scripts/python.exe`.
Open [API documentation](http://localhost:8000/docs) or [health](http://localhost:8000/health).
Stop the server with Ctrl+C. Data is stored in `data/tasks.db`, excluded from Git.

Ansible and GitHub CI/CD are planned for subsequent increments. This is a local prototype
without authentication; use synthetic data and loopback access.
See [documented AI assistance](docs/ai-use.md).

## Docker and Compose

Start Docker Desktop with Linux containers (or use Docker Engine on Linux) and a Compose
version supporting `--wait`. From the repository root:

```bash
TASK_API_IMAGE=task-api:dev docker compose -f compose.yaml -f compose.build.yaml build --pull
TASK_API_IMAGE=task-api:dev docker compose -f compose.yaml up -d --wait --wait-timeout 60
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

The API is available at [localhost:8000/docs](http://localhost:8000/docs). It runs as a
non-root user with a read-only root filesystem; SQLite writes to the named `task-data`
volume at `/data/tasks.db`. This container volume is separate from local Python's `data/`.
Use `docker compose -f compose.yaml down` to stop the stack while keeping its data.

Check container behaviour and persistence in a disposable test stack:

```bash
./.venv/Scripts/python.exe scripts/container_check.py --image task-api:dev --version dev
```

The check uses a random Compose project and available port, creates/completes a task,
recreates the container and verifies that the saved task remains. It removes its own test
stack and volume afterwards. Runtime `compose.yaml` uses an existing image;
`compose.build.yaml` adds the local source build configuration.

