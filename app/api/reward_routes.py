# app/api/reward_routes.py
from flask import Blueprint, jsonify, g
from app.models import User, Achievement
from app.services.reward_service import RewardService
from app.utils.decorators import require_api_key # 1. IMPORT THE DECORATOR

reward_bp = Blueprint('reward_bp', __name__)

@reward_bp.route('/<int:user_id>/status', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_reward_status(user_id):
    """
    Checks for new rewards and returns all achievements for a user,
    ensuring the user belongs to the authenticated client.
    """
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )

    try:
        # Note: The RewardService might also need to be made client-aware
        reward_service = RewardService(user.id)
        newly_unlocked = reward_service.check_and_grant_rewards()
        
        # 4. ENSURE WE ONLY QUERY ACHIEVEMENTS FOR THIS CLIENT'S USER
        all_achievements = Achievement.query.filter_by(user_id=user.id, client_id=g.client.id).order_by(Achievement.unlocked_at.desc()).all()

        return jsonify({
            "newly_unlocked_rewards": newly_unlocked,
            "all_achievements": [ach.to_dict() for ach in all_achievements]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to check rewards", "details": str(e)}), 500