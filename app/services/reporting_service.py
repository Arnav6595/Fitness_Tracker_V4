# app/services/reporting_service.py
from app.models import User, DietLog, WorkoutLog, WeightEntry, db
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from flask import abort

class ReportingService:
    def __init__(self, user_id):
        # FIX 1: Replaced deprecated get_or_404 with db.session.get
        self.user = db.session.get(User, user_id)
        if not self.user:
            abort(404, description=f"User with id {user_id} not found.")
        self.target_calories = self._calculate_target_calories()

    def _calculate_target_calories(self):
        """
        Calculates a robust TDEE based on the user's stored profile data.
        """
        # 1. Calculate BMR (no change here)
        if self.user.gender.lower() == 'male':
            bmr = 10 * self.user.weight_kg + 6.25 * self.user.height_cm - 5 * self.user.age + 5
        else:
            bmr = 10 * self.user.weight_kg + 6.25 * self.user.height_cm - 5 * self.user.age - 161
        
        # 2. Get the correct TDEE multiplier based on the user's activity level
        activity_multipliers = {
            'sedentary': 1.2,
            'lightlyactive': 1.375,
            'moderatelyactive': 1.55,
            'veryactive': 1.725,
            'extraactive': 1.9
        }
        
        # Use the user's stored activity_level, defaulting to sedentary if not set
        user_activity_level = (self.user.activity_level or 'sedentary').lower().replace(" ", "")
        multiplier = activity_multipliers.get(user_activity_level, 1.2)
        tdee = bmr * multiplier

        # 3. Adjust for fitness goal (no change here)
        goal = self.user.fitness_goals.lower()
        if 'loss' in goal:
            return tdee - 500
        elif 'gain' in goal:
            return tdee + 500
        else: # maintainWeight
            return tdee

    def get_diet_adherence_score(self, days=7):
        """Calculates the diet adherence score over a given period."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        daily_logs = db.session.query(
            func.date(DietLog.date),
            func.sum(DietLog.calories)
        ).filter(
            DietLog.user_id == self.user.id,
            DietLog.date >= start_date
        ).group_by(func.date(DietLog.date)).all()

        if not daily_logs:
            return 0

        total_adherence = 0
        for day_log in daily_logs:
            actual_calories = day_log[1]
            # Calculate adherence for the day (max score 100)
            # Score decreases as you move away from the target
            day_adherence = max(0, 100 - abs(actual_calories - self.target_calories) / self.target_calories * 100)
            total_adherence += day_adherence
        
        return round(total_adherence / len(daily_logs), 2)

    def get_weekly_report(self):
        """Gathers all data needed for a weekly summary report."""
        # FIX 2: Replaced deprecated utcnow() with datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        # 1. Weight Trend (now as a number)
        weight_history = WeightEntry.query.filter(
            WeightEntry.user_id == self.user.id,
            WeightEntry.date >= start_date
        ).order_by(WeightEntry.date.asc()).all()
        
        weight_change_kg = 0.0 # Default to a number
        if len(weight_history) >= 2:
            start_weight = weight_history[0].weight_kg
            end_weight = weight_history[-1].weight_kg
            weight_change_kg = round(end_weight - start_weight, 2)

        # 2. Workout Performance
        workouts_completed = WorkoutLog.query.filter(
            WorkoutLog.user_id == self.user.id,
            WorkoutLog.date >= start_date
        ).count()

        # 3. Diet Adherence
        adherence_score = self.get_diet_adherence_score(days=7)

        # 4. Assemble the report with raw numbers
        report = {
            "user_name": self.user.name,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "summary": {
                "weight_change_kg": weight_change_kg, # Use the numeric value
                "workouts_completed": workouts_completed,
                "diet_adherence_score": adherence_score,
                "target_daily_calories": round(self.target_calories)
            }
        }
        return report