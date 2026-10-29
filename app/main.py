from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Path as PathParam, Response, status
from pydantic import BaseModel, ConfigDict, Field

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: TaskStatus = TaskStatus.pending

    @classmethod
    def validate_title(cls, value):
        return value


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TaskStatus
    createdAt: datetime


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL CHECK(status IN ('pending', 'in-progress', 'completed')),
                createdAt TEXT NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="TaskFlow Mini API",
    description="A simple task-management REST API built with FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


def row_to_task(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "createdAt": row["createdAt"],
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "TaskFlow Mini API"}


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty or whitespace only.")

    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description, status, createdAt) VALUES (?, ?, ?, ?)",
            (title, payload.description, payload.status.value, created_at),
        )
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return row_to_task(row)


@app.get("/api/tasks", response_model=list[Task])
def get_tasks():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return [row_to_task(row) for row in rows]


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int = PathParam(..., ge=1)):
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    return row_to_task(row)


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task_status(payload: TaskStatusUpdate, task_id: int = PathParam(..., ge=1)):
    with get_connection() as connection:
        existing = connection.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
        connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (payload.status.value, task_id))
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return row_to_task(row)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int = PathParam(..., ge=1)):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
