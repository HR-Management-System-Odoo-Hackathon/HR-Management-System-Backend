from functools import wraps
from flask import request, jsonify
import jwt
from utils.tokens import decode_auth_token
from models.user import find_by_id


def token_required(f):
    """Reads 'Authorization: Bearer <token>', attaches request.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Authentication token is missing."}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_auth_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Session expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid authentication token."}), 401

        user = find_by_id(payload["user_id"])
        if not user:
            return jsonify({"message": "User no longer exists."}), 401

        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def roles_required(*allowed_roles):
    """Stack under @token_required. e.g. @roles_required('HR')"""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.current_user.get("role") not in allowed_roles:
                return jsonify({"message": "You do not have permission to perform this action."}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper
