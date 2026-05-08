import streamlit as st
from src.ui.styles import apply_custom_css
from src.database.auth import signup
import numpy as np
from PIL import Image


def register_screen():
    apply_custom_css()

    page = st.session_state.get('page', 'register_student')
    is_student = page == 'register_student'
    role = "student" if is_student else "teacher"
    role_label = "Student" if is_student else "Teacher"
    icon = "🎓" if is_student else "👨‍🏫"

    # Back to home — top-left
    b1, _, _ = st.columns([1, 3, 1])
    with b1:
        if st.button("← Home", key="reg_back_home"):
            st.session_state['page'] = 'home'
            st.rerun()

    # --- Centered register form ---
    _, center, _ = st.columns([1.2, 2, 1.2])

    with center:
        st.markdown(f"""
            <div class="auth-header animate-in">
                <div class="auth-icon">{icon}</div>
                <h2 class="auth-title">{role_label} Registration</h2>
                <p class="auth-subtitle">Create your AttendX {role_label.lower()} account</p>
            </div>
        """, unsafe_allow_html=True)

        # Full Name
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">Full Name</p>', unsafe_allow_html=True)
        name = st.text_input(
            "Name",
            placeholder="Enter your full name",
            label_visibility="collapsed",
            key="reg_name"
        )

        # Email
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Email</p>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            label_visibility="collapsed",
            key="reg_email"
        )

        # Password
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Password</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password (min 6 characters)",
            label_visibility="collapsed",
            key="reg_password"
        )

        # Confirm Password
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Confirm Password</p>', unsafe_allow_html=True)
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            label_visibility="collapsed",
            key="reg_confirm_password"
        )

        st.write("")

        # Submit button
        if st.button(f"Create {role_label} Account  →", key="btn_register", use_container_width=True, type="primary"):
            with st.spinner("Creating your account..."):
                result = signup(name, email, password, confirm_password, role)

            if result["success"]:
                st.success(result["message"])
                # Auto-login after successful registration
                # Re-authenticate to get user_id properly
                from src.database.auth import login as auth_login
                login_result = auth_login(email, password)

                if login_result["success"]:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = login_result['user_id']
                    st.session_state['user_role'] = login_result['role']
                    st.session_state['profile'] = login_result['profile']
                    st.session_state['username'] = name
                    st.session_state['page'] = 'student_dashboard' if is_student else 'teacher_dashboard'
                    st.session_state['transition'] = True
                    st.rerun()
                else:
                    # Registration succeeded but auto-login failed — send to login page
                    st.info("Account created! Please sign in.")
                    st.session_state['page'] = 'login'
                    st.rerun()
            else:
                st.error(result["message"])

        # Link to login
        st.write("")
        st.markdown("""
            <div style="text-align: center; margin-top: 0.5rem;">
                <p style="color: #999; font-size: 0.88rem;">
                    Already have an account?
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Sign In Instead", key="reg_to_login", use_container_width=True):
            st.session_state['page'] = 'login'
            st.rerun()
