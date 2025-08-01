Fitness Tracker - B2B SaaS Platform
This document provides a comprehensive overview of the Fitness Tracker project, its architecture, setup, and development roadmap. The project has been refactored from a standard single-user application into a robust, multi-tenant B2B platform ready for commercial deployment.

1. Project Evolution: From App to Platform
This project underwent a significant architectural overhaul to transition from a consumer-facing application to a commercial, API-first service for business clients.

The Original Version (Legacy)
The initial application was a monolithic service designed for individual users. It lacked the security, separation, and scalability required to serve multiple business clients.

The Refactored B2B Version (Current)
The current platform is a multi-tenant, API-driven service. The core logic has been re-engineered to securely isolate data for each business client (tenant). Functionality is exposed through a secure, well-documented API that now supports both client-level and end-user authentication, making it a true B2B2C platform.

2. Core Architectural Changes
The foundation of the new platform rests on these critical changes:

Multi-Tenancy: The database schema and all application logic have been refactored to be tenant-aware. A client_id is now a fundamental part of the data model, ensuring that one client can never access another client's data.

Two-Layered Authentication: The platform now uses a robust, two-tiered authentication system:

Client-Level (B2B): Every request to the API must include a valid X-API-Key header. This key identifies the business client (e.g., a gym).

End-User-Level (B2C): For user-specific actions (like logging a workout), a JSON Web Token (JWT) must be passed in the Authorization: Bearer <token> header. This securely authenticates the end-user.

Containerization with Docker: The entire application is containerized using Docker and managed with Docker Compose. This guarantees a consistent environment, simplifies deployment, and enhances scalability.

Automated Testing & CI/CD: A comprehensive test suite using Pytest ensures code quality. This is integrated into a GitHub Actions CI/CD pipeline that automatically runs all tests on every code push.

3. Getting Started: Local Development Setup
Follow these steps to get the project running on your local machine.

Prerequisites
Git

Python 3.10+

Docker & Docker Compose

Installation
Clone the Repository

git clone https://github.com/Arnav6595/Fitness_Tracker.git
cd Fitness_Tracker

Create and Activate a Virtual Environment

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Configure Environment Variables
Create a .env file in the project root. This file is ignored by Git and holds your secrets.

# .env
DATABASE_URL="postgresql://user:password@db:5432/yourdbname"
SECRET_KEY="a-very-strong-and-secret-key-for-jwt"
GEMINI_API_KEY="your-google-gemini-api-key"
FLASK_ENV="development"

Set Up the Database
Run the database migrations to create all the necessary tables.

flask db upgrade

4. How to Run the Application
A. Running with Docker Compose (Recommended Method)
This method uses docker-compose.yml to build and run the application and its database in containers, mirroring a production environment.

Start the Application
This command builds the images if they don't exist and starts the containers in the background.

docker-compose up --build -d

Stop the Application
This command stops and removes the containers and network.

docker-compose down

The application will be available at http://127.0.0.1:5000.

B. Running Locally (for Quick Development)
To run the application with the Flask development server without Docker:

python run.py

5. Testing
The project uses Pytest for all testing. Tests are located in the tests/ directory. To run the complete test suite:

pytest

6. API Usage & Documentation
Authentication
All API endpoints require authentication.

Client-level endpoints (e.g., plan generation) require a valid X-API-Key.

User-specific endpoints (e.g., logging a workout, getting history) require both a valid X-API-Key and a user's Authorization: Bearer <token> header.

Documentation
The API documentation is generated using Swagger/OpenAPI and is available live once the application is running.


7. Project Roadmap
This project is being developed in phases.

✅ Phase 1: Foundational Refactoring

Implemented a testing framework with Pytest.

Refactored the database and services for multi-tenancy.

Built the B2B API key authentication system.

Implemented End-User JWT Authentication.

Generated public API documentation with Swagger/OpenAPI.

➡️ Phase 2: DevOps and Client Enablement

Containerized the application with Docker and Docker Compose.

Set up a basic CI/CD pipeline with GitHub Actions.

⏳ Phase 3: Production Readiness & Monetization

Implement rate limiting to prevent API abuse.

Integrate a centralized logging service (e.g., Sentry).

Deploy to a cloud provider (AWS, Google Cloud, etc.).

Integrate a billing provider like Stripe for subscriptions.

⏳ Phase 4: Scaling and Management

Formalize API versioning in all routes.

Build an internal admin dashboard for client onboarding and management.
```
Directory Tree
Fitness-Tracker/
|
|____ .github/
| |____ workflows/
| | |____ ci.yml
|
|____ app/
| |____ api/
| | |____ auth_routes.py
| | |____ diet_routes.py
| | |____ progress_routes.py
| | |____ reward_routes.py
| | |____ user_routes.py
| | |____ workout_routes.py
| |____ services/
| | |____ adaptive_planner_service.py
| | |____ diet_planner.py
| | |____ reporting_service.py
| | |____ reward_service.py
| | |____ workout_planner_service.py
| |____ schemas/
| | |____ diet_schemas.py
| | |____ progress_schemas.py
| | |____ user_schemas.py
| | |____ workout_schemas.py
| |____ static/
| | |____ swagger.yaml
| |____ utils/
| | |____ decorators.py
| |____ __init__.py
| |____ models.py
|
|____ migrations/
| |____ versions/
| | |____ ... (migration scripts)
| |____ alembic.ini
| |____ env.py
| |____ README
| |____ script.py.mako
|
|____ tests/
| |____ test_integration.py
| |____ test_edge_cases.py
| |____ conftest.py
|
|____ .env (Ignored by Git)
|____ .gitignore
|____ config.py
|____ Dockerfile
|____ docker-compose.yml
|____ entrypoint.sh
|____ pytest.ini
|____ README.md
|____ requirements.txt
|____ run.py
```
