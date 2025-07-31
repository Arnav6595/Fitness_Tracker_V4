#!/bin/sh
set -e

# Set working directory
cd /app

# Load environment
export $(grep -v '^#' .env | xargs)

# Apply database migrations with detailed output
echo "Applying database migrations..."
flask db upgrade 

# Start the Gunicorn server with log output
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --preload --log-level debug app:create_app