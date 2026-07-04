from flask_mail import Message
from extensions import mail
from config import Config


def send_verification_email(to_email, token):
    verify_link = f"{Config.FRONTEND_URL}/verify-email?token={token}"
    msg = Message(
        subject="Verify your Employee Management System account",
        recipients=[to_email],
        body=(
            "Welcome!\n\n"
            "Please verify your email address by clicking the link below. "
            f"This link expires in {Config.EMAIL_TOKEN_EXP_MINUTES} minutes.\n\n"
            f"{verify_link}\n\n"
            "If you did not create this account, you can ignore this email."
        ),
        html=(
            f"<p>Welcome!</p>"
            f"<p>Please verify your email address by clicking the link below. "
            f"This link expires in {Config.EMAIL_TOKEN_EXP_MINUTES} minutes.</p>"
            f'<p><a href="{verify_link}">Verify my email</a></p>'
            f"<p>If you did not create this account, you can ignore this email.</p>"
        ),
    )
    mail.send(msg)


def send_leave_notification(employee_name, employee_email, leave):
    """Notify HR when an employee submits a new leave request."""
    msg = Message(
        subject=f"New Leave Request from {employee_name}",
        recipients=[Config.HR_NOTIFY_EMAIL],
        body=(
            f"{employee_name} ({employee_email}) has submitted a new leave request.\n\n"
            f"Type: {leave['leave_type']}\n"
            f"From: {leave['start_date']}\n"
            f"To: {leave['end_date']}\n"
            f"Reason: {leave['reason']}\n\n"
            "Please review it in the HR dashboard."
        ),
        html=(
            f"<p><strong>{employee_name}</strong> ({employee_email}) has submitted a new leave request.</p>"
            f"<ul>"
            f"<li><strong>Type:</strong> {leave['leave_type']}</li>"
            f"<li><strong>From:</strong> {leave['start_date']}</li>"
            f"<li><strong>To:</strong> {leave['end_date']}</li>"
            f"<li><strong>Reason:</strong> {leave['reason']}</li>"
            f"</ul>"
            f"<p>Please review it in the HR dashboard.</p>"
        ),
    )
    mail.send(msg)


def send_leave_status_email(employee_email, leave):
    """Notify employee once HR approves/rejects their request."""
    msg = Message(
        subject=f"Your leave request has been {leave['status']}",
        recipients=[employee_email],
        body=(
            f"Your {leave['leave_type']} leave request "
            f"({leave['start_date']} to {leave['end_date']}) has been {leave['status']}."
        ),
        html=(
            f"<p>Your <strong>{leave['leave_type']}</strong> leave request "
            f"({leave['start_date']} to {leave['end_date']}) has been "
            f"<strong>{leave['status']}</strong>.</p>"
        ),
    )
    mail.send(msg)