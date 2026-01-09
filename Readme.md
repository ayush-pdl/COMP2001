# COMP2001 CW2 – Profile Service API

## Overview
This repository contains my **COMP2001 Coursework 2** implementation: a RESTful **Profile Service API** built using **Python**, **Flask**, and **Connexion**, backed by a **SQL Server** database and fully **containerised using Docker**.

All database operations are performed **entirely in Python** via stored procedures, in line with the coursework requirements.  
The service supports **user management**, **role retrieval**, and **authentication verification** using the COMP2001 Authenticator API.

---

## Technologies Used
- Python 3.11
- Flask
- Connexion (OpenAPI-first REST API)
- pyodbc (SQL Server connectivity)
- Docker & Docker Desktop
- Microsoft ODBC Driver 17 for SQL Server
- OpenAPI / Swagger UI

---

## Project Structure
COMP2001_CW2_API/
│
├── controllers/
│ ├── init.py
│ └── users_controller.py
│
├── app.py
├── db.py
├── auth_client.py
├── swagger.yml
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env
├── .env.docker
└── README.md


---

## API Features
- Health check endpoint
- List all users
- Create a new user
- Retrieve user by ID
- Retrieve user by email
- Update user details
- Delete user (Admin-only)
- List all roles
- Retrieve roles for a user (assigned automatically if missing)
- External authentication via COMP2001 Authenticator

---

## Running the Application (Docker – Required)

### Prerequisites
- Docker & Docker Desktop installed and running.
- The database schema must already exist (provided by the module).
- A .env.docker file containing the required DB credentials (not committed to Git).

### 1. Build the Docker image
From the project root:
```bash
docker build -t comp2001-cw2-api .
```

### 2. Run the container
```bash
docker run --rm -p 5000:5000 --env-file .env.docker comp2001-cw2-api
```

### Accessing the API
- API base: http://127.0.0.1:5000/api  
- Swagger UI: http://127.0.0.1:5000/api/ui

### Environment variables
Database credentials are supplied via Docker (.env.docker). Required variables:
- DB_SERVER
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_DRIVER

These are used at runtime from the .env.docker file.

### Authentication
- Authentication is verified using the COMP2001 Authenticator API:
    https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users
- Protected operations (for example, deleting a user) require these headers on the request:
    - X-Auth-Email
    - X-Auth-Password
    - X-Actor-UserId
- Authentication is validated server-side by the service (requests library).

### Admin-only operations
- Deleting a user requires the acting user to have the Admin role.
- If a user has no role assigned, a role is automatically assigned (allowed by the coursework brief).

### Testing
Endpoints were exercised using:
- Swagger UI
- PowerShell (Invoke-RestMethod)
- curl

Screenshots of the OpenAPI documentation, each API operation, and authentication tests are included in the coursework report.

### Notes on the database
- No SQL is written inside the API routes.
- All database operations are executed via stored procedures.

### Author
Ayush Paudel  
BSc (Hons) Computer Science
