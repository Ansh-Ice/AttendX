"""
student_screen.py — Premium Student Dashboard for AttendX.
"""

import streamlit as st
import base64
import os
from src.ui.styles import apply_custom_css
from src.components.footer import render_footer
from src.database.db import (
    get_student_by_user_id,
    get_student_subjects,
    join_subject,
    leave_subject,
    get_student_attendance
)

# ----------------------------
# HELPERS
# ----------------------------

def _b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def _get_logo_src():
    logo_path = os.path.join("src", "assets", "logo_light.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("src", "assets", "logo.png")
    try:
        return f"data:image/png;base64,{_b64(logo_path)}"
    except Exception:
        return ""

# ----------------------------
# DASHBOARD CSS
# ----------------------------
def _apply_dashboard_css():
    st.markdown("""
        <style>
            /* Copying required CSS from teacher_screen.py */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0;
                width: 100%;
                background-color: transparent;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .stTabs [data-baseweb="tab"] {
                flex: 1;
                display: flex;
                justify-content: center;
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 4px 4px 0 0;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
                color: #999;
                font-family: 'Poppins', sans-serif;
                font-size: 0.95rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: #D4AF37;
            }
            .stTabs [aria-selected="true"] {
                color: #D4AF37 !important;
                border-bottom: 2px solid #D4AF37 !important;
                background-color: rgba(212, 175, 55, 0.05);
            }
            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 2rem;
            }

            .dash-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.6rem 0 1rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                margin-bottom: 2rem;
            }
            .dash-header-logo img {
                height: 48px;
                object-fit: contain;
            }
            .dash-header-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.1rem;
                font-weight: 600;
                color: #f0f0f0;
                letter-spacing: 0.03em;
            }
            .dash-header-title span {
                color: #D4AF37;
            }

            .welcome-banner {
                background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(212,175,55,0.02));
                border: 1px solid rgba(212, 175, 55, 0.15);
                border-radius: 16px;
                padding: 2rem 2.5rem;
                margin-bottom: 2rem;
            }
            .welcome-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.6rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.3rem;
            }
            .welcome-title .gold {
                background: linear-gradient(135deg, #D4AF37, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .welcome-subtitle {
                font-size: 0.95rem;
                color: #999;
                line-height: 1.6;
            }

            .section-label {
                font-family: 'Poppins', sans-serif;
                font-size: 0.8rem;
                font-weight: 700;
                color: #D4AF37;
                letter-spacing: 0.15em;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: center;
                gap: 0.7rem;
            }
            .section-label::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, rgba(212,175,55,0.3), transparent);
            }
        </style>
    """, unsafe_allow_html=True)


# ----------------------------
# REUSABLE COMPONENTS
# ----------------------------

def render_dashboard_header():
    logo_src = _get_logo_src()
    username = st.session_state.get('username', 'Student')

    col_logo, col_title, col_logout = st.columns([2, 5, 1.5])

    with col_logo:
        st.markdown(f"""
            <div class="dash-header-logo">
                <img src="{logo_src}" alt="AttendX">
            </div>
        """, unsafe_allow_html=True)

    with col_title:
        st.markdown(f"""
            <div class="dash-header-title">
                <span>Student</span> Dashboard — {username}
            </div>
        """, unsafe_allow_html=True)

    with col_logout:
        if st.button("🚪 Logout", key="dash_logout", width="stretch"):
            cookie_manager = st.session_state.get('cookie_manager')
            if cookie_manager:
                for c, k in [("user_id", "del_user_id"), ("role", "del_role"), ("is_logged_in", "del_logged_in")]:
                    try:
                        cookie_manager.delete(c, key=k)
                    except KeyError:
                        pass
                
            st.session_state.clear()
            st.session_state['page'] = 'home'
            st.rerun()

    st.markdown('<hr style="margin: 0.5rem 0 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)

def render_welcome_banner():
    username = st.session_state.get('username', 'Student')
    st.markdown(f"""
        <div class="welcome-banner dash-animate">
            <div class="welcome-title">Welcome back, <span class="gold">{username}</span> 👋</div>
            <div class="welcome-subtitle">
                View your enrolled subjects and track your attendance records.
            </div>
        </div>
    """, unsafe_allow_html=True)


# ----------------------------
# SECTION VIEWS
# ----------------------------

@st.dialog("Leave Subject")
def leave_subject_dialog(student_id: int, subject_id: int, subject_name: str):
    st.warning(f"Are you sure you want to leave **{subject_name}**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Leave", type="primary", width="stretch"):
            res = leave_subject(student_id, subject_id)
            if res.get("success"):
                st.success("Successfully left the subject.")
                st.rerun()
            else:
                st.error(res.get("message"))
    with col2:
        if st.button("Cancel", width="stretch"):
            st.rerun()


@st.dialog("Join Subject")
def join_subject_dialog(student_id: int):
    st.markdown("### Join a new subject")
    join_code = st.text_input("Enter Join Code*", placeholder="e.g. 7X9A2B")
    
    if st.button("Submit", type="primary", width="stretch"):
        if not join_code:
            st.error("Please enter a valid join code.")
        else:
            res = join_subject(student_id, join_code.strip())
            if res.get("success"):
                st.success(res.get("message"))
                st.rerun()
            else:
                st.error(res.get("message"))


def section_my_subjects(student_id: int):
    st.markdown('<div class="section-label">MY SUBJECTS</div>', unsafe_allow_html=True)
    
    subjects = get_student_subjects(student_id)
    if not subjects:
        st.info("You haven't joined any subjects yet.")
    else:
        for sub in subjects:
            with st.container():
                st.markdown(f"**{sub.get('subject_code', '')} - {sub.get('name', '')} (Section {sub.get('section', 'N/A')})**")
                
                if st.button("Leave", key=f"leave_{sub['subject_id']}"):
                    leave_subject_dialog(student_id, sub['subject_id'], sub.get('name', ''))
                    
                st.markdown("<hr style='margin:0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)


def section_join_subject(student_id: int):
    st.markdown('<div class="section-label">JOIN SUBJECT</div>', unsafe_allow_html=True)
    
    st.markdown("Got a join code from your teacher? Join the subject to start tracking your attendance.")
    if st.button("➕ Join New Subject", type="primary"):
        join_subject_dialog(student_id)


def section_attendance_records(student_id: int):
    st.markdown('<div class="section-label">ATTENDANCE RECORDS</div>', unsafe_allow_html=True)
    
    logs = get_student_attendance(student_id)
    if not logs:
        st.info("No attendance records found.")
    else:
        st.dataframe(
            logs,
            column_config={
                "subject_name": "Subject",
                "section": "Section",
                "timestamp": "Date",
                "is_present": "Status"
            },
            hide_index=True,
            width="stretch"
        )

# ----------------------------
# MAIN SCREEN
# ----------------------------

def student_screen():
    apply_custom_css()
    _apply_dashboard_css()

    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Access denied. Please login first.")
        st.stop()

    if st.session_state.get('user_role') != 'student':
        st.error("🚫 Access denied. This dashboard is for students only.")
        st.stop()

    user_id = st.session_state.get('user_id')
    student_data = get_student_by_user_id(user_id)
    if not student_data:
        st.error("Student profile not found.")
        st.stop()
        
    student_id = student_data['student_id']

    render_dashboard_header()
    render_welcome_banner()

    # Trigger auto-enroll dialog if URL param was captured
    if st.session_state.get('pending_join_code'):
        from src.components.dialog_auto_enroll import auto_enroll_dialog
        auto_enroll_dialog(st.session_state['pending_join_code'], student_id)

    tab1, tab2, tab3 = st.tabs(["📚 My Subjects", "➕ Join Subject", "📊 Attendance"])
    
    with tab1:
        section_my_subjects(student_id)
        
    with tab2:
        section_join_subject(student_id)
        
    with tab3:
        section_attendance_records(student_id)

    render_footer()