from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, User, WorkoutLog, ExerciseEntry, WorkoutPlan
from app.services.workout_planner_service import WorkoutPlannerService
import google.generativeai as genai
from datetime import datetime
from pydantic import ValidationError
from app.schemas.workout_schemas import GenerateWorkoutPlanSchema, WorkoutLogSchema
# --- MODIFIED: Import require_jwt ---
from app.utils.decorators import require_api_key, require_jwt

workout_bp = Blueprint('workout_bp', __name__)

# This route remains unchanged as it's a B2B client action
@workout_bp.route('/generate-plan', methods=['POST'])
@require_api_key
@require_jwt
def generate_workout_plan():
    raw_data = request.get_json()
    try:
        data = GenerateWorkoutPlanSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    user = g.current_user
    
    try:
        gemini_api_key = current_app.config.get('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        return jsonify({"error": "API Key configuration error", "details": str(e)}), 500

    planner = WorkoutPlannerService(user=user, form_data=data.dict())
    result = planner.generate_plan()

    if result.get("success"):
        new_plan = WorkoutPlan(
            client_id=g.client.id,
            author=user, 
            generated_plan=result['plan']
        )
        db.session.add(new_plan)
        db.session.commit()
        return jsonify(result['plan']), 200
    else:
        return jsonify({"error": result.get("error")}), 500

# --- MODIFIED: This route is now protected by JWT ---
@workout_bp.route('/log', methods=['POST'])
@require_jwt
def log_workout():
    raw_data = request.get_json()
    try:
        # Note: Ensure user_id is removed from WorkoutLogSchema
        data = WorkoutLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    try:
        new_workout_log = WorkoutLog(
            # Use the authenticated user's info from the JWT
            client_id=g.current_user.client_id,
            user_id=g.current_user.id,
            name=data.name
        )
        db.session.add(new_workout_log)
        db.session.flush()

        for ex_data in data.exercises:
            exercise_entry = ExerciseEntry(
                client_id=g.current_user.client_id,
                name=ex_data.name,
                sets=ex_data.sets,
                reps=ex_data.reps,
                weight=ex_data.weight,
                workout_log=new_workout_log
            )
            db.session.add(exercise_entry)

        db.session.commit()
        return jsonify({
            "message": "Workout logged successfully!",
            "workout": new_workout_log.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log workout.", "details": str(e)}), 500

# --- MODIFIED: Route changed to fetch current user's data ---
@workout_bp.route('/history/me', methods=['GET'])
@require_jwt
def get_my_workout_history():
    logs = WorkoutLog.query.filter_by(user_id=g.current_user.id).order_by(WorkoutLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

# --- NEW ROUTE TO FETCH THE LATEST WORKOUT PLAN ---
@workout_bp.route('/plan/latest/me', methods=['GET'])
@require_jwt
def get_my_latest_workout_plan():
    """
    Fetches the most recent workout plan for the authenticated user.
    """
    try:
        # Query the database for the latest plan created for the current user,
        # ordered by creation date.
        latest_plan = WorkoutPlan.query.filter_by(
            user_id=g.current_user.id
        ).order_by(WorkoutPlan.created_at.desc()).first()

        # If no plan is found for the user, return a 404 error.
        if not latest_plan:
            return jsonify({"error": "No workout plan found for this user."}), 404

        # If a plan is found, convert it to a dictionary and return it.
        return jsonify(latest_plan.to_dict()), 200

    except Exception as e:
        # Handle any other unexpected errors.
        return jsonify({"error": "An error occurred while retrieving the workout plan.", "details": str(e)}), 500