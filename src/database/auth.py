"""
auth.py — Authentication service layer for AttendX.

Sits between the UI screens and db.py.
Handles validation, business logic, rate limiting, and structured responses.
All password hashing is delegated to db.py.
"""

import re
import time
import streamlit as st
from src.database.db import (
    login_user,
    create_teacher,
    create_student,
    get_teacher_by_user_id,
    get_student_by_user_id,
    update_student_embeddings,
    check_face_exists,
    generate_verification_token,
    get_user_by_email,
    update_verification_token,
)


# ----------------------------
# RATE LIMITING
# ----------------------------

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes


def _check_rate_limit() -> str | None:
    """Check if the user has exceeded login attempts. Returns error message or None."""
    if 'login_attempts' not in st.session_state:
        st.session_state['login_attempts'] = 0
        st.session_state['login_lockout_until'] = 0

    now = time.time()
    lockout_until = st.session_state.get('login_lockout_until', 0)

    if now < lockout_until:
        remaining = int(lockout_until - now)
        mins = remaining // 60
        secs = remaining % 60
        return f"Too many failed attempts. Please try again in {mins}m {secs}s."

    return None


def _record_failed_attempt():
    """Record a failed login attempt and lock out if threshold exceeded."""
    st.session_state['login_attempts'] = st.session_state.get('login_attempts', 0) + 1
    if st.session_state['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
        st.session_state['login_lockout_until'] = time.time() + LOCKOUT_SECONDS
        st.session_state['login_attempts'] = 0


def _reset_attempts():
    """Reset login attempt counter after successful login."""
    st.session_state['login_attempts'] = 0
    st.session_state['login_lockout_until'] = 0


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
# EMAIL VERIFICATION (EmailJS)
# ----------------------------

def send_otp_email(email: str, name: str, otp: str) -> dict:
    """
    Send a 6-digit OTP verification email via EmailJS REST API.
    
    Requires EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY, 
    and EMAILJS_PRIVATE_KEY to be set in .streamlit/secrets.toml.
    """
    import requests

    try:
        service_id = st.secrets.get("EMAILJS_SERVICE_ID")
        template_id = st.secrets.get("EMAILJS_TEMPLATE_ID")
        public_key = st.secrets.get("EMAILJS_PUBLIC_KEY")
        private_key = st.secrets.get("EMAILJS_PRIVATE_KEY")

        if not all([service_id, template_id, public_key, private_key]):
            # EmailJS not configured — silently skip
            return {"success": True, "message": "Verification skipped (EmailJS not configured)."}

        payload = {
            "service_id": service_id,
            "template_id": template_id,
            "user_id": public_key,
            "accessToken": private_key,
            "template_params": {
                "to_email": email,
                "to_name": name,
                "otp": otp,
                "app_name": "AttendX"
            }
        }

        response = requests.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            return {"success": True, "message": "Verification email sent!"}
        else:
            return {"success": False, "message": f"Failed to send email (status {response.status_code}): {response.text}"}

    except Exception as e:
        return {"success": False, "message": f"Email service error: {str(e)}"}


# ----------------------------
# SIGNUP
# ----------------------------

def validate_signup(name: str, email: str, password: str, confirm_password: str) -> dict:
    """Validates signup fields and checks if user exists. Used for both teachers and students."""
    validation_err = _validate_signup_fields(name, email, password, confirm_password)
    if validation_err:
        return {"success": False, "message": validation_err}

    email = email.strip().lower()
    user = get_user_by_email(email)
    if user:
        return {"success": False, "message": "User already exists with this email."}

    return {"success": True}

def commit_signup(name: str, email: str, password: str, role: str) -> dict:
    """Actually insert the validated user into the database."""
    email = email.strip().lower()
    name = name.strip()
    
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
# STUDENT SIGNUP WITH BIOMETRICS
# ----------------------------


def commit_student_signup(name: str, email: str, password: str, face_embedding: list, voice_embedding: list) -> dict:
    """Actually insert the validated student with biometrics into the database."""
    email = email.strip().lower()
    name = name.strip()
    
    try:
        result = create_student(name, email, password)
        if not result["success"]:
            return {"success": False, "message": result.get("message", "Registration failed.")}

        student_data = result["student"]
        student_id = student_data["student_id"]

        embed_result = update_student_embeddings(
            student_id=student_id,
            face_embedding=face_embedding,
            voice_embedding=voice_embedding
        )

        if not embed_result["success"]:
            return {
                "success": True,
                "message": "Account created, but biometric data could not be saved. Please contact admin.",
                "data": student_data
            }
            

        return {
            "success": True,
            "message": "Student account created successfully!",
            "data": embed_result["student"]
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


# ----------------------------
# LOGIN
# ----------------------------

def login(email: str, password: str) -> dict:
    """
    Authenticate a user and fetch their profile.
    Includes rate limiting protection.

    Returns:
        {
            "success": True/False,
            "message": "...",
            "role": "student" | "teacher" | "admin",
            "user_id": int,
            "profile": { name, etc. }  (None for admin)
        }
    """
    # 0. Check rate limit
    rate_err = _check_rate_limit()
    if rate_err:
        return {"success": False, "message": rate_err}

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
            _record_failed_attempt()
            return {"success": False, "message": auth_result.get("message", "Login failed.")}

        user_id = auth_result["user_id"]
        role = auth_result["role"]

        # 4. Check email verification (if column exists)
        user = get_user_by_email(email)
        if user and user.get('is_verified') is False:
            return {
                "success": False,
                "message": "EMAIL_NOT_VERIFIED",
                "email": email
            }

        # 5. Fetch role-specific profile
        profile = None
        if role == "teacher":
            profile = get_teacher_by_user_id(user_id)
        elif role == "student":
            profile = get_student_by_user_id(user_id)
        # admin → no profile needed

        _reset_attempts()

        return {
            "success": True,
            "message": "Login successful!",
            "role": role,
            "user_id": user_id,
            "profile": profile
        }

    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
