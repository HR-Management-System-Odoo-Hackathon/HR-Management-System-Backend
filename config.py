import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/employee_management")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 8))

    EMAIL_TOKEN_SECRET = os.getenv("EMAIL_TOKEN_SECRET", "dev-email-secret-change-me")
    EMAIL_TOKEN_EXP_MINUTES = int(os.getenv("EMAIL_TOKEN_EXP_MINUTES", 30))

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
