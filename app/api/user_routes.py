# app/api/user_routes.py

from flask import Blueprint, jsonify, g, request
from app.utils.decorators import require_jwt
from app.models import db
from app.schemas.user_schemas import UserProfileUpdateSchema
from pydantic import ValidationError

# Create a new Blueprint
user_bp = Blueprint('user_bp', __name__)

@user_bp.route("/profile/me", methods=['GET'])
@require_jwt # This decorator protects the route
def get_my_profile():
    """Fetches the complete profile for the authenticated user."""
    user = g.current_user
    # Now uses the consistent to_dict() method from the User model
    return jsonify(user.to_dict()), 200


@user_bp.route("/profile/me", methods=['PUT'])
@require_jwt # Protect the route so only a logged-in user can update their own profile
def update_my_profile():
    """
    Endpoint for a user to update their own profile details.
    """
    user = g.current_user
    raw_data = request.get_json()

    if not raw_data:
        return jsonify({"error": "Request body must be JSON."}), 400

    try:
        # Validate the incoming data using our new update schema
        data = UserProfileUpdateSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    try:
        # Update user fields only if they were provided in the request.
        for field, value in data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        db.session.commit()
        
        # Return the updated user profile using the consistent to_dict() method
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile.", "details": str(e)}), 500