# app/services/reward_service.py
from app.models import User, Achievement, db
from app.services.reporting_service import ReportingService
from flask import abort

class RewardService:
    def __init__(self, user_id):
        # CHANGE 1: Use db.session.get() and handle the 'not found' case.
        self.user = db.session.get(User, user_id)
        if not self.user:
            abort(404, description="User not found.")
        self.reporting_service = ReportingService(user_id)

    def check_and_grant_rewards(self):
        """
        Main method to check all possible rewards, grant them,
        and then commit all changes at once.
        """
        newly_unlocked = []
        
        # Check for each potential reward
        if self._check_for_cheat_meal():
            newly_unlocked.append("Cheat Meal Unlocked")

        if self._check_weight_loss_milestone():
            newly_unlocked.append("5% Weight Loss Milestone")
            
        # If any new achievements were added to the session, commit them now.
        if newly_unlocked:
            db.session.commit()

        return newly_unlocked

    def _check_for_cheat_meal(self, required_score=90.0):
        """
        Checks for and ADDS (but does not commit) the cheat meal achievement.
        """
        # Check if this achievement already exists in the database
        if Achievement.query.filter_by(user_id=self.user.id, name="Cheat Meal Unlocked").first():
            return False # Already has this reward, do nothing.

        adherence_score = self.reporting_service.get_diet_adherence_score(days=7)
        
        if adherence_score >= required_score:
            # CHANGE 2: Add client_id and use user_id for consistency.
            achievement = Achievement(
                client_id=self.user.client_id,
                user_id=self.user.id,
                name="Cheat Meal Unlocked",
                description=f"Unlocked for maintaining a {adherence_score}% diet adherence for 7 days."
            )
            db.session.add(achievement) # Add to session, but don't commit yet
            return True # Signal that a new reward was added
        return False

    def _check_weight_loss_milestone(self, percentage_goal=5.0):
        """
        Checks for and ADDS (but does not commit) the weight loss milestone.
        """
        if Achievement.query.filter_by(user_id=self.user.id, name="5% Weight Loss Milestone").first():
            return False # Already has this reward

        if not self.user.weight_history:
            return False
            
        initial_weight = self.user.weight_history[0].weight_kg
        current_weight = self.user.weight_kg

        # Ensure initial_weight is not zero to avoid division by zero error
        if initial_weight == 0:
            return False

        weight_loss_percentage = ((initial_weight - current_weight) / initial_weight) * 100

        if weight_loss_percentage >= percentage_goal:
            # CHANGE 3: Add client_id and use user_id for consistency.
            achievement = Achievement(
                client_id=self.user.client_id,
                user_id=self.user.id,
                name="5% Weight Loss Milestone",
                description=f"Congratulations on losing {weight_loss_percentage:.1f}% of your starting body weight!"
            )
            db.session.add(achievement) # Add to session, but don't commit yet
            return True # Signal that a new reward was added
        return False