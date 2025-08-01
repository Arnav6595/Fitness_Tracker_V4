# app/utils/decorators.py

from functools import wraps
from flask import request, g, jsonify, current_app
from app.models import Client, User
import jwt

def require_api_key(f):
    """
    Decorator to protect routes with API key authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401

        client = Client.query.filter_by(api_key=api_key).first()
        if not client:
            return jsonify({"error": "API key is invalid or unauthorized"}), 403

        g.client = client
        return f(*args, **kwargs)
    return decorated_function


def require_jwt(f):
    """
    Decorator to protect routes with JWT authentication for end-users.
    It now ALSO validates the client API key to ensure the user belongs to the client.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. First, validate the client's API Key
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401

        client = Client.query.filter_by(api_key=api_key).first()
        if not client:
            return jsonify({"error": "API key is invalid or unauthorized"}), 403
        
        # 2. Next, validate the user's JWT
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authentication token is missing!"}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.query.get(data['user_id'])

            # 3. Finally, verify the user belongs to the client
            if not user or user.client_id != client.id:
                return jsonify({"error": "User not found or does not belong to this client"}), 404

            g.current_user = user
            g.client = client # Also attach the client for consistency

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)
    return decorated_function