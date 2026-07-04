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
