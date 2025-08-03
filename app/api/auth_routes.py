# app/api/auth_routes.py

from flask import Blueprint, request, jsonify, g, current_app
from app.models import db, User, Membership, TokenBlocklist
from datetime import datetime, timedelta
from pydantic import ValidationError
from app.schemas.user_schemas import UserRegistrationSchema, UserLoginSchema
from app.utils.decorators import require_api_key, require_jwt
import logging
import jwt
import uuid # Import uuid for generating token IDs

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
    Now includes password handling.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # Validate the incoming data using the Pydantic schema
    try:
        data = UserRegistrationSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # Check if user already exists FOR THIS SPECIFIC CLIENT by email
    if User.query.filter_by(email=data.email, client_id=g.client.id).first():
        return jsonify({"error": f"User with email '{data.email}' already exists for this client."}), 409

    # Use the clean, validated data to create the database objects
    try:
        username = data.name.lower().replace(' ', '_')  # Create a simple username

        new_user = User(
            client_id=g.client.id,
            username=username,
            email=data.email,  # Use the new email field
            name=data.name,
            age=data.age,
            gender=data.gender,
            phone_number=data.phone_number,
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
        # Set the password using the new method from the User model
        new_user.set_password(data.password)

        db.session.add(new_user)
        db.session.flush()  # Flush to get the new_user.id
        logger.debug(f"Debug: new_user.id after flush = {new_user.id}")

        if data.membership:
            new_membership = Membership(
                client_id=g.client.id,
                user_id=new_user.id,
                plan=data.membership.plan,
                start_date=datetime.now().date()
            )
            db.session.add(new_membership)

        db.session.commit()

        return jsonify({
            "message": f"User '{new_user.name}' created successfully for client {g.client.company_name}!",
            "user_id": new_user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create user: {str(e)}")
        return jsonify({"error": "Failed to create user.", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@require_api_key
def login_user():
    """
    Endpoint to authenticate a user and return a JWT token.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({"error": "Request body must be JSON."}), 400

    try:
        data = UserLoginSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # Find the user by email for the specific client
    user = User.query.filter_by(email=data.email, client_id=g.client.id).first()

    # Check if the user exists and the password is correct
    if user and user.check_password(data.password):
        # Create the JWT token with a unique ID (jti)
        token_id = uuid.uuid4().hex
        token = jwt.encode({
            'user_id': user.id,
            'client_id': g.client.id,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expiration time
            'jti': token_id, # Add the unique token identifier
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "message": "Login successful!",
            "token": token
        })

    return jsonify({"error": "Invalid email or password."}), 401


# --- NEW LOGOUT ENDPOINT ---
@auth_bp.route('/logout', methods=['POST'])
@require_jwt
def logout_user():
    """
    Endpoint to log out a user by blocklisting their token.
    """
    try:
        # The decorator has already decoded the token and put it in g.decoded_token
        jti = g.decoded_token['jti']
        
        # Add the token's unique ID to the blocklist
        blocklisted_token = TokenBlocklist(jti=jti)
        db.session.add(blocklisted_token)
        db.session.commit()
        
        return jsonify({"message": "Successfully logged out."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to logout.", "details": str(e)}), 500
