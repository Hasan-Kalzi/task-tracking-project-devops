"""Small persistent API: application behaviour stays separate from delivery tooling."""

import logging
import os
import sqlite3
from contextlib import asynccontextmanager, closing
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi import Path as ApiPath
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictBool, StringConstraints

LOGGER = logging.getLogger(__name__)
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    completed: StrictBool


class Task(BaseModel):
    id: int
    title: str
    completed: bool


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def initialise(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as connection, connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise RuntimeError(f"Unsupported database schema {version}; expected 0 or 1")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 200), "
            "completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1)))"
        )
        connection.execute("PRAGMA user_version = 1")


def create_app(database_path: Path | None = None, version: str | None = None) -> FastAPI:
    path = database_path or Path(os.environ.get("DATABASE_PATH", "data/tasks.db"))
    app_version = version or os.environ.get("APP_VERSION", "dev")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        # Fail startup if storage/schema is unusable rather than accepting requests.
        initialise(path)
        yield

    api = FastAPI(title="Task-tracking API", version=app_version, lifespan=lifespan)

    @api.exception_handler(sqlite3.Error)
    async def storage_error(_request: Request, exc: sqlite3.Error):
        LOGGER.error("Database operation failed: %s", type(exc).__name__)
        return JSONResponse(status_code=503, content={"detail": "Storage unavailable"})

    @api.get("/health")
    def health():
        with closing(connect(path)) as connection:
            connection.execute("SELECT id FROM tasks LIMIT 1").fetchone()
        return {"status": "ok", "version": app_version}

    @api.post("/tasks", response_model=Task, status_code=201)
    def create_task(body: TaskCreate):
        # Parameters are bound, including titles containing quotes or SQL syntax.
        with closing(connect(path)) as connection, connection:
            cursor = connection.execute("INSERT INTO tasks(title) VALUES (?)", (body.title,))
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,))
            return dict(row.fetchone())

    @api.get("/tasks", response_model=list[Task])
    def list_tasks(
        completed: bool | None = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        where = "" if completed is None else " WHERE completed = ?"
        parameters = () if completed is None else (int(completed),)
        with closing(connect(path)) as connection:
            rows = connection.execute(
                "SELECT * FROM tasks" + where + " ORDER BY id LIMIT ? OFFSET ?",
                (*parameters, limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]

    @api.get("/tasks/{task_id}", response_model=Task)
    def get_task(task_id: Annotated[int, ApiPath(ge=1)]):
        with closing(connect(path)) as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Task not found")
        return dict(row)

    @api.patch("/tasks/{task_id}", response_model=Task)
    def update_task(task_id: Annotated[int, ApiPath(ge=1)], body: TaskUpdate):
        with closing(connect(path)) as connection, connection:
            cursor = connection.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?", (int(body.completed), task_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(404, "Task not found")
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return dict(row)

    return api


app = create_app()
