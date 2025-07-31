# tests/conftest.py

import pytest
import json
import uuid
from app import create_app
from app.models import db, Client

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the entire test session."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        # Ensure exceptions are propagated and debug mode is on
        'PROPAGATE_EXCEPTIONS': True,
        'DEBUG': True
    })

    with app.app_context():
        db.create_all()
        yield app
        # The session is removed and tables are dropped at the end of the test session.
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    """A standard, unseeded test client for the app."""
    return app.test_client()

@pytest.fixture(scope="session")
def seeded_client(app):
    """
    An API-key-authenticated test client.
    This is session-scoped, so the B2B Client is created only once.
    """
    with app.app_context():
        # Find or create the B2B client company.
        test_client_instance = Client.query.filter_by(company_name="Test Fitness Corp").first()
        if not test_client_instance:
            test_client_instance = Client(company_name="Test Fitness Corp")
            db.session.add(test_client_instance)
            db.session.commit()

        # Get a test client from the app and attach the API key to it.
        api_client = app.test_client()
        api_client.api_key = test_client_instance.api_key
        return api_client

@pytest.fixture(scope="function")
def test_user(seeded_client):
    """
    Creates a new, unique end-user for EACH test function.
    This ensures that tests are completely isolated from each other.
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    unique_id = str(uuid.uuid4())[:8] # Ensures user is unique for each test run.
    user_data = {
        "name": f"Test User {unique_id}",
        "age": 28, "gender": "Male",
        "contact_info": f"test.user.{unique_id}@example.com",
        "weight_kg": 80, "height_cm": 182,
        "fitness_goals": "Build muscle", "workouts_per_week": "4",
        "workout_duration": 60, "sleep_hours": "8", "stress_level": "low"
    }
    response = seeded_client.post('/api/auth/register', headers=headers, data=json.dumps(user_data))
    
    # Ensure the user was actually created before the test runs.
    assert response.status_code == 201, f"Failed to create test user: {response.get_data(as_text=True)}"
    
    return response.get_json()['user_id']