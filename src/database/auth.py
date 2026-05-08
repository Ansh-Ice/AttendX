"""
auth.py — Authentication service layer for AttendX.

Sits between the UI screens and db.py.
Handles validation, business logic, and structured responses.
All password hashing is delegated to db.py.
"""

import re
from src.database.db import (
    login_user,
    create_teacher,
    create_student,
    get_teacher_by_user_id,
    get_student_by_user_id,
)


# ----------------------------
# VALIDATORS
# ----------------------------

def _validate_email(email: str) -> str | None:
    """Returns an error message if invalid, None if valid."""
    if not email or not email.strip():
        return "Email is required."
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return "Please enter a valid email address."
    return None


def _validate_password(password: str) -> str | None:
    """Returns an error message if weak, None if acceptable."""
    if not password:
        return "Password is required."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None


def _validate_signup_fields(name: str, email: str, password: str, confirm_password: str) -> str | None:
    """Runs all signup validations. Returns first error found, or None."""
    if not name or not name.strip():
        return "Full name is required."

    email_err = _validate_email(email)
    if email_err:
        return email_err

    pass_err = _validate_password(password)
    if pass_err:
        return pass_err

    if password != confirm_password:
        return "Passwords do not match."

    return None


# ----------------------------
# SIGNUP
# ----------------------------

def signup(name: str, email: str, password: str, confirm_password: str, role: str) -> dict:
    """
    Register a new user (student or teacher).

    Returns:
        {
            "success": True/False,
            "message": "...",
            "data": { profile dict } (on success)
        }
    """
    # 1. Validate all fields
    validation_err = _validate_signup_fields(name, email, password, confirm_password)
    if validation_err:
        return {"success": False, "message": validation_err}

    # 2. Normalize
    email = email.strip().lower()
    name = name.strip()

    # 3. Create user + profile based on role
    try:
        if role == "teacher":
            result = create_teacher(name, email, password)
            profile_key = "teacher"
        elif role == "student":
            result = create_student(name, email, password)
            profile_key = "student"
        else:
            return {"success": False, "message": f"Invalid role: {role}"}

        if not result["success"]:
            return {"success": False, "message": result.get("message", "Registration failed.")}

        return {
            "success": True,
            "message": f"{role.capitalize()} account created successfully!",
            "data": result.get(profile_key, {})
        }

    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}


# ----------------------------
# LOGIN
# ----------------------------

def login(email: str, password: str) -> dict:
    """
    Authenticate a user and fetch their profile.

    Returns:
        {
            "success": True/False,
            "message": "...",
            "role": "student" | "teacher" | "admin",
            "user_id": int,
            "profile": { name, etc. }  (None for admin)
        }
    """
    # 1. Validate inputs
    email_err = _validate_email(email)
    if email_err:
        return {"success": False, "message": email_err}

    if not password:
        return {"success": False, "message": "Password is required."}

    # 2. Normalize
    email = email.strip().lower()

    # 3. Authenticate against users table
    try:
        auth_result = login_user(email, password)

        if not auth_result["success"]:
            return {"success": False, "message": auth_result.get("message", "Login failed.")}

        user_id = auth_result["user_id"]
        role = auth_result["role"]

        # 4. Fetch role-specific profile
        profile = None
        if role == "teacher":
            profile = get_teacher_by_user_id(user_id)
        elif role == "student":
            profile = get_student_by_user_id(user_id)
        # admin → no profile needed

        return {
            "success": True,
            "message": "Login successful!",
            "role": role,
            "user_id": user_id,
            "profile": profile
        }

    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
