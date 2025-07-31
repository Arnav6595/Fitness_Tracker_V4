# config.py
import os

class Config:
    """
    Set Flask configuration variables from environment variables.
    """
    # Get the secret key from the environment
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Get the database URL from the environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
    "connect_args": {
        "options": "-c search_path=neondb"
          # or "public"
    }
}

    
    # Suppress a warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    """Set Flask configuration variables from environment variables."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- ADD THIS LINE ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')