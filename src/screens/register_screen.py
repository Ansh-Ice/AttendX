import streamlit as st
from src.ui.styles import apply_custom_css

def register_screen():
    apply_custom_css()

    page = st.session_state.get('page', 'register_student')
    is_student = page == 'register_student'
    role_label = "Student" if is_student else "Teacher"
    icon = "🎓" if is_student else "👨‍🏫"

    # No navbar — just a back button at the top
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

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">Full Name</p>', unsafe_allow_html=True)
        name = st.text_input(
            "Name",
            placeholder="Enter your full name",
            label_visibility="collapsed",
            key="reg_name"
        )

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Username</p>', unsafe_allow_html=True)
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            label_visibility="collapsed",
            key="reg_username"
        )

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Password</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            label_visibility="collapsed",
            key="reg_password"
        )

        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Confirm Password</p>', unsafe_allow_html=True)
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            label_visibility="collapsed",
            key="reg_confirm_password"
        )

        st.write("")

        if st.button(f"Create {role_label} Account  →", key="btn_register", use_container_width=True, type="primary"):
            if not all([name, username, password, confirm_password]):
                st.warning("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # UI only — backend logic to be added later
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['user_role'] = 'student' if is_student else 'teacher'
                st.session_state['page'] = 'student_dashboard' if is_student else 'teacher_dashboard'
                st.session_state['transition'] = True
                st.success("Account created successfully! Redirecting...")
                st.rerun()

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
