# PlateRate — Restaurant Review Demo

## Overview

This repository contains a small Restaurant Review demo (PlateRate) used for
local development and teaching in **CSCI 2040U – Software Design and Analysis**.

The repository provides a consistent project structure and tooling that is reused
across multiple lab assignments. Each lab builds on the same foundation to
illustrate software design concepts such as separation of concerns,
client–server interaction, modularity, refactoring, and incremental development.

The system consists of:

- a Java Spring Boot backend exposing a REST API
- a Python Flask frontend that runs as a local web server
- a PostgreSQL database (or an in-memory fallback for some demo data)

---

## Project Structure

```
.
├── backend/                # Java Spring Boot backend (Maven)
│   ├── src/main/java/...   # Java sources: controller, service, model, repository
│   ├── src/main/resources  # application.properties, profiles
│   └── pom.xml             # Maven project descriptor (use ./mvnw or mvnw.cmd)
├── frontend/               # Python Flask frontend
│   ├── app.py              # Flask app + inline templates
  │   ├── templates/       # Jinja2 templates (user, owner, admin views)
│   └── requirements.txt    # Python dependencies for frontend (venv)
├── database/               # DB schema and SQL helpers
│   └── schema.sql
├── catalog.csv             # Optional CSV datastore used by some labs
└── README.md               # This file (Windows-specific notes included below)
```

---

## Tech Stack

### Backend

- Java 17+
- Spring Boot (3.x)
- Maven (wrapper included)

### Frontend

- Python 3.8+
- Flask and requests

### Data Storage

- PostgreSQL (recommended for full demo)

---

## Purpose (Course Context)

This repository serves as a **shared codebase for all labs** in **CSCI 2040U – Software Design and Analysis**.

The structure, tooling, and core architecture remain consistent across labs. Individual labs may:

* add new features
* refactor existing components
* introduce testing or design improvements
* modify the frontend or backend behavior

**Lab 2** uses this repository as an initial rapid prototyping exercise. Later labs build directly on the same structure rather than starting from scratch.

---

## API

**Base URL:**

```
http://localhost:8080/api/catalog
```

The backend handles:

* CSV reads/writes
* Basic validation
* CRUD operations on catalog items

---

## Prerequisites

- **Java 17 (JDK 17)** installed and available on PATH
- No separate Maven install required (Maven wrapper included)
- **Python 3.8+**
- **Docker** (recommended for running a local Postgres instance)

Windows users: the commands below assume PowerShell (not WSL/bash). PowerShell handles line-continuation and quoting differently; examples below include PowerShell-friendly forms.

Recommended: use the included Maven wrapper (`./mvnw`) and a Python virtualenv for the frontend.

---

## Run Locally (Recommended)

### 1) Start Postgres (recommended)

Run a local Postgres container (only if you don't already have Postgres running):

```bash
docker run --name demo-postgres \
  -e POSTGRES_DB=restaurant_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgres:15
```

Wait until Postgres is ready (use `docker logs -f demo-postgres`).

### 2) Start the backend

From the repository root:

```bash
cd backend
./mvnw spring-boot:run
```

Verify it’s running:

```bash
curl http://localhost:8080/api/catalog
```

Expected: HTTP 200 and a JSON array (possibly empty).

---

### 3) Set up Python frontend

From the repository root (create and activate a virtualenv first):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

Windows PowerShell notes
- To create and activate a venv in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r frontend/requirements.txt
```

- To run the backend on Windows use the Maven wrapper Windows script:

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

- Docker on PowerShell: use a single-line `docker run` or PowerShell backtick (`) for continuation. Example (single-line recommended):

```powershell
docker rm -f demo-postgres 2>$null; docker run --name demo-postgres -e POSTGRES_DB=restaurant_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
```

Or multi-line with PowerShell continuation (no trailing spaces after backtick):

```powershell
docker rm -f demo-postgres 2>$null
docker run --name demo-postgres `
  -e POSTGRES_DB=restaurant_db `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  -d postgres:15
```

- To open a psql session inside the running container (preferred):

```powershell
docker exec -it demo-postgres psql -U postgres -d restaurant_db
```

If you instead `docker exec -it demo-postgres bash` you'll be in a shell; run `psql -U postgres -d restaurant_db` there. Remember that `\c` and `\d` are psql metacommands and only work inside `psql`, not in bash.

Database constraint fix (OWNER role)
- If owner self-registration fails with an error like:

```
ERROR: new row for relation "users" violates check constraint "users_role_check"
Detail: Failing row contains (..., OWNER, ...)
```

run these SQL commands inside `psql` connected to `restaurant_db` to allow `OWNER` as a role:

```sql
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));
```

You can execute them directly from PowerShell using `docker exec`:

```powershell
docker exec -it demo-postgres psql -U postgres -d restaurant_db -c "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;"
docker exec -it demo-postgres psql -U postgres -d restaurant_db -c "ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));"
```

---

### 4) Run the frontend web app

```bash
python3 frontend/app.py
```

Open the local URL shown in the terminal, typically:

```text
http://127.0.0.1:5000
```

---

## Seeded credentials

On first run the backend seeds a default admin account if one does not exist:

- Username: `admin`
- Password: `admin123`

Use these credentials to log in from the frontend and perform admin actions (creating restaurants).

## Notes

- The frontend proxies auth and API calls to the backend and expects the backend at `http://localhost:8080` by default. You can change this with the `BACKEND_BASE_URL` environment variable in `frontend/app.py`.
- Java dependencies are managed via Maven (`backend/pom.xml`).
- Python dependencies are listed in `requirements.txt` at the repo root (install with `pip install -r requirements.txt`).

Recent repo changes (quick summary)
- Yelp Fusion integration: an admin endpoint and backend `YelpService` were added to import restaurants from the Yelp Fusion API. Set `YELP_API_KEY` in your `.env` or environment and use the admin import UI.
- Owner registration DB issue: some environments had a PostgreSQL CHECK constraint that disallowed the `OWNER` role — see the Database constraint fix above.
- Frontend text changes: three landing-page buttons had their emoji icons removed and em-dashes replaced with hyphens across frontend templates to improve cross-platform rendering. If you prefer the original icons, revert the first block in `frontend/templates/landing.html` where the `.brand` and the three buttons are defined.

Windows-specific troubleshooting tips
- If PowerShell complains about running scripts when activating the venv, run PowerShell as Administrator and set the execution policy for the current user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- If `psql` is not available on your host, use `docker exec` to run it inside the container as shown above.
- If ports are in use, stop other services or change the `spring.datasource.url` and `-p` mapping when launching Postgres.

---

## Troubleshooting

* **Cannot connect to backend**

  * Ensure Spring Boot is running
  * Ensure port `8080` is free
* **Python dependency errors**

  * Activate the virtual environment
  * Re-run `pip install -r frontend/requirements.txt`
* **Java errors**

  * Confirm `java -version` reports Java 17

---

## Development Notes

* Java dependencies are managed via Maven (`backend/pom.xml`)
* Python dependencies are listed in `frontend/requirements.txt`
* Do **not** add a `requirements.txt` for Java
* Update Python deps with:

  ```bash
  pip freeze > frontend/requirements.txt
  ```

---
