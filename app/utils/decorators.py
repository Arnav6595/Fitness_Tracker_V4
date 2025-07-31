# app/utils/decorators.py

from functools import wraps
from flask import request, g, jsonify
from app.models import Client

def require_api_key(f):
    """
    Decorator to protect routes with API key authentication.

    This function acts as a wrapper around your API route functions. It checks
    for a valid API key in the 'X-API-Key' header before allowing the
    request to proceed to the actual route logic.

    If the key is valid, it finds the corresponding client and attaches it
    to Flask's global 'g' object, making it accessible within the route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Get the API key from the request headers.
        api_key = request.headers.get('X-API-Key')
        
        # 2. If no key is provided, block the request with a 401 Unauthorized error.
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401

        # 3. Look for a client in the database with a matching API key.
        client = Client.query.filter_by(api_key=api_key).first()

        # 4. If the key doesn't match any client, block with a 403 Forbidden error.
        if not client:
            return jsonify({"error": "API key is invalid or unauthorized"}), 403

        # 5. If the key is valid, attach the client object to the request context.
        # This allows you to use `g.client` inside your route.
        g.client = client
        
        # 6. Finally, call the original route function (e.g., register_user).
        return f(*args, **kwargs)
    return decorated_function