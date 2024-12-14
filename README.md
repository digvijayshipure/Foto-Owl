# Library Management System

This is a backend implementation of a Library Management System using FastAPI, SQLAlchemy, and SQLite. The system supports features like user authentication, book borrowing requests, and admin controls for managing users and borrow requests.

# Features

- User Authentication: Users can register and log in using JWT tokens.
- Book Management: Admins can create, read, update, and delete books.
- Borrow Requests: Users can request to borrow books, and admins can approve or reject requests.
- User Roles: Admins can manage users and their borrow requests.

# Technologies

- Python: Backend logic and API development
- FastAPI: Web framework for building APIs
- SQLAlchemy: ORM for database interactions
- JWT: For user authentication
- SQLite: Database for storing users, books, and borrow requests
- Pydantic: For data validation and serialization
- Passlib: For password hashing

#Folder Structure
.
├── app
│ ├── **init**.py
│ ├── main.py # FastAPI app initialization
│ ├── models.py # Database models
│ ├── schemas.py # Pydantic models for request/response validation
│ ├── database.py # Database setup and session management
│ ├── crud.py # CRUD operations for interacting with the database
│ ├── auth.py # Authentication logic (JWT and password hashing)
│ ├── routers
│ │ ├── **init**.py # Initialize routers
│ │ ├── admin.py # Admin routes (user and borrow request management)
│ │ ├── user.py # User routes (book listing and borrow history)
├── migrations
│ ├── alembic.ini # Alembic configuration for schema migrations
│ └── ... # Alembic migration scripts
├── requirements.txt # Project dependencies
├── README.md # Project documentation

# Setup

## Prerequisites

Ensure you have Python 3.8+ installed. You also need a virtual environment for the project.

## install dependencies:

Install Python dependencies using pip: `pip install -r requirements.txt`

## Running the Application

- Run the application:
  Start the FastAPI application:uvicorn app.main:app

- Access the API:
  The app will be available at http://127.0.0.1:8000/docs.

# API Endpoints

## User Routes

- POST /token: Get an access token (login).
- GET /books: List all available books.
- POST /borrow_request: Create a borrow request for a book.
- GET /borrow_history: View borrow history.

## Admin Routes (Requires Admin Role)

- POST /create_user: Create a new user.
- GET /borrow_requests: View all borrow requests.
- POST /approve_request/{request_id}: Approve a borrow request.
- GET /user/{user_id}/borrow_history: View a user's borrow history.
