#!/bin/sh
set -e

# Set working directory
cd /app

# The file-loading commands have been REMOVED from here.
# Docker Compose injects the environment variables from your local .env file automatically.

# Apply database migrations with detailed output
echo "Applying database migrations..."
flask db upgrade

# Start the Gunicorn server with log output
echo "Starting Gunicorn on port 5000..."
# Corrected the app reference to use the factory pattern: "app:create_app()"
exec gunicorn --bind 0.0.0.0:5000 --preload --log-level debug --timeout 120 "app:create_app()"