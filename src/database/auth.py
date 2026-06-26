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

def send_verification_email(email: str, name: str, token: str) -> dict:
    """
    Send a verification email via EmailJS REST API.
    
    Requires EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, and EMAILJS_PUBLIC_KEY
    to be set in .streamlit/secrets.toml.
    """
    import requests

    try:
        service_id = st.secrets.get("EMAILJS_SERVICE_ID")
        template_id = st.secrets.get("EMAILJS_TEMPLATE_ID")
        public_key = st.secrets.get("EMAILJS_PUBLIC_KEY")
        private_key = st.secrets.get("EMAILJS_PRIVATE_KEY")
        base_url = st.secrets.get("APP_BASE_URL", "https://attendx-046.streamlit.app")

        if not all([service_id, template_id, public_key, private_key]):
            # EmailJS not configured — silently skip
            return {"success": True, "message": "Verification skipped (EmailJS not configured)."}

        verification_link = f"{base_url}/?verify-token={token}"

        payload = {
            "service_id": service_id,
            "template_id": template_id,
            "user_id": public_key,
            "accessToken": private_key,
            "template_params": {
                "to_email": email,
                "to_name": name,
                "verification_link": verification_link,
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


def resend_verification(email: str) -> dict:
    """Resend verification email with a new token."""
    user = get_user_by_email(email)
    if not user:
        return {"success": False, "message": "User not found."}

    if user.get('is_verified'):
        return {"success": False, "message": "Email is already verified."}

    token = generate_verification_token()
    update_result = update_verification_token(user['user_id'], token)
    if not update_result.get('success'):
        return {"success": False, "message": "Failed to generate new token."}

    name = user.get('email', '').split('@')[0]  # Fallback name
    return send_verification_email(email, name, token)


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

    # 3. Check if user already exists
    user = get_user_by_email(email)
    if user:
        return {"success": False, "message": "User already exists with this email."}

    # 4. Generate token and save to pending_registrations
    try:
        token = generate_verification_token()
        
        from src.database.db import create_pending_registration
        result = create_pending_registration(
            token=token,
            name=name,
            email=email,
            password=password,
            role=role
        )

        if not result["success"]:
            return {"success": False, "message": result.get("message", "Registration failed.")}

        # 5. Send verification email
        email_result = send_verification_email(email, name, token)
        
        if email_result.get("success"):
            return {
                "success": True,
                "message": f"{role.capitalize()} account created! Please check your email to verify and complete registration.",
                "data": {}
            }
        else:
            return {
                "success": False,
                "message": f"Registration saved, but failed to send verification email: {email_result.get('message')}"
            }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


# ----------------------------
# STUDENT SIGNUP WITH BIOMETRICS
# ----------------------------

def signup_student_with_biometrics(
    name: str,
    email: str,
    password: str,
    confirm_password: str,
    face_embedding: list,
    voice_embedding: list
) -> dict:
    """
    Register a student with face and voice biometric data.

    Flow:
        1. Validate form fields
        2. Check if face already exists in database
        3. Create user + student record
        4. Store face & voice embeddings
        5. Send verification email

    Returns:
        {
            "success": True/False,
            "message": "...",
            "data": { student profile dict }
        }
    """
    # 1. Validate form fields
    validation_err = _validate_signup_fields(name, email, password, confirm_password)
    if validation_err:
        return {"success": False, "message": validation_err}

    # 2. Validate biometric data is present
    if not face_embedding:
        return {"success": False, "message": "Face data is required. Please capture your photo."}
    if not voice_embedding:
        return {"success": False, "message": "Voice data is required. Please record your audio."}

    # 3. Normalize inputs
    email = email.strip().lower()
    name = name.strip()

    # 4. Check if this face is already registered
    try:
        face_check = check_face_exists(face_embedding)
        if face_check["exists"]:
            existing = face_check["student"]
            return {
                "success": False,
                "message": f"This face is already registered to '{existing.get('name', 'another student')}'."
            }
    except Exception as e:
        return {"success": False, "message": f"Face verification error: {str(e)}"}

    # 5. Check if user already exists
    user = get_user_by_email(email)
    if user:
        return {"success": False, "message": "User already exists with this email."}

    # 6. Save to pending_registrations
    try:
        token = generate_verification_token()
        
        from src.database.db import create_pending_registration
        result = create_pending_registration(
            token=token,
            name=name,
            email=email,
            password=password,
            role="student",
            face_embedding=face_embedding,
            voice_embedding=voice_embedding
        )

        if not result["success"]:
            return {"success": False, "message": result.get("message", "Registration failed.")}

        # 7. Send verification email
        email_result = send_verification_email(email, name, token)
        
        if email_result.get("success"):
            return {
                "success": True,
                "message": "Student registration saved! Check your email to verify and complete registration.",
                "data": {}
            }
        else:
            return {
                "success": False,
                "message": f"Registration saved, but failed to send verification email: {email_result.get('message')}"
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
