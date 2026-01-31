# Catalog Management System

## Overview
This project is a rapid prototype of a catalog management system developed for  
CSCI 2040U – Software Design and Analysis (Lab 2: Rapid Prototyping).

The objective of this project is to demonstrate core software design principles
by building a functional system within a limited timeframe. The system emphasizes
clear separation between the front end, back end, and data storage.

Users can view, add, edit, and delete catalog items through a command-line
interface, with all data persisted in a CSV file.

---

## Tech Stack

### Backend
- Java 17+
- Spring Boot (3.x compatible)
- Maven (wrapper included) (Intellij recommended because it comes pre-installed)

### Frontend
- Python 3.8+
- requests library

### Data Storage
- CSV file (catalog.csv)

---

# Catalog Management System

## Overview
This repository contains a small catalog management prototype used for
CSCI-2040U rapid prototyping exercises. It consists of:

- a Java Spring Boot backend (under `backend/`) that exposes a simple REST API
- a Python frontend (under `frontend/`) with a CLI (`cli_app.py`) and a
	Tkinter GUI (`gui3.py`)
- a CSV file at the repo root (`catalog.csv`) used as the persistent datastore

The frontend interacts with the backend via HTTP. The backend handles CSV
reads/writes and basic validation.

**API base:** http://localhost:8080/api/catalog

---

**Prerequisites**

- Java 17 (JDK 17) installed for the backend. Set `JAVA_HOME` to your JDK 17
	installation if required.
- No separate Maven install required: the project includes the Maven wrapper
	(`./mvnw`). If you prefer system Maven, `mvn` works too.
- Python 3.8+ for the frontend. A virtual environment is recommended.
- On Debian/Ubuntu systems, the GUI may require the `python3-tk` package.
 - Visual Studio Code (VS Code) recommended as the editor/IDE for this
	 project (extensions: Java, Spring Boot, Python).

---

## Step-by-step: Run locally (recommended)

Follow these exact steps in separate terminals (or use the commands below in order):

1) Start the backend (terminal A):

```bash
# from repo root
cd backend
./mvnw spring-boot:run
```

2) Verify the backend is ready (terminal A or new terminal):

```bash
# simple HTTP check
curl -sS http://localhost:8080/api/catalog || echo "backend not ready"
```

Expected: a JSON array (possibly empty) or an HTTP 200 response.

3) Prepare Python environment (terminal B):

```bash
# from repo root
python3 -m venv venv
source venv/bin/activate
pip install -r frontend/requirements.txt
```

4) Run the CLI frontend (terminal B):

```bash
python3 frontend/cli_app.py
```

Or run the GUI frontend:

```bash
python3 frontend/gui3.py
```

Notes & tips:

- If the CLI prints "Cannot connect to backend", ensure step (1) completed
	and that port `8080` is not blocked by another process.
- To run both backend and CLI in one command, I can add a `run-dev.sh` script or
	a `Makefile` target — tell me if you want me to create that file.
- To change the backend the frontends call, edit the top-level `BACKEND_URL`
	variable in `frontend/cli_app.py` and `URL` in `frontend/gui3.py`.
- On Linux, if the GUI fails to start, install `python3-tk` (Debian/Ubuntu):

```bash
sudo apt-get install python3-tk
```

---

## Quickstart — Backend (Java / Spring Boot)

From the repository root:

1. Start the backend (uses the included Maven wrapper):

```bash
cd backend
./mvnw spring-boot:run
```

This starts the Spring Boot app on port `8080` by default.

Run backend tests with:

```bash
./mvnw test
```

Notes:
- The backend uses Java 17 (see `backend/pom.xml`). You do not need a
	`requirements.txt` for the backend because Maven manages dependencies.

---

## Quickstart — Frontend (Python)

There are two frontend options included:

- CLI: `frontend/cli_app.py` — lightweight, terminal-driven
- GUI: `frontend/gui3.py` — Tkinter-based desktop GUI

Recommended steps (from repository root):

```bash
# create a virtual environment
python3 -m venv venv
source venv/bin/activate

# install Python dependencies
pip install -r frontend/requirements.txt
```

Run the CLI frontend:

```bash
python3 frontend/cli_app.py
```

Run the GUI frontend:

```bash
python3 frontend/gui3.py
```

If the GUI fails to start on Linux, install the system Tk bindings (Debian/Ubuntu):

```bash
sudo apt-get install python3-tk
```

The frontends expect the backend to be running at `http://localhost:8080`.
If you run the backend on a different host/port, edit the `BACKEND_URL` in
`frontend/cli_app.py` and the `URL` in `frontend/gui3.py`.

---

## Data

- The CSV datastore is `backend/catalog.csv` by default. The backend service
	will look for a `catalog.csv` file in these locations (in order):
	1. the current working directory where the JVM was started (`./catalog.csv`)
	2. the parent directory (`../catalog.csv`)
	3. `backend/catalog.csv`

	If no file is found the service creates a new `catalog.csv` in the JVM's
	working directory with a header row. To ensure consistent behavior, run
	the backend from the `backend/` directory (see Quickstart above).

---


---

## Troubleshooting

- "Cannot connect to backend": make sure the backend is running and accessible
	on port `8080`.
- If a Python dependency is missing, activate the virtualenv and run
	`pip install -r frontend/requirements.txt`.
- For Java build or runtime issues, ensure you have JDK 17 installed and that
	`java -version` reports a 17.x runtime.

---

## Development notes

- Backend dependencies are managed by Maven (`backend/pom.xml`). Do not add a
	`requirements.txt` for the Java backend — Maven already handles dependency
	resolution.
- The frontend's `requirements.txt` includes third-party packages used by the
	Python code (e.g., `requests`). Update it after adding new Python packages
	with `pip freeze > frontend/requirements.txt`.

---

## Contact / Next steps

If you'd like, I can:

- add a small shell script to start both backend and CLI frontend together,
- update `frontend/requirements.txt` to remove unused Flask entries (the
	current file mentions Flask but the provided frontends use `requests` and
	Tkinter), or
- create a `Makefile` with common commands (`make run-backend`, `make run-cli`).

Tell me which of these you'd like and I'll implement it.
