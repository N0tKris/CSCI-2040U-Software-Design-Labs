# lab 2 Rapid Prototyping Architecture / Requirements

## 1. Project Structure

lab2_Rapid_Prototyping/
├── src/

│   ├── main.java

│   ├── logic.java

│   └── db.java

├── catalog.csv

└── architecture.md

## 2. Tools & Languages
Programming Language: Java
Database: CSV file (catalog.csv)
Version Control: Git / GitHub

## 3. Component Responsibilities
Main.java - Handles the CLI, shows the catalog, takes input, and calls the backend.
Logic.java - Handles adding, editing, and validating catalog items.
Database.java - Reads from and writes to the CSV, so data is saved between runs.

## 4. Component Interaction
CLI (main.java) → Logic (logic.java) → CSV (db.java)
- The CLI takes user input and sends it to Logic.
- Logic processes the request and uses the database to read/write the CSV.
- Results flow back to the CLI to show feedback.
