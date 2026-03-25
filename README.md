# User Management API

A professional, production-ready RESTful API built with Flask for managing users with JWT authentication. Designed for scalability, security, and a clean project structure.

## Features
- **RESTful Endpoints**: Standardized CRUD operations for user management.
- **JWT Authentication**: Secure login and protected routes using JSON Web Tokens.
- **Centralized Error Handling**: Standardized responses for all API errors.
- **Logging**: Integrated logging for requests, errors, and database operations.
- **Health Check**: Endpoint to monitor API status.
- **Dockerized**: Optimized for production deployment using Gunicorn.
- **Clean Architecture**: Disconnected layers (Controller, Service, Repository, Model).

## Tech Stack
- **Backend**: Flask
- **Database**: SQLAlchemy (SQLite for dev, easily switchable to PostgreSQL)
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: PyJWT
- **Server**: Gunicorn
- **Deployment**: Docker, CI/CD ready

## Folder Structure
```text
app/
├── controllers/          # Request handlers
├── services/             # Business logic
├── repository/           # Data access layer
├── models/               # SQLAlchemy models
├── routes/               # API endpoint definitions
├── utils/                # Auth, Error handling, and helper utilities
└── database/             # Database configuration
run.py                    # Application entry point
Dockerfile                # Production Docker setup
requirements.txt          # Python dependencies
```

## API Endpoints

### Authentication
- `POST /auth/login` - Authenticate and get tokens.
- `POST /auth/refresh` - Refresh access token using a refresh token.
- `POST /auth/logout` - Revoke current refresh token.

### User Management
- `GET /users` - List all users (Admin only, support paging/filtering).
- `GET /users/<id>` - Get user details (Self or Admin).
- `POST /users` - Register a new user.
- `PUT /users/<id>` - Update user data (Self or Admin).
- `DELETE /users/<id>` - Delete a user (Admin only).
- `PUT /users/<id>/promote` - Promote a user to Admin (Admin only).

### System
- `GET /health` - Check API health status.
- `GET /` - Welcome message.

## Setup Instructions

### Local Environment
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```

### Using Docker
1. Build the image:
   ```bash
   docker build -t user-management-api .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 user-management-api
   ```

## Standard Response Format
All API responses follow this structure:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```
