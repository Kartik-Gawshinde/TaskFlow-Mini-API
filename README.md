# TaskFlow Mini API

A beginner-friendly task-management REST API built with **Python**, **FastAPI**, **SQLite**, and **Docker Compose**.

## Features

- Create a task with a title, description, and status
- List all tasks or retrieve one task by ID
- Update a task's status
- Delete a task
- Health-check endpoint
- Input validation and useful HTTP error responses
- SQLite database stored in a Docker named volume so data persists when the container restarts

## Requirements

- Docker Desktop (with Docker Compose) for the containerized setup
- Or Python 3.10+ to run locally without Docker

## Run with Docker

From the project root, run:

```bash
docker compose up --build
```

Open:

- API base: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

Stop the application with `Ctrl+C`. To stop and remove the container while preserving the named database volume, run:

```bash
docker compose down
```

To also delete the stored database data, run:

```bash
docker compose down -v
```

## Run locally without Docker

Create and activate a virtual environment, then install dependencies.

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at http://localhost:8000. The SQLite database is created at `data/tasks.db`.

## API endpoints

| Method | Endpoint | Purpose | Success response |
|---|---|---|---|
| `GET` | `/api/health` | Check service health | `200 OK` |
| `POST` | `/api/tasks` | Create a task | `201 Created` |
| `GET` | `/api/tasks` | List all tasks | `200 OK` |
| `GET` | `/api/tasks/{id}` | Get a task by ID | `200 OK` |
| `PUT` | `/api/tasks/{id}` | Update task status | `200 OK` |
| `DELETE` | `/api/tasks/{id}` | Delete a task | `204 No Content` |

### Create a task

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker","description":"Containerize the TaskFlow API","status":"pending"}'
```

On Windows PowerShell, you can also use the Swagger UI at `/docs` to send requests.

Valid status values are exactly:

- `pending`
- `in-progress`
- `completed`

If `status` is omitted during creation, it defaults to `pending`. `description` defaults to an empty string.

### List tasks

```bash
curl "http://localhost:8000/api/tasks"
```

### Get one task

```bash
curl "http://localhost:8000/api/tasks/1"
```

### Update task status

```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

The PUT endpoint intentionally updates **status only**, as specified in the assignment.

### Delete a task

```bash
curl -i -X DELETE "http://localhost:8000/api/tasks/1"
```

A successful delete returns `204 No Content`.

## Validation and error handling

- `title` is required and must contain 1–200 characters; whitespace-only titles are rejected.
- `description` can contain up to 2,000 characters.
- `status` must be one of the three supported values.
- Task IDs must be positive integers.
- A task ID that does not exist returns `404 Not Found`.
- Invalid request bodies or invalid IDs return `422 Unprocessable Entity`.
- Successful creation returns `201 Created`; successful deletion returns `204 No Content`.

## Database schema

The `tasks` table contains:

| Column | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key, auto-increment |
| `title` | Text | Required |
| `description` | Text | Required; defaults to empty |
| `status` | Text | Restricted to supported statuses |
| `createdAt` | Text | UTC ISO-8601 timestamp |

## Project structure

```text
taskflow-mini-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Publish to GitHub

1. Create a new empty repository on GitHub.
2. Extract this ZIP and open a terminal in the `taskflow-mini-api` folder.
3. Run:

```bash
git init
git add .
git commit -m "Build TaskFlow Mini API"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the example repository URL with your own GitHub repository URL.
