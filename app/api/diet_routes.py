# app/api/diet_routes.py
from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, User, DietLog, DietPlan 
from app.services.diet_planner import DietPlannerService
from app.services.reporting_service import ReportingService
import google.generativeai as genai
from datetime import datetime
from pydantic import ValidationError
from app.schemas.diet_schemas import DietLogSchema, GenerateDietPlanSchema
# --- MODIFIED: Import require_jwt ---
from app.utils.decorators import require_api_key, require_jwt

# Create a Blueprint for diet routes
diet_bp = Blueprint('diet_bp', __name__)

# This route remains unchanged as it's a B2B client action
@diet_bp.route('/generate-plan', methods=['POST'])
@require_api_key
def generate_diet_plan():
    raw_data = request.get_json()
    try:
        data = GenerateDietPlanSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    
    try:
        gemini_api_key = current_app.config.get('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured in .env file.")
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        return jsonify({"error": "API Key configuration error", "details": str(e)}), 500

    planner = DietPlannerService(user=user, form_data=data.dict())
    result = planner.generate_plan()

    if result.get("success"):
        new_plan = DietPlan(
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
@diet_bp.route('/log', methods=['POST'])
@require_jwt
def log_meal():
    raw_data = request.get_json()
    try:
        # Note: Ensure user_id is removed from DietLogSchema
        data = DietLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    
    try:
        macros = data.macros.model_dump() if data.macros else {}
        new_log = DietLog(
            # Use the authenticated user's info from the JWT
            client_id=g.current_user.client_id,
            user_id=g.current_user.id,
            meal_name=data.meal_name,
            food_items=data.food_items,
            calories=data.calories,
            protein_g=macros.get('protein_g'),
            carbs_g=macros.get('carbs_g'),
            fat_g=macros.get('fat_g')
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Meal logged successfully!", "log": new_log.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log meal.", "details": str(e)}), 500

# --- MODIFIED: Route changed to fetch current user's data ---
@diet_bp.route('/logs/me', methods=['GET'])
@require_jwt
def get_my_diet_logs():
    logs = DietLog.query.filter_by(user_id=g.current_user.id).order_by(DietLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

# --- MODIFIED: Route changed to fetch current user's data ---
@diet_bp.route('/plan/latest/me', methods=['GET'])
@require_jwt
def get_my_latest_diet_plan():
    latest_plan = DietPlan.query.filter_by(
        user_id=g.current_user.id
    ).order_by(DietPlan.created_at.desc()).first()

    if not latest_plan:
        return jsonify({"error": "No diet plan found for this user."}), 404

    full_plan_object = latest_plan.generated_plan
    jumbled_weekly_plan = full_plan_object.get('weekly_plan', {})
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    try:
        sorted_plan_items = sorted(
            jumbled_weekly_plan.items(), 
            key=lambda item: day_order.index(item[0])
        )
    except (ValueError, AttributeError, TypeError):
        return jsonify({"error": "Could not sort the diet plan due to unexpected format."}), 500

    formatted_plan = [{"day": day, "meals": meals} for day, meals in sorted_plan_items]
    return jsonify(formatted_plan), 200

# --- MODIFIED: Route changed to fetch current user's data ---
@diet_bp.route('/weekly-summary/me', methods=['GET'])
@require_jwt
def get_my_diet_summary():
    try:
        reporter = ReportingService(g.current_user.id)
        summary = reporter.get_weekly_diet_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate diet summary", "details": str(e)}), 500