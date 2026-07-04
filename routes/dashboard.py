from flask import Blueprint, request, jsonify
from utils.decorators import token_required
from models.user import serialize_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/me", methods=["GET"])
@token_required
def me():
    """Returns the logged-in user's profile -- used by the frontend right after
    login/redirect to know who's signed in and which dashboard view to show."""
    return jsonify({"user": serialize_user(request.current_user)}), 200
