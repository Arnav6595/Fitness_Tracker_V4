# app/api/reward_routes.py
from flask import Blueprint, jsonify, g
from app.models import User, Achievement
from app.services.reward_service import RewardService
# --- MODIFIED: Import require_jwt ---
from app.utils.decorators import require_api_key, require_jwt

reward_bp = Blueprint('reward_bp', __name__)

# --- MODIFIED: Route changed to fetch current user's data ---
@reward_bp.route('/status/me', methods=['GET'])
@require_jwt
def get_my_reward_status():
    """
    Checks for new rewards and returns all achievements for the authenticated user.
    """
    try:
        # Use the authenticated user's ID
        reward_service = RewardService(g.current_user.id)
        newly_unlocked = reward_service.check_and_grant_rewards()
        
        all_achievements = Achievement.query.filter_by(user_id=g.current_user.id).order_by(Achievement.unlocked_at.desc()).all()

        return jsonify({
            "newly_unlocked_rewards": newly_unlocked,
            "all_achievements": [ach.to_dict() for ach in all_achievements]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to check rewards", "details": str(e)}), 500