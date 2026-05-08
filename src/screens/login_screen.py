import streamlit as st
from src.ui.styles import apply_custom_css

def login_screen():
    apply_custom_css()

    # No navbar — just a back button at the top
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

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">Username</p>', unsafe_allow_html=True)
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            label_visibility="collapsed",
            key="login_username"
        )

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Password</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            label_visibility="collapsed",
            key="login_password"
        )

        st.write("")

        if st.button("Sign In  →", key="btn_sign_in", use_container_width=True, type="primary"):
            if username and password:
                # UI only — role will be fetched from Supabase later
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['user_role'] = 'student'
                st.session_state['page'] = 'student_dashboard'
                st.session_state['transition'] = True
                st.rerun()
            else:
                st.warning("Please fill in all fields.")

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
            if st.button("Register as Student", key="login_to_reg_s", use_container_width=True):
                st.session_state['page'] = 'register_student'
                st.rerun()
        with c2:
            if st.button("Register as Teacher", key="login_to_reg_t", use_container_width=True):
                st.session_state['page'] = 'register_teacher'
                st.rerun()
