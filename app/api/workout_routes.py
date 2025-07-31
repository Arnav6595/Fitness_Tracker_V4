from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, User, WorkoutLog, ExerciseEntry, WorkoutPlan
from app.services.workout_planner_service import WorkoutPlannerService
import google.generativeai as genai
from datetime import datetime
from pydantic import ValidationError
from app.schemas.workout_schemas import GenerateWorkoutPlanSchema, WorkoutLogSchema
from app.utils.decorators import require_api_key # 1. IMPORT THE DECORATOR

workout_bp = Blueprint('workout_bp', __name__)

@workout_bp.route('/generate-plan', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def generate_workout_plan():
    raw_data = request.get_json()
    try:
        data = GenerateWorkoutPlanSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    
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
            client_id=g.client.id, # 4. ASSOCIATE PLAN WITH THE CLIENT
            author=user, 
            generated_plan=result['plan']
        )
        db.session.add(new_plan)
        db.session.commit()
        return jsonify(result['plan']), 200
    else:
        return jsonify({"error": result.get("error")}), 500


@workout_bp.route('/log', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def log_workout():
    raw_data = request.get_json()
    try:
        data = WorkoutLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )

    try:
        new_workout_log = WorkoutLog(
            client_id=g.client.id,
            user_id=user.id,  #<-- Use user_id directly
            name=data.name
        )
        db.session.add(new_workout_log)
        db.session.flush() # <-- SOLUTION IMPLEMENTED HERE

        for ex_data in data.exercises:
            exercise_entry = ExerciseEntry(
                client_id=g.client.id, # 4. ASSOCIATE EXERCISE WITH THE CLIENT
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


@workout_bp.route('/<int:user_id>/history', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_workout_history(user_id):
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    # 4. ENSURE WE ONLY QUERY LOGS FOR THIS CLIENT
    logs = WorkoutLog.query.filter_by(user_id=user.id, client_id=g.client.id).order_by(WorkoutLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200