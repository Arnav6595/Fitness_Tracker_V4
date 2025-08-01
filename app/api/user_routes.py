# app/api/user_routes.py

from flask import Blueprint, jsonify, g
from app.utils.decorators import require_jwt

# Create a new Blueprint
user_bp = Blueprint('user_bp', __name__)

@user_bp.route("/profile/me", methods=['GET'])
@require_jwt # This decorator protects the route
def get_my_profile():
    # Because of the decorator, g.current_user is available with the logged-in user's data
    user = g.current_user

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "fitness_goals": user.fitness_goals
    })