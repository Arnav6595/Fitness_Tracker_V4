# This file acts as the single entrypoint for Vercel
from app import create_app

# Vercel will automatically find and serve this 'app' object
app = create_app()