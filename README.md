# Catalog Management System

## Overview
This project is a rapid prototype of a catalog management system. It demonstrates a modular architecture with a **Python CLI frontend**, a **Java Spring Boot backend**, and a **CSV file as the database**. Users can view, add, edit, and delete catalog items through an interactive command-line interface.

---

## Requirements

### Backend (Java)
- Java 17+ (or compatible with Spring Boot 3.x)
- Maven (wrapper included: `./mvnw`)

### Frontend (Python)
- Python 3.8+
- pip
- requests library

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd CSCI-2040U-Software-Design-Labs
```

### 2. Start the Backend
```bash
cd backend
chmod +x mvnw
./mvnw spring-boot:run
# On Windows: mvnw.cmd spring-boot:run
```
The backend will start on [http://localhost:8080](http://localhost:8080)

### 3. Start the Frontend (CLI)
Open a **new terminal** window:
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python cli_app.py
```

---

## Usage

The CLI menu provides the following options:

```
==================================================
CATALOG MANAGEMENT SYSTEM
==================================================
1. View all items
2. View item details
3. Add new item
4. Edit item
5. Delete item
6. Exit
==================================================
```

### Features
- **View all items**: Display all catalog items in a formatted table
- **View item details**: Enter an item ID to see detailed information
- **Add new item**: Enter name and description to create new entries
- **Edit item**: Update existing items by ID with validation
- **Delete item**: Remove items from catalog with confirmation
- **Persistent storage**: All changes are automatically saved to `catalog.csv`

---

## System Architecture

```
┌─────────────────────┐      HTTP/REST      ┌─────────────────────┐
│  Python CLI         │ ◄─────────────────► │  Java Spring Boot   │
│  Frontend           │   localhost:8080    │  Backend API        │
│  (cli_app.py)       │                     │                     │
└─────────────────────┘                     └──────────┬──────────┘
                                                       │
                                                       │ Read/Write
                                                       ▼
                                               ┌───────────────┐
                                               │  catalog.csv  │
                                               │  (Database)   │
                                               └───────────────┘
```

---

## File Structure
```
.
├── catalog.csv              # CSV database file (ID, Name, Description)
├── README.md               # This file
├── backend/                # Java Spring Boot backend
│   ├── .mvn/wrapper/       # Maven wrapper config
│   ├── src/main/java/com/lab2/backend/
│   │   ├── BackendApplication.java     # Main Spring Boot app
│   │   ├── controller/
│   │   │   └── CatalogController.java  # REST API endpoints
│   │   ├── model/
│   │   │   └── CatalogItem.java        # Data model
│   │   └── service/
│   │       └── CatalogService.java     # Business logic & CSV operations
│   └── pom.xml             # Maven dependencies
└── frontend/               # Python CLI frontend
    ├── cli_app.py          # Command-line interface (MAIN)
    ├── app.py              # Web interface (optional)
    ├── requirements.txt    # Python dependencies
    └── templates/          # HTML templates (for optional web version)
        ├── base.html       # Base template with styling
        ├── index.html      # Home page - list all items
        ├── view_item.html  # View single item details
        ├── add_item.html   # Add new item form
        └── edit_item.html  # Edit item form
```

---

## API Endpoints

The backend provides RESTful API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/catalog` | Get all items |
| GET | `/api/catalog/{id}` | Get item by ID |
| POST | `/api/catalog` | Add new item |
| PUT | `/api/catalog/{id}` | Update item |
| DELETE | `/api/catalog/{id}` | Delete item |

---

## Lab Milestones Completed

[CHECKED] **Milestone 1**: Database Integration - CSV file reading and parsing  
[CHECKED] **Milestone 2**: Front-End Interaction - CLI menu system for viewing items  
[CHECKED] **Milestone 3**: Core Functionality - Add, Edit with input validation  
[CHECKED] **Milestone 4**: Saving Changes - Persist updates to CSV file  

---

## Input Validation

The system validates user inputs:
- [CHECKED] Item names cannot be empty
- [CHECKED] Item descriptions cannot be empty
- [CHECKED] Backend returns proper error messages for invalid input
- [CHECKED] CLI displays clear error/success messages

---

## Notes
- Both backend and CLI frontend must be running for full functionality
- The backend reads and writes to `catalog.csv` in the project root
- IDs are auto-incremented for new items
- All CRUD operations are immediately persisted to CSV file
- A web-based frontend (app.py) is also available as an alternative interface

---

## License
This project is for educational purposes (CSCI-2040U Software Design Labs).

