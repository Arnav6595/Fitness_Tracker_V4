Fitness Tracker - B2B SaaS Platform
This document provides a comprehensive overview of the Fitness Tracker project, its architecture, setup, and development roadmap. The project has been refactored from a standard single-user application into a robust, multi-tenant B2B platform ready for commercial deployment.

1. Project Evolution: From App to Platform
This project underwent a significant architectural overhaul to transition from a consumer-facing application to a commercial, API-first service for business clients.

The Original Version (Legacy)
The initial application was a monolithic service designed for individual users. It lacked the security, separation, and scalability required to serve multiple business clients.

The Refactored B2B Version (Current)
The current platform is a multi-tenant, API-driven service. The core logic has been re-engineered to securely isolate data for each business client (tenant) and expose functionality through a secure, well-documented API. This new architecture is built for scalability, reliability, and monetization.

2. Core Architectural Changes
The foundation of the new platform rests on these critical changes:

Multi-Tenancy: The database schema and all application logic have been refactored to be tenant-aware. A client_id is now a fundamental part of the data model, ensuring that one client can never access another client's data.

B2B API Key Authentication: A robust authentication layer was implemented. Every request to the API must include a valid X-API-Key header. This key identifies the client, authenticates their request, and scopes all subsequent operations to their specific data.

Containerization with Docker: The entire application is containerized using Docker. This guarantees a consistent environment from local development to production, simplifies deployment, and enhances scalability.

Automated Testing & CI/CD: A comprehensive test suite using Pytest ensures code quality and prevents regressions. This is integrated into a GitHub Actions CI/CD pipeline that automatically runs all tests on every code push, enforcing quality control.

3. Getting Started: Local Development Setup
Follow these steps to get the project running on your local machine.

Prerequisites
Git

Python 3.10+

Docker & Docker Compose

Installation
Clone the Repository

git clone [https://github.com/Arnav6595/Fitness_Tracker.git](https://github.com/Arnav6595/Fitness_Tracker.git)
cd your-repository

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
Create a .env file in the project root. This file is ignored by Git and holds your secrets. You can copy the example file if one exists.

# .env
DATABASE_URL="postgresql://user:password@localhost/fitnessdb"
SECRET_KEY="a-very-secret-key"
FLASK_ENV="development"

Set Up the Database
Run the database migrations to create all the necessary tables.

flask db upgrade

4. How to Run the Application
A. Running Locally (for Development)
To run the application with the Flask development server:

python run.py

The application will be available at http://127.0.0.1:5000.

B. Running with Docker (Production-like)
This method uses the Dockerfile to build and run the application in a container, which is how it would be deployed in production.

Build the Docker Image

docker build -t fitness-tracker .

Run the Docker Container
This command starts the container, maps port 5000, and passes the environment variables from your .env file.

docker run -p 5000:5000 --env-file .env fitness-tracker

5. Testing
The project uses Pytest for all testing. Tests are located in the tests/ directory.

To run the complete test suite:

pytest

6. API Usage & Documentation
Authentication
All API endpoints require a valid API key to be passed in the X-API-Key request header. Unauthorized or invalid requests will be rejected.

Documentation & Versioning
Documentation: Public API documentation will be generated using Swagger/OpenAPI to provide a clear guide for client developers.

Versioning: All API routes will be versioned (e.g., /api/v1/...) to ensure that future updates do not break existing client integrations.

7. Project Roadmap
This project is being developed in phases.

✅ Phase 1: Foundational Refactoring

Implemented a testing framework with Pytest.

Refactored the database and services for multi-tenancy.

Built the B2B API key authentication system.

➡️ Phase 2: DevOps and Client Enablement

Containerized the application with Docker.

Set up a basic CI/CD pipeline with GitHub Actions.

Next Up: Generate public API documentation (Swagger/OpenAPI).

⏳ Phase 3: Production Readiness & Monetization

Implement rate limiting to prevent API abuse.

Integrate a centralized logging service (e.g., Sentry).

Deploy to a cloud provider (AWS, Google Cloud, etc.).

Integrate a billing provider like Stripe for subscriptions.

⏳ Phase 4: Scaling and Management

Formalize API versioning in all routes.

Build an internal admin dashboard for client onboarding and management.


Directory tree

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
| | |____ ... (other route files)
| |____ services/
| | |____ adaptive_planner_service.py
| | |____ ... (other service files)
| |____ schemas/
| | |____ user_schemas.py
| | |____ ... (other schema files)
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
|____ venv/ (Ignored by Git)
|
|____ .dockerignore
|____ .env (Ignored by Git, contains secrets)
|____ .gitignore
|____ config.py
|____ Dockerfile
|____ entrypoint.sh
|____ pytest.ini
|____ README.md
|____ requirements.txt
|____ run.py