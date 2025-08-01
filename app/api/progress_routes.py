from flask import Blueprint, request, jsonify, g
from app.models import db, User, WeightEntry, MeasurementLog
from app.services.reporting_service import ReportingService
from datetime import datetime
from pydantic import ValidationError
from app.schemas.progress_schemas import WeightLogSchema, MeasurementLogSchema
# --- MODIFIED: Import require_jwt ---
from app.utils.decorators import require_api_key, require_jwt

progress_bp = Blueprint('progress_bp', __name__)

# --- MODIFIED: Route changed to fetch current user's data ---
@progress_bp.route('/weekly-report/me', methods=['GET'])
@require_jwt
def get_my_weekly_report():
    try:
        # Use the authenticated user's ID
        reporting_service = ReportingService(g.current_user.id)
        report = reporting_service.get_weekly_report()
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate report", "details": str(e)}), 500

# --- MODIFIED: This route is now protected by JWT ---
@progress_bp.route('/weight/log', methods=['POST'])
@require_jwt
def log_weight():
    raw_data = request.get_json()
    try:
        # Note: user_id is removed from WeightLogSchema
        data = WeightLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    try:
        # Use the authenticated user's info from the JWT
        g.current_user.weight_kg = data.weight_kg
        new_entry = WeightEntry(
            client_id=g.current_user.client_id,
            user_id=g.current_user.id,
            weight_kg=data.weight_kg
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Weight logged successfully!", "entry": new_entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log weight.", "details": str(e)}), 500

# --- MODIFIED: This route is now protected by JWT ---
@progress_bp.route('/measurements/log', methods=['POST'])
@require_jwt
def log_measurements():
    raw_data = request.get_json()
    try:
        # Note: user_id is removed from MeasurementLogSchema
        data = MeasurementLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    
    try:
        new_log = MeasurementLog(
            # Use the authenticated user's info from the JWT
            client_id=g.current_user.client_id,
            author=g.current_user,
            waist_cm=data.waist_cm,
            chest_cm=data.chest_cm,
            arms_cm=data.arms_cm,
            hips_cm=data.hips_cm
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Measurements logged successfully!", "log": new_log.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log measurements.", "details": str(e)}), 500

# --- MODIFIED: Route changed to fetch current user's data ---
@progress_bp.route('/weight/me', methods=['GET'])
@require_jwt
def get_my_weight_history():
    history = WeightEntry.query.filter_by(user_id=g.current_user.id).order_by(WeightEntry.date.asc()).all()
    return jsonify([entry.to_dict() for entry in history]), 200