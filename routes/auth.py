import bcrypt
import jwt
from flask import Blueprint, request, jsonify

from models.user import (
    find_by_email, find_by_employee_id, create_user, mark_verified, serialize_user,
)
from utils.validators import (
    validate_password, validate_email_format, validate_employee_id, validate_role,
)
from utils.tokens import generate_auth_token, generate_email_token, decode_email_token
from utils.mailer import send_verification_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    employee_id = (data.get("employee_id") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "").strip()

    # ---- Validate input ----
    ok, err = validate_employee_id(employee_id)
    if not ok:
        return jsonify({"message": err}), 400

    ok, err = validate_email_format(email)
    if not ok:
        return jsonify({"message": err}), 400

    ok, err = validate_role(role)
    if not ok:
        return jsonify({"message": err}), 400

    ok, err = validate_password(password)
    if not ok:
        return jsonify({"message": err}), 400

    # ---- Uniqueness checks ----
    if find_by_email(email):
        return jsonify({"message": "An account with this email already exists."}), 409

    if find_by_employee_id(employee_id):
        return jsonify({"message": "An account with this Employee ID already exists."}), 409

    # ---- Create user ----
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = create_user(employee_id, email, password_hash, role)

    # ---- Send verification email ----
    token = generate_email_token(email)
    try:
        send_verification_email(email, token)
    except Exception as e:
        # Account is created either way; surface a clear message so the frontend
        # can tell the user verification email delivery failed and offer a resend.
        return jsonify({
            "message": "Account created, but the verification email could not be sent. Please try resending it.",
            "user": serialize_user(user),
            "email_error": str(e),
        }), 201

    return jsonify({
        "message": "Account created. Please check your email to verify your account.",
        "user": serialize_user(user),
    }), 201


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()

    user = find_by_email(email)
    if not user:
        # Do not reveal whether the email exists.
        return jsonify({"message": "If an account exists for this email, a verification link has been sent."}), 200

    if user.get("is_verified"):
        return jsonify({"message": "This account is already verified. You can log in."}), 200

    token = generate_email_token(email)
    try:
        send_verification_email(email, token)
    except Exception as e:
        return jsonify({"message": "Could not send verification email. Please try again later."}), 500

    return jsonify({"message": "Verification email sent."}), 200


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    token = request.args.get("token") or (request.get_json(silent=True) or {}).get("token")
    if not token:
        return jsonify({"message": "Verification token is missing."}), 400

    try:
        payload = decode_email_token(token)
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "This verification link has expired. Please request a new one."}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "This verification link is invalid."}), 400

    email = payload["email"]
    user = find_by_email(email)
    if not user:
        return jsonify({"message": "No account found for this verification link."}), 404

    if user.get("is_verified"):
        return jsonify({"message": "Email already verified. You can log in."}), 200

    mark_verified(email)
    return jsonify({"message": "Email verified successfully. You can now log in."}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = find_by_email(email)

    # Generic message for both "no such user" and "wrong password" -- avoids
    # leaking which emails are registered.
    invalid_credentials_msg = "Incorrect email or password."

    if not user:
        return jsonify({"message": invalid_credentials_msg}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"message": invalid_credentials_msg}), 401

    if not user.get("is_verified"):
        return jsonify({"message": "Please verify your email before logging in."}), 403

    token = generate_auth_token(user["_id"], user["role"])
    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": serialize_user(user),
    }), 200
