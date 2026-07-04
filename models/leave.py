from datetime import datetime
from bson import ObjectId
from extensions import db

LEAVE_TYPES = ["Casual", "Sick", "Earned", "Unpaid"]
LEAVE_STATUSES = ["Pending", "Approved", "Rejected"]


def create_leave_request(user_id, leave_type, start_date, end_date, reason):
    doc = {
        "user_id": ObjectId(user_id),
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": "Pending",
        "reviewed_by": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = db.leave_requests.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_leaves_for_user(user_id):
    cursor = db.leave_requests.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1)
    return list(cursor)


def get_all_leaves():
    cursor = db.leave_requests.find().sort("created_at", -1)
    return list(cursor)


def find_leave_by_id(leave_id):
    return db.leave_requests.find_one({"_id": ObjectId(leave_id)})


def delete_leave(leave_id):
    result = db.leave_requests.delete_one({"_id": ObjectId(leave_id)})
    return result.deleted_count > 0


def update_leave_status(leave_id, status, reviewer_id):
    db.leave_requests.update_one(
        {"_id": ObjectId(leave_id)},
        {
            "$set": {
                "status": status,
                "reviewed_by": ObjectId(reviewer_id),
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return find_leave_by_id(leave_id)


def serialize_leave(doc):
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "leave_type": doc["leave_type"],
        "start_date": doc["start_date"].isoformat(),
        "end_date": doc["end_date"].isoformat(),
        "reason": doc["reason"],
        "status": doc["status"],
        "reviewed_by": str(doc["reviewed_by"]) if doc.get("reviewed_by") else None,
        "created_at": doc["created_at"].isoformat(),
    }