# Catalog Management System

## Overview

This repository contains a catalog management system used throughout
**CSCI 2040U – Software Design and Analysis** as a **shared codebase for all labs**.

The repository provides a consistent project structure and tooling that is reused
across multiple lab assignments. Each lab builds on the same foundation to
illustrate software design concepts such as separation of concerns,
client–server interaction, modularity, refactoring, and incremental development.

The system consists of:

* a Java Spring Boot backend exposing a REST API
* a Python Flask frontend that runs as a local web server
* a CSV file used as persistent storage

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

* Java 17+
* Spring Boot (3.x)
* Maven (wrapper included)

### Frontend

* Python 3.8+
* Flask
* requests

### Data Storage

* CSV file (catalog.csv)

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

* **Java 17 (JDK 17)** installed and available on PATH
* No separate Maven install required (Maven wrapper included)
* **Python 3.8+**
* VS Code or IntelliJ recommended

---

## Run Locally (Recommended)

### 1) Start the backend

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

### 2) Set up Python frontend

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r frontend/requirements.txt
```

---

### 3) Run the frontend web app

```bash
python3 frontend/app.py
```

Open the local URL shown in the terminal, typically:

```text
http://127.0.0.1:5000
```

---

## Data Handling

* The backend looks for `catalog.csv` in the following order:

  1. current working directory
  2. parent directory
  3. `backend/catalog.csv`

If no file is found, a new `catalog.csv` is created automatically with headers.

**Important:**
For predictable behavior, start the backend from the `backend/` directory.

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
