from flask import Blueprint, request, jsonify, g
from app.models import db, User, WeightEntry, MeasurementLog
from app.services.reporting_service import ReportingService
from datetime import datetime
from pydantic import ValidationError
from app.schemas.progress_schemas import WeightLogSchema, MeasurementLogSchema
from app.utils.decorators import require_api_key # 1. IMPORT THE DECORATOR

progress_bp = Blueprint('progress_bp', __name__)

@progress_bp.route('/<int:user_id>/weekly-report', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_weekly_report(user_id):
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    try:
        # Note: The ReportingService might also need to be made client-aware
        reporting_service = ReportingService(user_id)
        report = reporting_service.get_weekly_report()
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate report", "details": str(e)}), 500

@progress_bp.route('/weight/log', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def log_weight():
    raw_data = request.get_json()
    try:
        data = WeightLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )

    try:
        user.weight_kg = data.weight_kg
        new_entry = WeightEntry(
            client_id=g.client.id,
            user_id=user.id,  #<-- Use user_id directly
            weight_kg=data.weight_kg
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Weight logged successfully!", "entry": new_entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log weight.", "details": str(e)}), 500

@progress_bp.route('/measurements/log', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def log_measurements():
    raw_data = request.get_json()
    try:
        data = MeasurementLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    
    try:
        new_log = MeasurementLog(
            client_id=g.client.id, # 4. ASSOCIATE LOG WITH THE CLIENT
            author=user,
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


@progress_bp.route('/<int:user_id>/weight', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_weight_history(user_id):
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    # 4. ENSURE WE ONLY QUERY LOGS FOR THIS CLIENT
    history = WeightEntry.query.filter_by(user_id=user.id, client_id=g.client.id).order_by(WeightEntry.date.asc()).all()
    return jsonify([entry.to_dict() for entry in history]), 200