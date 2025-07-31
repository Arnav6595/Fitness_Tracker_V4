# app/services/workout_planner_service.py
import google.generativeai as genai
import json

class WorkoutPlannerService:
    def __init__(self, user, form_data):
        self.user = user
        self.form_data = form_data

    def _generate_llm_prompt(self):
        # Using details from the user's profile and the request form
        prompt = f"""
        Please generate a detailed, 7-day weekly workout plan based on the following user profile.
        The output MUST be only a valid JSON object.

        **User Profile & Goals:**
        - Primary Goal: {self.user.fitness_goals} [cite: 9]
        - Fitness Level: {self.form_data.get('fitnessLevel', 'beginner')} [cite: 12]
        - Workouts Per Week: {self.user.workouts_per_week} [cite: 106]
        - Preferred Duration: {self.user.workout_duration} minutes per session [cite: 106]
        - Equipment Availability: {self.form_data.get('equipment', 'bodyweight only')} [cite: 14]
        - Existing Injuries or Conditions: {self.user.health_conditions} [cite: 13]

        **Workout Plan Requirements:**
        - Create a schedule for the entire week (Monday to Sunday), scheduling rest days appropriately based on the 'Workouts Per Week' value.
        - For each workout day, provide a list of 5-7 exercises. [cite: 18]
        - For each exercise, specify the name, target sets, reps, and rest time in seconds. [cite: 18]
        - The plan should be categorized by muscle group or workout type (e.g., Push, Pull, Legs, Cardio). [cite: 19]
        - Include a brief "form_guidance" tip for each exercise. [cite: 18]

        **JSON Output Structure Requirement:**
        {{
          "plan_name": "Weekly Plan for {self.user.fitness_goals}",
          "weekly_schedule": {{
            "Monday": {{
              "day_type": "Push Day",
              "exercises": [
                {{"name": "Bench Press", "sets": 4, "reps": 8, "rest_seconds": 60, "form_guidance": "..."}},
                ...
              ]
            }},
            "Tuesday": {{
              "day_type": "Rest"
            }},
            ...
          }}
        }}
        """
        return prompt

    def _call_llm_api(self, prompt):
        model = genai.GenerativeModel('gemini-2.5-pro')
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)

    def generate_plan(self):
        try:
            prompt = self._generate_llm_prompt()
            final_plan = self._call_llm_api(prompt)
            return {"success": True, "plan": final_plan}
        except Exception as e:
            return {"success": False, "error": str(e)}