# PlateRate – Setup & Testing Instructions

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Java JDK | 17+ | Backend runtime |
| Python | 3.8+ | Frontend runtime |
| Maven | Included via wrapper | Backend build |
| PostgreSQL | 15 (Docker recommended) | Production database |
| Docker | Optional | Easy Postgres setup |
| Node.js / npm | Any LTS | Frontend Jest tests |

---

## Environment Variables

Create a `.env` file in the repository root before starting the system:

```
YELP_API_KEY=<your_yelp_api_key>
DB_URL=<postgres_connection_string>
```

> **Security note:** Never commit `.env` to version control. Rotate keys before sharing the repository or setting up CI pipelines. Use GitHub Secrets for CI/CD workflows.

---

## Running the Full System

### Windows (Recommended Quick Start)

```powershell
powershell -ExecutionPolicy Bypass -File .\run-system.ps1
```

Available flags:

| Flag | Effect |
|---|---|
| `-SkipInstall` | Skip Python dependency installation |
| `-UseDevProfile` | Use H2 in-memory database instead of PostgreSQL |
| `-NoBackend` | Start frontend only |
| `-NoFrontend` | Start backend only |

---

## Manual Setup (Step by Step)

### Step 1 – Start PostgreSQL

Using Docker:

```bash
docker run --name demo-postgres \
  -e POSTGRES_DB=restaurant_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgres:15
```

Check logs:

```bash
docker logs -f demo-postgres
```

Skip this step if using the dev (H2) profile.

### Step 2 – Start the Backend

```bash
cd backend
./mvnw spring-boot:run          # Linux/Mac
.\mvnw.cmd spring-boot:run      # Windows
```

To use the H2 dev profile instead:

```bash
# Linux/Mac
export SPRING_PROFILES_ACTIVE=dev
./mvnw spring-boot:run

# Windows PowerShell
$env:SPRING_PROFILES_ACTIVE="dev"
.\mvnw.cmd spring-boot:run
```

Verify the backend is running:

```bash
curl http://localhost:8080/api/catalog
# Expected: HTTP 200 and a JSON array
```

### Step 3 – Start the Frontend

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate           # Linux/Mac
.\.venv\Scripts\Activate.ps1        # Windows PowerShell

# Install dependencies
pip install -r frontend/requirements.txt

# Run frontend
python3 frontend/app.py
```

Open the URL shown in the terminal (default: `http://127.0.0.1:5000`).

---

## Default Seeded Credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |

Use these credentials for first login and to create additional accounts.

---

## Running Tests

### Backend Tests

```bash
cd backend
.\mvnw.cmd test          # Windows
./mvnw test              # Linux/Mac
```

The test suite uses an H2 in-memory database automatically via `application.properties` test config.

Existing test classes:

- `AuthControllerTest.java`
- `MenuItemControllerTest.java`
- `UserControllerTest.java`
- `RestaurantServiceTest.java`
- `ReviewServiceTest.java`

Feature-specific backend coverage includes:

- Menu item dietary tag normalization and update behavior (`MenuItemControllerTest.java`)
- Review moderation service behavior (`ReviewServiceTest.java`)

### Frontend Tests

```bash
cd frontend
npm install
npm test                   # Run tests once
npm run test:watch         # Watch mode
npm run test:coverage      # With coverage report
```

Test file: `filters.test.js`

Current frontend tests focus on filtering behavior, including menu-item dietary tag matching in user filtering.

---

## Manual Smoke Checks for Recent Features

1. Admin simulation modes
  - Log in as admin.
  - Enter **View As User**, then return to admin.
  - Enter **View as Owner**, register/update a restaurant, then return to admin.
2. User discovery updates
  - Use **Find Restaurants Near Me** and verify location status messaging.
  - Apply dietary filters and confirm matches can come from restaurant tags or menu item tags.
3. Owner menu metadata
  - Add/edit a menu item with dietary tags.
  - Confirm tags appear on owner dashboard and user restaurant detail views.

---

## Database Fix for OWNER Role Constraint

If you encounter a role constraint error with an existing database created before the OWNER role was added:

```sql
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));
```

---

## Project Structure Reference

```
.
├── backend/                 Java Spring Boot (Maven)
│   ├── src/main/java/...    Controllers, services, models, repositories
│   ├── src/main/resources/  application.properties, profiles
│   └── pom.xml
├── frontend/                Python Flask
│   ├── app.py               Flask app and proxy routes
│   ├── templates/           Jinja2 templates (user, owner, admin views)
│   └── requirements.txt
├── database/
│   └── schema.sql           Core table definitions
├── docs/                    Documentation (this directory)
├── catalog.csv              Optional CSV datastore
├── run-system.ps1           Windows quick-start script
└── README.md
```
