# tests/test_edge_cases.py
import json
import uuid
import pytest

# Note: This file relies on the fixtures (seeded_client, test_user) from conftest.py

# --- Registration Edge Cases ---

def test_register_user_with_missing_required_field_fails(seeded_client):
    """
    Test that user registration fails with a 400 error if a required field like 'name' is missing.
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    user_data = {
        "age": 30, "gender": "Female", "contact_info": "missing.name@example.com",
        "weight_kg": 70, "height_cm": 170, "fitness_goals": "lose weight",
        "workouts_per_week": "3", "workout_duration": 45, "sleep_hours": "7",
        "stress_level": "medium"
    }
    response = seeded_client.post('/api/auth/register', headers=headers, data=json.dumps(user_data))
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "Invalid input" in response.get_json()['error']

def test_register_user_with_invalid_data_type_fails(seeded_client):
    """
    Test that user registration fails with a 400 error if a field has the wrong data type (e.g., age as a string).
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    user_data = {
        "name": "Invalid Type User",
        "age": "twenty-five",
        "gender": "Male",
        "contact_info": "invalid.type@example.com",
        "weight_kg": 80, "height_cm": 180, "fitness_goals": "maintain",
        "workouts_per_week": "3", "workout_duration": 45, "sleep_hours": "7",
        "stress_level": "medium"
    }
    response = seeded_client.post('/api/auth/register', headers=headers, data=json.dumps(user_data))
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert "Invalid input" in response.get_json()['error']

def test_register_user_with_duplicate_name_fails(seeded_client):
    """
    Test that registration fails with a 409 Conflict error if a user with the same name already exists for this client.
    """
    user_to_duplicate_name = f"Duplicate Test User {str(uuid.uuid4())[:4]}"
    user_to_duplicate_email = f"duplicate.{str(uuid.uuid4())[:4]}@example.com"

    reg_headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    # FIX: Ensure the first user has all required fields to be created successfully.
    first_user_data = {
        "name": user_to_duplicate_name,
        "age": 40, "gender": "Other", "contact_info": user_to_duplicate_email,
        "weight_kg": 80, "height_cm": 180, "fitness_goals": "maintain",
        "workouts_per_week": "3", "workout_duration": 45, "sleep_hours": "7",
        "stress_level": "medium"
    }
    response1 = seeded_client.post('/api/auth/register', headers=reg_headers, data=json.dumps(first_user_data))
    assert response1.status_code == 201, f"Failed to create initial user for duplicate test: {response1.get_data(as_text=True)}"

    # Now, try to register a new user with the exact same name and all required fields
    duplicate_user_data = {
        "name": user_to_duplicate_name,
        "age": 41, "gender": "Other", "contact_info": "another.email@example.com",
        "weight_kg": 81, "height_cm": 181, "fitness_goals": "lose weight",
        "workouts_per_week": "4", "workout_duration": 60, "sleep_hours": "8",
        "stress_level": "low"
    }
    response2 = seeded_client.post('/api/auth/register', headers=reg_headers, data=json.dumps(duplicate_user_data))
    assert response2.status_code == 409

def test_register_user_with_invalid_email_format_fails(seeded_client):
    """Test registration fails if the contact_info is not a valid email format."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    user_data = {
        "name": "Bad Email", "contact_info": "not-an-email",
        "age": 25, "gender": "Male", "weight_kg": 75, "height_cm": 175,
        "fitness_goals": "build muscle", "workouts_per_week": "5",
        "workout_duration": 60, "sleep_hours": "8", "stress_level": "low"
    }
    response = seeded_client.post('/api/auth/register', headers=headers, data=json.dumps(user_data))
    assert response.status_code == 400
    assert "Invalid input" in response.get_json()['error']


# --- Logging Edge Cases ---

def test_log_diet_for_nonexistent_user_fails(seeded_client):
    """
    Test that logging a meal fails with a 404 error if the user_id does not exist.
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    meal_data = { "user_id": 99999, "meal_name": "Ghost Meal", "calories": 100 }
    response = seeded_client.post('/api/diet/log', headers=headers, data=json.dumps(meal_data))
    assert response.status_code == 404

def test_log_diet_with_logically_invalid_data_fails(seeded_client, test_user):
    """
    Test that logging a meal fails with a 400 error if data is logically invalid (e.g., negative calories).
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    meal_data = { "user_id": test_user, "meal_name": "Negative Calorie Meal", "calories": -200 }
    response = seeded_client.post('/api/diet/log', headers=headers, data=json.dumps(meal_data))
    assert response.status_code == 400
    assert "Invalid input" in response.get_json()['error']

def test_log_diet_with_empty_meal_name_fails(seeded_client, test_user):
    """Test logging a diet with an empty but required string field fails."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    meal_data = { "user_id": test_user, "meal_name": "", "calories": 150 }
    response = seeded_client.post('/api/diet/log', headers=headers, data=json.dumps(meal_data))
    assert response.status_code == 400

def test_log_workout_with_empty_exercises_fails(seeded_client, test_user):
    """
    Test that logging a workout fails with a 400 error if the exercises list is empty.
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    workout_data = { "user_id": test_user, "name": "Empty Workout", "exercises": [] }
    response = seeded_client.post('/api/workout/log', headers=headers, data=json.dumps(workout_data))
    assert response.status_code == 400
    assert "Invalid input" in response.get_json()['error']

def test_log_workout_with_invalid_nested_data_fails(seeded_client, test_user):
    """Test logging a workout where an exercise in the list is missing a required field."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    workout_data = {
        "user_id": test_user, "name": "Bad Exercise Workout",
        "exercises": [{"name": "Good Exercise", "sets": 3, "reps": 8, "weight": 100},
                      {"name": "Bad Exercise", "reps": 10, "weight": 50}] # Missing 'sets'
    }
    response = seeded_client.post('/api/workout/log', headers=headers, data=json.dumps(workout_data))
    assert response.status_code == 400

def test_log_weight_for_user_of_another_client_fails(seeded_client):
    """
    Simulates trying to log data for a user of another client by using a non-existent ID.
    The API should return 404 as it cannot find the user within its tenancy scope.
    """
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    weight_data = {"user_id": 99998, "weight_kg": 75}
    response = seeded_client.post('/api/progress/weight/log', headers=headers, data=json.dumps(weight_data))
    assert response.status_code == 404

def test_log_measurement_with_negative_value_fails(seeded_client, test_user):
    """Test logging a measurement with a logically invalid negative number."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    measurement_data = {"user_id": test_user, "waist_cm": -50}
    response = seeded_client.post('/api/progress/measurements/log', headers=headers, data=json.dumps(measurement_data))
    assert response.status_code == 400

# --- GET Request Edge Cases ---

def test_get_diet_history_for_nonexistent_user_fails(seeded_client):
    """Test that GETting diet history for a non-existent user returns 404."""
    headers = {'X-API-Key': seeded_client.api_key}
    response = seeded_client.get('/api/diet/99999/logs', headers=headers)
    assert response.status_code == 404

def test_get_workout_history_for_nonexistent_user_fails(seeded_client):
    """Test that GETting workout history for a non-existent user returns 404."""
    headers = {'X-API-Key': seeded_client.api_key}
    response = seeded_client.get('/api/workout/99999/history', headers=headers)
    assert response.status_code == 404

def test_get_weekly_report_for_nonexistent_user_fails(seeded_client):
    """Test that GETting a weekly report for a non-existent user returns 404."""
    headers = {'X-API-Key': seeded_client.api_key}
    response = seeded_client.get('/api/progress/99999/weekly-report', headers=headers)
    assert response.status_code == 404

# --- Plan Generation Edge Cases ---
def test_generate_diet_plan_for_nonexistent_user_fails(seeded_client):
    """Test generating a diet plan for a non-existent user returns 404."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    # FIX: Use the correct schema fields to pass Pydantic validation.
    plan_data = {
        "user_id": 99999,
        "activityLevel": "sedentary",
        "diet_type": "veg"
    }
    response = seeded_client.post('/api/diet/generate-plan', headers=headers, data=json.dumps(plan_data))
    assert response.status_code == 404

def test_generate_workout_plan_for_nonexistent_user_fails(seeded_client):
    """Test generating a workout plan for a non-existent user returns 404."""
    headers = {'Content-Type': 'application/json', 'X-API-Key': seeded_client.api_key}
    # FIX: Use the correct schema fields to pass Pydantic validation.
    plan_data = {
        "user_id": 99999,
        "fitnessLevel": "intermediate",
        "equipment": "Gym access"
    }
    response = seeded_client.post('/api/workout/generate-plan', headers=headers, data=json.dumps(plan_data))
    assert response.status_code == 404
