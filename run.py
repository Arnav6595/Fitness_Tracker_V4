# run.py
from dotenv import load_dotenv

# This loads the environment variables from the .env file
load_dotenv()

# Import the application factory from your app package
from app import create_app

# Create an instance of your application
app = create_app()
print("DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("DB Options:", app.config['SQLALCHEMY_ENGINE_OPTIONS'])


if __name__ == '__main__':
    # This will run the development server
    app.run(host='0.0.0.0', port=5000, debug=True)