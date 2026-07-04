import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_ROLES = {"Employee", "HR"}


def validate_password(password):
    """
    Password rules:
      - at least 8 characters
      - at least one uppercase letter
      - at least one lowercase letter
      - at least one digit
      - at least one special character
    Returns (is_valid, error_message)
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\];'`~/\\]", password):
        return False, "Password must contain at least one special character."
    return True, None


def validate_email_format(email):
    if not email or not EMAIL_RE.match(email.strip()):
        return False, "Please enter a valid email address."
    return True, None


def validate_employee_id(employee_id):
    if not employee_id or len(employee_id.strip()) < 3:
        return False, "Employee ID must be at least 3 characters long."
    return True, None


def validate_role(role):
    if role not in VALID_ROLES:
        return False, "Role must be either 'Employee' or 'HR'."
    return True, None
