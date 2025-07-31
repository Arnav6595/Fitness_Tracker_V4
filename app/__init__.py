# app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables from .env file
load_dotenv()

# Initialize extensions without attaching them to an app yet
db = SQLAlchemy()
migrate = Migrate()

# --- Swagger UI Configuration ---
# This sets up the endpoint for your interactive API documentation.
SWAGGER_URL = '/api/docs'  # The URL for the documentation page
API_URL = '/static/swagger.yaml'  # The path to your documentation content file

# Create the Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Fitness Tracker API"
    }
)
# ---------------------------------

def create_app(test_config=None):
    """
    Creates and configures an instance of the Flask application.
    This is the Application Factory pattern.
    """
    app = Flask(__name__)

    if test_config is None:
        # --- Normal App Execution ---
        # Load the default configuration from the config object
        app.config.from_object(Config)

        # IMPORTANT: Override with sensitive values from environment variables
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    else:
        # --- Test Execution ---
        # Load the test configuration if it's passed in
        app.config.from_mapping(test_config)


    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints for all your API routes
    from .api.auth_routes import auth_bp
    from .api.diet_routes import diet_bp
    from .api.workout_routes import workout_bp
    from .api.progress_routes import progress_bp
    from .api.reward_routes import reward_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(diet_bp, url_prefix='/api/diet')
    app.register_blueprint(workout_bp, url_prefix='/api/workout')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(reward_bp, url_prefix='/api/reward')

    # Register the Swagger UI blueprint with the app
    app.register_blueprint(swaggerui_blueprint)

    # --- Set up and start the background scheduler ---
    # Avoid running the scheduler during tests
    if not app.config.get("TESTING"):
        from .services.adaptive_planner_service import run_weekly_adaptive_planning

        scheduler = BackgroundScheduler(daemon=True)
        # Schedule the job to run every Sunday at 2 AM
        scheduler.add_job(run_weekly_adaptive_planning, 'cron', day_of_week='sun', hour=2)
        scheduler.start()
    # ---------------------------------------------
   
    from app import models
    return app
