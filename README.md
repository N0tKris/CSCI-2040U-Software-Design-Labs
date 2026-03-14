# PlateRate - Restaurant Review Demo

## Overview

This repository contains PlateRate, a simple Restaurant Review demo used for local development and in CSCI 2040U – Software Design and Analysis.

It demonstrates core software design concepts like modularity, separation of concerns, client-server interaction, and incremental development. Each lab builds on this base so you can focus on features rather than starting from scratch.

The system includes:

* Backend: Java Spring Boot exposing a REST API
* Frontend: Python Flask running a local web server
* Database: PostgreSQL (or in-memory fallback for demo data)

## Project Structure

```
.
├── backend/                # Java Spring Boot backend (Maven)
│   ├── src/main/java/...   # Java sources: controller, service, model, repository
│   ├── src/main/resources  # application.properties, profiles
│   └── pom.xml             # Maven project descriptor
├── frontend/               # Python Flask frontend
│   ├── app.py              # Flask app + templates
│   ├── templates/          # Jinja2 templates for user, owner, admin views
│   └── requirements.txt    # Python dependencies
├── database/               # DB schema and SQL helpers
│   └── schema.sql
├── catalog.csv             # Optional CSV datastore
└── README.md               # This file
```

## Tech Stack

Backend: Java 17+, Spring Boot 3.x, Maven wrapper included

Frontend: Python 3.8+, Flask, requests

Database: PostgreSQL recommended

## Purpose

This repo is a starting point for labs in CSCI 2040U. You can:

* Add features
* Refactor code
* Add tests or design improvements
* Modify frontend or backend behaviour

Lab 2 uses this repo for rapid prototyping. Later labs continue using this foundation.

## API

Base URL:

```
http://localhost:8080/api/catalog
```

Handles:

* CRUD on catalog items
* CSV read/write
* Basic validation

## Prerequisites

* Java 17 (JDK 17)
* Python 3.8+
* Docker (optional, for Postgres)
* Maven wrapper included

Use a Python virtual environment for the frontend. Windows users: PowerShell examples are included.

## Running Locally

### 1) Start Postgres (optional)

```
docker run --name demo-postgres \
  -e POSTGRES_DB=restaurant_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgres:15
```

Check logs:

```
docker logs -f demo-postgres
```

### 2) Start the backend

```
cd backend
./mvnw spring-boot:run
```

Verify:

```
curl http://localhost:8080/api/catalog
```

Expected: HTTP 200 and JSON array.

### 3) Setup frontend

```
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r frontend/requirements.txt
```

Run frontend:

```
python3 frontend/app.py
```

Open the URL shown in the terminal (usually [http://127.0.0.1:5000](http://127.0.0.1:5000)).

### Windows Notes

* Activate virtualenv in PowerShell:

```
.\.venv\Scripts\Activate.ps1
```

* Run Maven backend:

```
cd backend
.\mvnw.cmd spring-boot:run
```

* Fix OWNER role DB constraint:

```
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));
```

## Seeded Credentials

* Username: admin
* Password: admin123

Use to log in as admin and create restaurants.

## Notes

* Frontend proxies API requests to [http://localhost:8080](http://localhost:8080) by default
* Java dependencies managed with Maven
* Python dependencies in frontend/requirements.txt
* Yelp integration requires YELP_API_KEY in .env

## Troubleshooting

* Backend not reachable: Ensure Spring Boot is running and port 8080 is free
* Python errors: Activate venv and reinstall dependencies
* Java errors: Confirm java -version shows 17

## Development Notes

* Java: backend/pom.xml
* Python: frontend/requirements.txt
* Update Python dependencies:

```
pip freeze > frontend/requirements.txt
```
