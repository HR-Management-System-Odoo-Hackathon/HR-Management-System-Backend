import jwt
from datetime import datetime, timedelta
from config import Config

# ---------- Login session tokens ----------

def generate_auth_token(user_id, role):
    payload = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXP_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def decode_auth_token(token):
    """Returns payload dict, or raises jwt exceptions the caller should handle."""
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])


# ---------- Email verification tokens (separate secret + short expiry) ----------

def generate_email_token(email):
    payload = {
        "email": email.lower().strip(),
        "purpose": "email_verification",
        "exp": datetime.utcnow() + timedelta(minutes=Config.EMAIL_TOKEN_EXP_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, Config.EMAIL_TOKEN_SECRET, algorithm="HS256")


def decode_email_token(token):
    payload = jwt.decode(token, Config.EMAIL_TOKEN_SECRET, algorithms=["HS256"])
    if payload.get("purpose") != "email_verification":
        raise jwt.InvalidTokenError("Wrong token purpose")
    return payload
