# app/api/auth_routes.py

from flask import Blueprint, request, jsonify, g, current_app
from app.models import db, User, Membership, TokenBlocklist, RefreshToken
from datetime import datetime, timedelta, timezone
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
        try:
            # 1. Create short-lived access token
            access_token_id = uuid.uuid4().hex
            access_token = jwt.encode({
                'user_id': user.id,
                'client_id': g.client.id,
                'exp': datetime.now(timezone.utc) + timedelta(minutes=15),  # Short-lived token
                'jti': access_token_id,
                'type': 'access'
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            # 2. Create long-lived refresh token
            refresh_token_id = uuid.uuid4().hex
            refresh_token_expiry = datetime.now(timezone.utc) + timedelta(days=30)
            refresh_token = jwt.encode({
                'user_id': user.id,
                'client_id': g.client.id,
                'exp': refresh_token_expiry,
                'jti': refresh_token_id,
                'type': 'refresh'
            }, current_app.config['SECRET_KEY'], algorithm="HS256")
            
            # 3. Store the refresh token in the database
            new_refresh_token = RefreshToken(
                user_id=user.id,
                token=refresh_token,
                expiry_date=refresh_token_expiry
            )
            db.session.add(new_refresh_token)
            db.session.commit()

            # 4. Return both tokens
            return jsonify({
                "message": "Login successful!",
                "access_token": access_token,
                "refresh_token": refresh_token
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to issue tokens: {str(e)}")
            return jsonify({"error": "Failed to issue tokens.", "details": str(e)}), 500

    return jsonify({"error": "Invalid email or password."}), 401


# --- NEW REFRESH ENDPOINT ---
@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Endpoint to get a new access token using a refresh token.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header is missing or invalid."}), 401

    token = auth_header.split(' ')[1]

    try:
        # Decode the refresh token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

        # Verify it's a refresh token
        if payload.get('type') != 'refresh':
            return jsonify({"error": "Invalid token type."}), 401

        # Check if the refresh token exists in the database and is still valid
        refresh_token_entry = RefreshToken.query.filter_by(token=token).first()
        # CORRECTED THIS LINE
        if not refresh_token_entry or refresh_token_entry.expiry_date < datetime.now(timezone.utc):
            return jsonify({"error": "Refresh token is invalid or expired."}), 401

        # Issue a new access token
        new_access_token_id = uuid.uuid4().hex
        new_access_token = jwt.encode({
            'user_id': payload['user_id'],
            'client_id': payload['client_id'],
            # CORRECTED THIS LINE
            'exp': datetime.now(timezone.utc) + timedelta(minutes=15),
            'jti': new_access_token_id,
            'type': 'access'
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"access_token": new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token."}), 401
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        return jsonify({"error": "Failed to refresh token.", "details": str(e)}), 500


# --- UPDATED LOGOUT ENDPOINT ---
@auth_bp.route('/logout', methods=['POST'])
@require_jwt
def logout_user():
    """
    Endpoint to log out a user by blocklisting their access token 
    and deleting their refresh token.
    """
    try:
        # The decorator has already decoded the token and put it in g.decoded_token
        decoded_token = g.decoded_token
        
        # Add the access token's unique ID to the blocklist
        jti = decoded_token['jti']
        blocklisted_token = TokenBlocklist(jti=jti)
        db.session.add(blocklisted_token)
        
        # Delete the user's refresh token from the database
        user_id = decoded_token['user_id']
        RefreshToken.query.filter_by(user_id=user_id).delete()
        
        # Commit both changes to the database
        db.session.commit()
        
        return jsonify({"message": "Successfully logged out."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to logout.", "details": str(e)}), 500