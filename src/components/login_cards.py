import streamlit as st
import base64
import os

def _b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def login_selection():
    """Registration cards — redirect to register_student / register_teacher pages."""
    st.markdown("""
        <div class="login-section-title">REGISTER TO CONTINUE</div>
    """, unsafe_allow_html=True)

    # Load illustrations
    student_path = os.path.join("src", "assets", "student.png")
    teacher_path = os.path.join("src", "assets", "teacher.png")

    try:
        student_src = f"data:image/png;base64,{_b64(student_path)}"
    except Exception:
        student_src = ""
    try:
        teacher_src = f"data:image/png;base64,{_b64(teacher_path)}"
    except Exception:
        teacher_src = ""

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
            <div class="login-card animate-in">
                <img src="{student_src}" alt="Student" class="login-card-img">
                <div class="login-card-content">
                    <div class="login-card-title">Student Registration</div>
                    <div class="login-card-desc">
                        Create your account to access attendance,
                        view reports, and track your academic journey.
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Register as Student  →", key="btn_reg_student", use_container_width=True):
            st.session_state['page'] = 'register_student'
            st.session_state['transition'] = True
            st.rerun()

    with col2:
        st.markdown(f"""
            <div class="login-card animate-in">
                <img src="{teacher_src}" alt="Teacher" class="login-card-img">
                <div class="login-card-content">
                    <div class="login-card-title">Teacher Registration</div>
                    <div class="login-card-desc">
                        Create your account to manage classes,
                        take attendance, and view analytics.
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Register as Teacher  →", key="btn_reg_teacher", use_container_width=True):
            st.session_state['page'] = 'register_teacher'
            st.session_state['transition'] = True
            st.rerun()
