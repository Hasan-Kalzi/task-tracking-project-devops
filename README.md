# Task-tracking API — DD2482 2026

Project by Hasan Kalzi and Love Lingren. This first increment provides a FastAPI API with
SQLite persistence, input validation and automated behavioural tests.

The API supports creating, listing, retrieving and completing tasks. Tests also check
storage failures and persistence across a real server-process restart.

## Run and test

Use Python 3.12. In Windows Git Bash:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On Linux/WSL use `python3.12 -m venv .venv` and `source .venv/bin/activate` instead.
Open [API documentation](http://localhost:8000/docs) or [health](http://localhost:8000/health).
Stop the server with Ctrl+C. Data is stored in `data/tasks.db`, excluded from Git.

Docker, Ansible and GitHub CI/CD are planned for subsequent increments. This increment is
a local prototype without authentication; use synthetic data and loopback access.
See [documented AI assistance](docs/ai-use.md).
