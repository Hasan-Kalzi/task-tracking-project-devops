import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "tasks.db", version="v0.1.0")) as session:
        yield session


def test_create_read_complete_and_filter(client):
    assert client.get("/tasks").json() == []
    response = client.post("/tasks", json={"title": "  Review the pipeline  "})
    assert response.status_code == 201
    task = response.json()
    assert task == {"id": 1, "title": "Review the pipeline", "completed": False}
    assert client.get("/tasks/1").json() == task
    assert client.patch("/tasks/1", json={"completed": True}).json()["completed"] is True
    assert len(client.get("/tasks?completed=true").json()) == 1
    assert client.get("/tasks?completed=false").json() == []
    assert client.patch("/tasks/1", json={"completed": False}).json()["completed"] is False


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"title": ""},
        {"title": " \t "},
        {"title": "x" * 201},
        {"title": 3},
        {"title": "ok", "completed": True},
    ],
)
def test_reject_invalid_creation_without_changing_storage(client, body):
    assert client.post("/tasks", json=body).status_code == 422
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"completed": "true"},
        {"completed": 1},
        {"completed": None},
        {"completed": True, "title": "new"},
    ],
)
def test_reject_invalid_update(client, body):
    client.post("/tasks", json={"title": "Keep this"})
    assert client.patch("/tasks/1", json=body).status_code == 422
    assert client.get("/tasks/1").json()["completed"] is False


def test_missing_task(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"completed": True}).status_code == 404


@pytest.mark.parametrize(
    "url",
    [
        "/tasks/0",
        "/tasks/-1",
        "/tasks/abc",
        "/tasks?limit=0",
        "/tasks?limit=101",
        "/tasks?offset=-1",
    ],
)
def test_invalid_identifiers_and_pagination(client, url):
    assert client.get(url).status_code == 422


def test_sql_text_is_data_and_listing_is_paginated(client):
    titles = ["'); DROP TABLE tasks; --", "second", "third"]
    for title in titles:
        assert client.post("/tasks", json={"title": title}).status_code == 201
    assert client.get("/tasks/1").json()["title"] == titles[0]
    assert [t["title"] for t in client.get("/tasks?limit=1&offset=1").json()] == ["second"]
    assert len(client.get("/tasks").json()) == 3


def test_health_checks_storage_and_version(client):
    assert client.get("/health").json() == {"status": "ok", "version": "v0.1.0"}


def test_state_survives_new_application_instance(tmp_path):
    path = tmp_path / "tasks.db"
    with TestClient(create_app(path)) as first:
        first.post("/tasks", json={"title": "Persistent"})
        first.patch("/tasks/1", json={"completed": True})
    with TestClient(create_app(path)) as restarted:
        assert restarted.get("/tasks/1").json() == {
            "id": 1,
            "title": "Persistent",
            "completed": True,
        }


def test_incompatible_schema_prevents_startup(tmp_path):
    path = tmp_path / "tasks.db"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA user_version = 2")
    with pytest.raises(RuntimeError, match="Unsupported database schema"):
        with TestClient(create_app(path)):
            pass


def test_unavailable_storage_reports_503_without_path_leak(tmp_path):
    path = tmp_path / "tasks.db"
    with TestClient(create_app(path)) as session:
        path.unlink()
        path.mkdir()
        assert session.get("/health").status_code == 503
        assert session.get("/health").json() == {"detail": "Storage unavailable"}
