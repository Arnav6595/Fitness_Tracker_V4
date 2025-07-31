
  # app/api/auth_routes.py

from flask import Blueprint, request, jsonify, g
from app.models import db, User, Membership
from datetime import datetime
from pydantic import ValidationError
from app.schemas.user_schemas import UserRegistrationSchema
from app.utils.decorators import require_api_key
import logging

  # Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

  # Create a Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
@require_api_key
def register_user():
      """
      Endpoint to create a new user profile for the authenticated client.
      """
      raw_data = request.get_json()
      if not raw_data:
          return jsonify({"error": "Request body must be JSON."}), 400

      # Validate the incoming data using the Pydantic schema
      try:
          data = UserRegistrationSchema(**raw_data)
      except ValidationError as e:
          return jsonify({"error": "Invalid input", "details": e.errors()}), 400

      username = data.name.lower().replace(' ', '_')
      
      # Check if user already exists FOR THIS SPECIFIC CLIENT
      if User.query.filter_by(username=username, client_id=g.client.id).first():
          return jsonify({"error": f"User with name '{data.name}' already exists for this client."}), 409

      # Use the clean, validated data to create the database objects
      try:
          new_user = User(
              client_id=g.client.id,
              username=username,
              name=data.name,
              age=data.age,
              gender=data.gender,
              contact_info=data.contact_info,
              weight_kg=data.weight_kg,
              height_cm=data.height_cm,
              fitness_goals=data.fitness_goals,
              workouts_per_week=data.workouts_per_week,
              workout_duration=data.workout_duration,
              disliked_foods=data.disliked_foods,
              allergies=data.allergies,
              health_conditions=data.health_conditions,
              sleep_hours=data.sleep_hours,
              stress_level=data.stress_level
          )

          db.session.add(new_user)
          db.session.flush()  # Flush to generate new_user.id via the trigger
          logger.debug(f"Debug: new_user.id = {new_user.id}")  # Debug log

          if data.membership:
              new_membership = Membership(
                  client_id=g.client.id,
                  user_id=new_user.id,  # Use the generated user_id
                  plan=data.membership.plan,
                  start_date=datetime.now().date()  # Default start_date
              )
              db.session.add(new_membership)

          db.session.commit()

          return jsonify({
              "message": f"User '{new_user.name}' created successfully for client {g.client.company_name}!",
              "user_id": new_user.id
          }), 201

      except Exception as e:
          db.session.rollback()
          return jsonify({"error": "Failed to create user.", "details": str(e)}), 500
