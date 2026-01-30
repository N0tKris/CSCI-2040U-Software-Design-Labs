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
- Maven (wrapper included)

### Frontend
- Python 3.8+
- requests library

### Data Storage
- CSV file (catalog.csv)

---

## Project Structure

```
catalog-prototype/
├── catalog.csv # CSV database file
├── README.md # Project documentation
├── docs/ # Architecture and design documentation
│ └── architecture.md
├── backend/ # Java Spring Boot backend
│ ├── .mvn/wrapper/
│ ├── src/main/java/
│ └── pom.xml
└── frontend/ # Python CLI frontend
├── cli_app.py
├── requirements.txt
└── templates/ # Optional web templates
```

---

## Component Responsibilities

### Python CLI Frontend
- Provides a menu-driven command-line interface
- Collects user input and displays results
- Sends HTTP requests to the backend API

### Java Backend (Spring Boot)
- Handles business logic and input validation
- Processes catalog operations (add, edit, delete, retrieve)
- Manages reading from and writing to the CSV file

### CSV Database
- Stores catalog data in a flat-file format
- Provides lightweight persistence suitable for rapid prototyping

---

## Component Interactions (System Architecture)

1. The user interacts with the system through the Python CLI.
2. The CLI sends HTTP requests to the Java backend.
3. The backend validates requests and performs catalog operations.
4. Catalog data is read from or written to the CSV file.
5. The backend returns responses to the CLI for display.

This layered architecture keeps responsibilities clearly separated and supports
rapid development and future extensibility.
