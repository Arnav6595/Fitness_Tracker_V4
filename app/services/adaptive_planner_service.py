# app/services/adaptive_planner_service.py

from flask import current_app
import google.generativeai as genai
from app.models import db, User, WorkoutPlan
from .reporting_service import ReportingService
from .diet_planner import DietPlannerService
from .workout_planner_service import WorkoutPlannerService
import json

class AdaptivePlannerService:
    """
    A service dedicated to the weekly adaptive planning loop.
    """
    def __init__(self):
        # Configure the Gemini API once for the job
        try:
            gemini_api_key = current_app.config.get('GEMINI_API_KEY')
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY not configured.")
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        except Exception as e:
            print(f"A critical error occurred during API configuration: {e}")
            self.model = None

    def _get_dynamic_adjustment(self, user, report):
        """
        Asks the AI for a calorie adjustment based on the weekly report.
        """
        print("  - Asking AI for dynamic calorie adjustment...")
        prompt = f"""
        A user's primary fitness goal is '{user.fitness_goals}'.
        Based on their weekly progress report below, suggest a daily calorie adjustment for the next week.
        The user's target daily calories were {report['summary']['target_daily_calories']} kcal.
        Their diet adherence was {report['summary']['diet_adherence_score']}% and their weight changed by {report['summary']['weight_change_kg']} kg.

        - If their goal is 'weight loss' and they gained weight or didn't lose enough, suggest a negative adjustment (e.g., -150).
        - If their goal is 'weight gain' and they lost weight or didn't gain enough, suggest a positive adjustment (e.g., +150).
        - If progress is good, suggest a small or zero adjustment.

        Respond with ONLY a single integer number representing the calorie adjustment and nothing else.
        Example response: -100
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean up the response and convert to integer
            adjustment = int(response.text.strip())
            return adjustment
        except Exception as e:
            print(f"    - Could not get dynamic adjustment from AI: {e}. Defaulting to 0.")
            return 0 # Default to no adjustment if AI fails

    def run_for_all_users(self):
        """
        Iterates through all users and generates new, adjusted plans.
        """
        if not self.model:
            print("Aborting job due to API configuration error.")
            return

        all_users = User.query.all()
        for user in all_users:
            try:
                print(f"Processing user: {user.name} (ID: {user.id})")
                
                reporter = ReportingService(user.id)
                report = reporter.get_weekly_report()
                
                # Get the dynamic calorie adjustment from the AI
                calorie_adjustment = self._get_dynamic_adjustment(user, report)
                print(f"  - AI suggested calorie adjustment of: {calorie_adjustment} kcal")

                # Generate new plans with the dynamic adjustment
                diet_planner = DietPlannerService(user, form_data={})
                diet_result = diet_planner.generate_plan(calorie_adjustment=calorie_adjustment)
                
                if diet_result.get("success"):
                    print(f"  - Successfully generated new diet plan for {user.name}.")
                
                # You could similarly add logic to adjust and regenerate workout plans
                
            except Exception as e:
                print(f"  - An error occurred for user {user.id}: {e}")
                continue
        
        # This part of the logic does not directly interact with the DB,
        # so commit is not needed here. Plan saving happens in the planner services.

# This is the function the scheduler will call
def run_weekly_adaptive_planning():
    print("Starting weekly adaptive planning job...")
    from run import app
    with app.app_context():
        planner = AdaptivePlannerService()
        planner.run_for_all_users()
    print("Weekly adaptive planning job finished.")