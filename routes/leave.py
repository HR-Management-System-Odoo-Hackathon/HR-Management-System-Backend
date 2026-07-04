from datetime import datetime
from flask import Blueprint, request, jsonify
from utils.decorators import token_required, roles_required
from models.leave import (
    create_leave_request,
    get_leaves_for_user,
    get_all_leaves,
    find_leave_by_id,
    delete_leave,
    update_leave_status,
    serialize_leave,
    LEAVE_TYPES,
)
from utils.mailer import send_leave_notification, send_leave_status_email

leave_bp = Blueprint("leave", __name__, url_prefix="/api/leave")


def _parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {field_name}, expected YYYY-MM-DD.")


@leave_bp.route("/apply", methods=["POST"])
@token_required
def apply_leave():
    data = request.get_json() or {}
    leave_type = data.get("leaveType")
    reason = (data.get("reason") or "").strip()

    if leave_type not in LEAVE_TYPES:
        return jsonify({"message": "Invalid leave type."}), 400
    if not reason:
        return jsonify({"message": "Reason is required."}), 400

    try:
        start_date = _parse_date(data.get("startDate"), "startDate")
        end_date = _parse_date(data.get("endDate"), "endDate")
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    if end_date < start_date:
        return jsonify({"message": "End date cannot be before start date."}), 400

    user = request.current_user
    leave = create_leave_request(
        user_id=user["_id"], leave_type=leave_type,
        start_date=start_date, end_date=end_date, reason=reason,
    )

    try:
        send_leave_notification(
            employee_name=user.get("name", "Employee"),
            employee_email=user.get("email"),
            leave=serialize_leave(leave),
        )
    except Exception as e:
        # Don't fail the request just because the email didn't send
        print(f"Failed to send HR notification email: {e}")

    return jsonify(serialize_leave(leave)), 201


@leave_bp.route("/my", methods=["GET"])
@token_required
def my_leaves():
    user = request.current_user
    leaves = get_leaves_for_user(user["_id"])
    return jsonify([serialize_leave(l) for l in leaves]), 200


@leave_bp.route("/<leave_id>", methods=["DELETE"])
@token_required
def cancel_leave(leave_id):
    user = request.current_user
    leave = find_leave_by_id(leave_id)

    if not leave:
        return jsonify({"message": "Leave request not found."}), 404
    if str(leave["user_id"]) != str(user["_id"]):
        return jsonify({"message": "Not authorized."}), 403
    if leave["status"] != "Pending":
        return jsonify({"message": "Only pending requests can be cancelled."}), 400

    delete_leave(leave_id)
    return jsonify({"message": "Leave request cancelled."}), 200


@leave_bp.route("/all", methods=["GET"])
@token_required
@roles_required("HR", "Admin")
def all_leaves():
    leaves = get_all_leaves()
    return jsonify([serialize_leave(l) for l in leaves]), 200


@leave_bp.route("/<leave_id>/status", methods=["PATCH"])
@token_required
@roles_required("HR", "Admin")
def change_leave_status(leave_id):
    data = request.get_json() or {}
    status = data.get("status")

    if status not in ("Approved", "Rejected"):
        return jsonify({"message": "Invalid status."}), 400

    leave = find_leave_by_id(leave_id)
    if not leave:
        return jsonify({"message": "Leave request not found."}), 404

    reviewer = request.current_user
    updated = update_leave_status(leave_id, status, reviewer["_id"])

    try:
        from models.user import find_by_id
        employee = find_by_id(str(updated["user_id"]))
        if employee:
            send_leave_status_email(employee["email"], serialize_leave(updated))
    except Exception as e:
        print(f"Failed to send status update email: {e}")

    return jsonify(serialize_leave(updated)), 200