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
├── backend/        # Java Spring Boot backend (REST API)
├── frontend/       # Python Flask frontend (local web server)
├── catalog.csv     # Persistent datastore (CSV)
└── README.md
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
