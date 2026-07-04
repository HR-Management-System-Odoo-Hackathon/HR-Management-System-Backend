from datetime import datetime
from bson import ObjectId
from extensions import db

users = db.users

# Run once at startup (see app.py) to enforce uniqueness at the DB level.
def ensure_indexes():
    users.create_index("email", unique=True)
    users.create_index("employee_id", unique=True)


def serialize_user(user):
    """Convert a Mongo user document into a JSON-safe dict (never expose password_hash)."""
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "employee_id": user.get("employee_id"),
        "email": user.get("email"),
        "role": user.get("role"),
        "is_verified": user.get("is_verified", False),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
    }


def find_by_email(email):
    return users.find_one({"email": email.lower().strip()})


def find_by_employee_id(employee_id):
    return users.find_one({"employee_id": employee_id.strip()})


def find_by_id(user_id):
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def create_user(employee_id, email, password_hash, role):
    doc = {
        "employee_id": employee_id.strip(),
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "role": role,  # "Employee" or "HR"
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }
    result = users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def mark_verified(email):
    users.update_one({"email": email.lower().strip()}, {"$set": {"is_verified": True}})
