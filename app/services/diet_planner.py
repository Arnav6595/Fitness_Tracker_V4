import os
import google.generativeai as genai
import json

class DietPlannerService:
    def __init__(self, user, form_data):
        self.user = user
        self.form_data = form_data # For data not stored in the user model like budget
        self.bmr = 0
        self.tdee = 0

    def _calculate_bmr(self):
        # Using data from the user database object
        if self.user.gender.lower() == 'male':
            self.bmr = 10 * self.user.weight_kg + 6.25 * self.user.height_cm - 5 * self.user.age + 5
        else:
            self.bmr = 10 * self.user.weight_kg + 6.25 * self.user.height_cm - 5 * self.user.age - 161

    def _calculate_tdee(self):
        activity_multipliers = {
            'sedentary': 1.2,
            'lightlyActive': 1.375,
            'moderatelyActive': 1.55,
            'veryActive': 1.725,
            'extraActive': 1.9
        }
        # Using form_data for activity level which might be temporary
        activity_level = self.form_data.get('activityLevel', 'sedentary')
        multiplier = activity_multipliers.get(activity_level, 1.2)
        self.tdee = self.bmr * multiplier

    def _adjust_calories_for_goal(self):
        goal = self.user.fitness_goals.lower()
        if 'loss' in goal:
            return self.tdee - 500
        elif 'gain' in goal:
            return self.tdee + 500
        else:
            return self.tdee

    def _generate_llm_prompt(self, target_calories):
        # Get temporary data from the incoming request
        diet_preference = self.form_data.get('diet_type', 'veg').capitalize()
        monthly_budget = self.form_data.get('budget', '5000').replace(',', '')
        optional_cuisines = self.form_data.get('optional_cuisines', [])
        activity_level = self.form_data.get('activityLevel', 'sedentary')

        # --- NEW, MORE ROBUST LOGIC ---
        # 1. Filter the list to get only valid, non-placeholder cuisine names.
        valid_cuisines = [
            cuisine for cuisine in optional_cuisines
            if cuisine and isinstance(cuisine, str) and cuisine.strip().lower() not in ['', 'string']
        ]

        # 2. Conditionally build the prompt and a clean summary string.
        if valid_cuisines:
            cuisine_list_str = ", ".join(valid_cuisines)
            cuisine_prompt = f"The diet should be primarily Indian, but incorporate 2-3 meals from the following cuisines for variety: {cuisine_list_str}."
            cuisine_summary = f"Primarily Indian with some {cuisine_list_str} options."
        else:
            cuisine_prompt = "The diet must be strictly Indian, using commonly available ingredients in India."
            cuisine_summary = "Strictly Indian"
        # --- END OF NEW LOGIC ---

        prompt = f"""
        You are an expert nutritionist and fitness coach based in India.
        Please generate a comprehensive, 7-day weekly diet plan based on the following detailed instructions.

        Core Instructions:
        - Cuisine Focus: {cuisine_prompt}
        - Dietary Preference: {diet_preference}. (Note: For 'Veg', include dairy products like milk, paneer, and curd, but no eggs. For 'Non-veg', eggs, chicken, and fish are acceptable).
        - Monthly Food Budget: Approximately ₹{monthly_budget}. Meals should be cost-effective.
        - Primary Goal: {self.user.fitness_goals}
        - Target Daily Calories: Approximately {target_calories:.0f} kcal/day. Ensure meal diversity and portion control.
        - Meals must be balanced in macronutrients. Avoid processed, sugary, or deep-fried foods.

        User's Personal Information:
        - Age: {self.user.age}
        - Gender: {self.user.gender}
        - Weight: {self.user.weight_kg} kg
        - Height: {self.user.height_cm} cm
        - Activity Level: {activity_level}
        - Strict Food Avoidance: The user dislikes the following foods, which MUST NOT be included in the plan: {self.user.disliked_foods or 'None'}.
        - Allergen Alert: The user has the following allergies, so ingredients causing these MUST BE EXCLUDED: {self.user.allergies or 'None'}.

        Output Requirements:
        1. Provide a full 7-day meal plan (Monday to Sunday).
        2. Each day must have: Breakfast, Lunch, Dinner, and two Snacks.
        3. For each meal, list food items, portion sizes (cups, grams, rotis), and estimated calories.
        4. Output must be ONLY a valid JSON object — no comments, markdown, or extra text.
        5. JSON structure:
        {{
            "weekly_plan": {{
                "Monday": {{
                    "Breakfast": {{"items": "...", "portion": "...", "calories": ...}},
                    "Lunch": {{"items": "...", "portion": "...", "calories": ...}},
                    "Snack1": {{"items": "...", "portion": "...", "calories": ...}},
                    "Dinner": {{"items": "...", "portion": "...", "calories": ...}},
                    "Snack2": {{"items": "...", "portion": "...", "calories": ...}}
                }},
                "Tuesday": {{...}},
                "Wednesday": {{...}},
                "Thursday": {{...}},
                "Friday": {{...}},
                "Saturday": {{...}},
                "Sunday": {{...}}
            }},
            "summary": {{
                "primary_goal": "{self.user.fitness_goals}",
                "target_daily_calories": "{target_calories:.0f}",
                "cuisine_focus": "{cuisine_summary}",
                "dietary_preference": "{diet_preference}"
            }}
        }}
        """
        return prompt

    def _call_llm_api(self, prompt):
        model = genai.GenerativeModel('gemini-2.5-pro') # Or your preferred model
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
        
    def _adjust_calories_for_goal(self, adjustment=0): # Add the adjustment parameter
        goal = self.user.fitness_goals.lower()
        base_calories = 0
        if 'loss' in goal:
            base_calories = self.tdee - 500
        elif 'gain' in goal:
            base_calories = self.tdee + 500
        else:
            base_calories = self.tdee
        
        # Apply the dynamic adjustment
        return base_calories + adjustment
    
    def generate_plan(self, calorie_adjustment=0): # Add the calorie_adjustment parameter
        try:
            self._calculate_bmr()
            self._calculate_tdee()
            # Pass the adjustment to the calculation
            target_calories = self._adjust_calories_for_goal(adjustment=calorie_adjustment)
            prompt = self._generate_llm_prompt(target_calories)
            final_plan = self._call_llm_api(prompt)
            return {"success": True, "plan": final_plan}
        except Exception as e:
            return {"success": False, "error": str(e)}

