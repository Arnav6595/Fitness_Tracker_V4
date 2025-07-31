# tests/test_integration.py

import json
import uuid

# The create_test_user helper function has been removed.
# We now use the 'test_user' fixture from conftest.py for tests that need a pre-existing user.

# --- Auth Routes Tests ---
def test_register_endpoint_fails_without_key(client):
    """Test that registration fails without an API key."""
    headers = {'Content-Type': 'application/json'}
    data = {"name": "Fail User", "contact_info": "fail@example.com"}
    response = client.post('/api/auth/register', headers=headers, data=json.dumps(data))
    assert response.status_code == 401

def test_register_endpoint_succeeds_with_valid_key(seeded_client):
    """Test that a new, unique user can be registered successfully."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Registration Test User {unique_id}",
        "age": 30, "gender": "Female",
        "contact_info": f"reg.test.{unique_id}@example.com",
        "weight_kg": 70, "height_cm": 170,
        "fitness_goals": "Get stronger", "workouts_per_week": "3",
        "workout_duration": 60, "sleep_hours": "8", "stress_level": "low"
    }
    response = seeded_client.post('/api/auth/register', headers=headers, data=json.dumps(user_data))
    assert response.status_code == 201, f"Registration failed: {response.get_data(as_text=True)}"

# --- Diet Routes Tests ---
def test_diet_log_fails_without_key(client):
    """Test that logging a meal fails without an API key."""
    headers = {'Content-Type': 'application/json'}
    data = {"user_id": 1, "meal_name": "Breakfast"}
    response = client.post('/api/diet/log', headers=headers, data=json.dumps(data))
    assert response.status_code == 401

def test_diet_log_succeeds_with_key(seeded_client, test_user):
    """Test that logging a meal for our session user succeeds."""
    user_id = test_user
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    meal_data = {
        "user_id": user_id, "meal_name": "Test Lunch", "food_items": "Salad",
        "calories": 350, "macros": {"protein_g": 20, "carbs_g": 15, "fat_g": 25}
    }
    response = seeded_client.post('/api/diet/log', headers=headers, data=json.dumps(meal_data))

    # Print the server's response to the console for debugging
    print(f"Response data: {response.get_data(as_text=True)}")

    assert response.status_code == 201
    assert "Meal logged successfully" in response.get_json()['message']

# --- Workout Routes Tests ---
def test_workout_log_fails_without_key(client):
    """Test that logging a workout fails without an API key."""
    headers = {'Content-Type': 'application/json'}
    data = {"user_id": 1, "name": "Morning Run"}
    response = client.post('/api/workout/log', headers=headers, data=json.dumps(data))
    assert response.status_code == 401

def test_workout_log_succeeds_with_key(seeded_client, test_user):
    """Test that logging a workout for our session user succeeds."""
    user_id = test_user
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    workout_data = {
        "user_id": user_id, "name": "Chest Day",
        "exercises": [{"name": "Bench Press", "sets": 3, "reps": 8, "weight": 100}]
    }
    response = seeded_client.post('/api/workout/log', headers=headers, data=json.dumps(workout_data))
    assert response.status_code == 201
    assert "Workout logged successfully" in response.get_json()['message']

# --- Progress Routes Tests ---
def test_progress_log_fails_without_key(client):
    """Test that logging weight fails without an API key."""
    headers = {'Content-Type': 'application/json'}
    data = {"user_id": 1, "weight_kg": 80}
    response = client.post('/api/progress/weight/log', headers=headers, data=json.dumps(data))
    assert response.status_code == 401

def test_progress_log_succeeds_with_key(seeded_client, test_user):
    """Test that logging weight for our session user succeeds."""
    user_id = test_user
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    weight_data = {"user_id": user_id, "weight_kg": 79.5}
    response = seeded_client.post('/api/progress/weight/log', headers=headers, data=json.dumps(weight_data))
    assert response.status_code == 201
    assert "Weight logged successfully" in response.get_json()['message']

# --- Reward Routes Tests ---
def test_reward_status_fails_without_key(client):
    """Test that getting reward status fails without an API key."""
    response = client.get('/api/reward/1/status')
    assert response.status_code == 401

def test_reward_status_succeeds_with_key(seeded_client, test_user):
    """Test that getting reward status for our session user succeeds."""
    user_id = test_user
    headers = {'X-API-Key': seeded_client.api_key}
    response = seeded_client.get(f'/api/reward/{user_id}/status', headers=headers)
    assert response.status_code == 200
    assert "all_achievements" in response.get_json()