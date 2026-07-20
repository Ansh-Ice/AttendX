import streamlit as st
from src.ui.styles import apply_custom_css
from src.database.auth import login
from src.components.footer import render_footer


def login_screen():
    apply_custom_css()

    # Back to home — top-left
    b1, _, _ = st.columns([1, 3, 1])
    with b1:
        if st.button("← Home", key="login_back_home"):
            st.session_state['page'] = 'home'
            st.rerun()

    # --- Centered login form ---
    _, center, _ = st.columns([1.2, 2, 1.2])

    with center:
        st.markdown("""
            <div class="auth-header animate-in">
                <div class="auth-icon">🔐</div>
                <h2 class="auth-title">Welcome Back</h2>
                <p class="auth-subtitle">Sign in to your AttendX account</p>
            </div>
        """, unsafe_allow_html=True)

        # Email field
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">Email</p>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            label_visibility="collapsed",
            key="login_email"
        )

        # Password field
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Password</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            label_visibility="collapsed",
            key="login_password"
        )

        st.write("")

        # Sign In button
        if st.button("Sign In  →", key="btn_sign_in", width="stretch", type="primary"):
            if not email or not password:
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Signing in..."):
                    result = login(email, password)

                if result["success"]:
                    # Store in cookies
                    cookie_manager = st.session_state.get('cookie_manager')
                    if cookie_manager:
                        cookie_manager.set("user_id", str(result['user_id']), key="set_user_id")
                        cookie_manager.set("role", result['role'], key="set_role")
                        cookie_manager.set("is_logged_in", "true", key="set_logged_in")

                    # Store auth state
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = result['user_id']
                    st.session_state['user_role'] = result['role']
                    st.session_state['profile'] = result['profile']
                    st.session_state['username'] = result['profile']['name'] if result['profile'] else email

                    # Route to correct dashboard
                    if result['role'] == 'teacher':
                        st.session_state['page'] = 'teacher_dashboard'
                    elif result['role'] == 'student':
                        st.session_state['page'] = 'student_dashboard'
                    else:
                        st.session_state['page'] = 'home'

                    st.session_state['transition'] = True
                    st.rerun()
                elif result.get("message") == "EMAIL_NOT_VERIFIED":
                    st.error("📧 Your account is incomplete. Please register again to verify your email via OTP.")
                else:
                    st.error(result['message'])

        # Registration links
        st.write("")
        st.markdown("""
            <div style="text-align: center; margin-top: 0.5rem;">
                <p style="color: #999; font-size: 0.88rem;">
                    Don't have an account?
                </p>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Register as Student", key="login_to_reg_s", width="stretch"):
                st.session_state['page'] = 'register_student'
                st.rerun()
        with c2:
            if st.button("Register as Teacher", key="login_to_reg_t", width="stretch"):
                st.session_state['page'] = 'register_teacher'
                st.rerun()

    # --- Footer ---
    render_footer()
