"""
teacher_screen.py — Premium Teacher Dashboard for AttendX.

Features:
    - Custom dashboard header with logo + logout
    - Sidebar navigation (Take Attendance, Manage Subjects, Attendance Records)
    - Reusable card components with icons, descriptions, and action buttons
    - Fully styled with the dark + gold theme
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import base64
import os
from src.ui.styles import apply_custom_css
from src.components.footer import render_footer
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_take_attendance import take_attendance_dialog
from src.components.dialog_voice_attendance import take_voice_attendance_dialog
from src.components.dialog_view_session import view_session_dialog
from src.database.db import (
    get_teacher_by_user_id,
    create_subject,
    get_teacher_subjects,
    delete_subject,
    get_teacher_attendance_sessions,
    get_subject_students,
    get_subject_class_count
)
from datetime import datetime
import pytz


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
    """Extra CSS specific to dashboard pages — layered on top of the global styles."""
    st.markdown("""
        <style>
            /* Tabs styling */
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

            /* Dashboard header */
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

            /* Dashboard cards */
            .dash-card {
                background: #1A1A1A;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 2rem 1.8rem;
                transition: all 0.35s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
            }
            .dash-card:hover {
                border-color: rgba(212, 175, 55, 0.3);
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(212, 175, 55, 0.08);
            }
            .dash-card-icon {
                width: 56px;
                height: 56px;
                border-radius: 14px;
                background: rgba(212, 175, 55, 0.08);
                border: 1px solid rgba(212, 175, 55, 0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                margin-bottom: 1.2rem;
                transition: all 0.3s ease;
            }
            .dash-card:hover .dash-card-icon {
                background: rgba(212, 175, 55, 0.15);
                border-color: rgba(212, 175, 55, 0.4);
                box-shadow: 0 0 20px rgba(212, 175, 55, 0.12);
            }
            .dash-card-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.15rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.5rem;
            }
            .dash-card-desc {
                font-size: 0.88rem;
                color: #999;
                line-height: 1.6;
                margin-bottom: 1.5rem;
                flex: 1;
            }

            /* Welcome banner */
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

            /* Stats row */
            .stat-card {
                background: #141414;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
                padding: 1.4rem 1.6rem;
                text-align: center;
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                border-color: rgba(212, 175, 55, 0.2);
            }
            .stat-value {
                font-family: 'Poppins', sans-serif;
                font-size: 1.8rem;
                font-weight: 800;
                color: #D4AF37;
                margin-bottom: 0.2rem;
            }
            .stat-label {
                font-size: 0.8rem;
                color: #999;
                font-weight: 500;
                letter-spacing: 0.05em;
            }

            /* Section label */
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

            /* Animation */
            .dash-animate {
                animation: fadeInUp 0.6s ease-out forwards;
                opacity: 0;
            }
            .dash-animate:nth-child(1) { animation-delay: 0.05s; }
            .dash-animate:nth-child(2) { animation-delay: 0.12s; }
            .dash-animate:nth-child(3) { animation-delay: 0.19s; }
        </style>
    """, unsafe_allow_html=True)


# ----------------------------
# REUSABLE COMPONENTS
# ----------------------------

def render_dashboard_header():
    """Dashboard-specific header: Logo | Title | Logout."""
    logo_src = _get_logo_src()
    username = st.session_state.get('username', 'Teacher')

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
                <span>Teacher</span> Dashboard — {username}
            </div>
        """, unsafe_allow_html=True)

    with col_logout:
        if st.button("🚪 Logout", key="dash_logout", width="stretch"):
            cookie_manager = st.session_state.get('cookie_manager')
            if cookie_manager:
                for c, k in [("user_id", "del_user_id_t"), ("role", "del_role_t"), ("is_logged_in", "del_logged_in_t")]:
                    try:
                        cookie_manager.delete(c, key=k)
                    except KeyError:
                        pass

            st.session_state.clear()
            st.session_state['page'] = 'home'
            st.rerun()

    st.markdown('<hr style="margin: 0.5rem 0 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)


def render_welcome_banner():
    """Welcome banner with teacher name."""
    username = st.session_state.get('username', 'Teacher')
    st.markdown(f"""
        <div class="welcome-banner dash-animate">
            <div class="welcome-title">Welcome back, <span class="gold">{username}</span> 👋</div>
            <div class="welcome-subtitle">
                Manage your classes, track attendance with AI-powered face & voice recognition,
                and access real-time analytics — all from one place.
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_stat_card(value, label):
    """Renders a single stat metric card."""
    return f"""
        <div class="stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
    """


def render_card(icon, title, description):
    """Renders a styled dashboard card — the button is handled separately via st.button."""
    st.markdown(f"""
        <div class="dash-card dash-animate">
            <div class="dash-card-icon">{icon}</div>
            <div class="dash-card-title">{title}</div>
            <div class="dash-card-desc">{description}</div>
        </div>
    """, unsafe_allow_html=True)


# ----------------------------
# SECTION VIEWS
# ----------------------------

@st.dialog("Create Subject")
def create_subject_dialog(teacher_id):
    st.markdown("### Add New Subject")
    sub_code = st.text_input("Subject Code*")
    sub_name = st.text_input("Subject Name*")
    sub_sec = st.text_input("Section")
    
    if st.button("Submit", type="primary", width="stretch"):
        if not sub_code or not sub_name:
            st.error("Subject code and name are required.")
        else:
            res = create_subject(sub_code, sub_name, sub_sec, teacher_id)
            if res.get("success"):
                st.success("Subject created successfully.")
                st.rerun()
            else:
                st.error(res.get("message"))


def section_take_attendance(teacher_id):
    """Take Attendance section — camera + voice capture cards."""
    st.markdown('<div class="section-label">TAKE ATTENDANCE</div>', unsafe_allow_html=True)

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("Please create a subject first in the 'Manage Subjects' tab.")
        return

    subject_options = {f"{sub['subject_code']} - {sub['name']} (Section {sub.get('section', 'N/A')})": sub['subject_id'] for sub in subjects}
    selected_subject_key = st.selectbox("Select Subject", options=list(subject_options.keys()))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_card(
            icon="📸",
            title="Face Recognition",
            description="Capture a class photo and let AI identify present students using trained face embeddings. Fast, accurate, and proxy-proof."
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Face Attendance →", key="btn_face_attend", width="stretch", type="primary"):
            take_attendance_dialog(subject_options[selected_subject_key])

    with col2:
        render_card(
            icon="🎙️",
            title="Voice Recognition",
            description="Record a class audio session to identify students by their voice prints. Perfect for roll-call scenarios with AI verification."
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Voice Attendance →", key="btn_voice_attend", width="stretch", type="primary"):
            take_voice_attendance_dialog(subject_options[selected_subject_key])


def section_manage_subjects(teacher_id):
    """Manage Subjects section."""
    st.markdown('<div class="section-label">MANAGE SUBJECTS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### Your Subjects")
        if st.button("➕ Create Subject", type="primary"):
            create_subject_dialog(teacher_id)
            
        st.markdown("<br>", unsafe_allow_html=True)
        subjects = get_teacher_subjects(teacher_id)
        
        if not subjects:
            st.info("No subjects found. Create one to get started.")
        else:
            for sub in subjects:
                with st.container(border=True):
                    # Fetch stats
                    students = get_subject_students(sub['subject_id'])
                    student_count = len(students)
                    classes_count = get_subject_class_count(sub['subject_id'])
                    
                    c_info, c_share, c_del = st.columns([6, 1, 1])
                    
                    with c_info:
                        st.markdown(f"**{sub.get('subject_code', '')} - {sub.get('name', '')}**")
                        st.caption(f"Section {sub.get('section', 'N/A')} &nbsp;•&nbsp; 👥 {student_count} Students &nbsp;•&nbsp; 📚 {classes_count} Classes")
                    
                    with c_share:
                        if st.button("", icon=":material/send:", key=f"share_{sub['subject_id']}", help="Share Subject Link", width="stretch"):
                            share_subject_dialog(sub.get('name', ''), sub.get('section', ''), sub.get('join_code', ''))
                    
                    with c_del:
                        if st.button("", icon=":material/delete:", key=f"del_{sub['subject_id']}", help="Delete Subject", width="stretch"):
                            res = delete_subject(sub['subject_id'])
                            if res.get("success"):
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error(res.get("message"))

    with col2:
        render_card(
            icon="👥",
            title="Student Roster",
            description="View enrolled students across your subjects. See their registration status, biometric enrollment, and attendance summary."
        )
        if st.button("View Students →", key="btn_view_students", width="stretch", type="primary"):
            st.info("👥 Student roster module coming soon!")


def section_attendance_records(teacher_id):
    """Attendance Records section — display sessions grouped by timestamp."""
    st.markdown('<div class="section-label">ATTENDANCE RECORDS</div>', unsafe_allow_html=True)
    
    # Add CSS for session cards
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,500,0,0');

            .attendance-log-row {
                margin-bottom: 1rem;
            }
            .session-card {
                background:
                    radial-gradient(circle at top left, rgba(212, 175, 55, 0.10), transparent 34%),
                    linear-gradient(135deg, rgba(26, 26, 26, 0.98), rgba(20, 20, 20, 0.94));
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 18px;
                padding: 1.35rem 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .session-card:hover {
                border-color: rgba(212, 175, 55, 0.3);
                box-shadow: 0 14px 32px rgba(212, 175, 55, 0.10);
                transform: translateY(-2px);
            }
            .session-card::after {
                content: '';
                position: absolute;
                inset: auto -35px -35px auto;
                width: 120px;
                height: 120px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(212, 175, 55, 0.10), transparent 65%);
                pointer-events: none;
            }
            .session-card-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1.5rem;
                flex-wrap: wrap;
            }
            .session-card-info {
                flex: 1;
                min-width: 250px;
            }
            .session-card-subject {
                font-family: 'Poppins', sans-serif;
                font-size: 1.1rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.7rem;
            }
            .session-card-meta {
                font-size: 0.85rem;
                color: #999;
                display: flex;
                gap: 0.75rem;
                flex-wrap: wrap;
            }
            .session-card-meta-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.42rem 0.7rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.06);
                color: #bdbdbd;
            }
            .material-symbols-rounded {
                font-family: 'Material Symbols Rounded';
                font-weight: normal;
                font-style: normal;
                font-size: 1rem;
                line-height: 1;
                letter-spacing: normal;
                text-transform: none;
                display: inline-block;
                white-space: nowrap;
                word-wrap: normal;
                direction: ltr;
                -webkit-font-smoothing: antialiased;
            }
            .session-card-stats {
                display: flex;
                gap: 1rem;
                align-items: center;
                flex-wrap: wrap;
            }
            .session-stat {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                min-width: 72px;
            }
            .session-stat-value {
                font-size: 1.4rem;
                font-weight: 800;
                line-height: 1;
                margin-bottom: 0.2rem;
            }
            .session-stat-value-present {
                color: #4ade80;
            }
            .session-stat-value-absent {
                color: #f87171;
            }
            .session-stat-value-total {
                color: #D4AF37;
            }
            .session-stat-label {
                font-size: 0.65rem;
                color: #999;
                font-weight: 600;
                letter-spacing: 0.05em;
            }
            .session-card-hint {
                margin-top: 0.9rem;
                font-size: 0.78rem;
                color: rgba(212, 175, 55, 0.82);
                letter-spacing: 0.04em;
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
            }
            @media (max-width: 768px) {
                .session-card {
                    padding: 1.15rem 1.1rem;
                }
                .session-card-content {
                    gap: 1rem;
                }
                .session-card-meta {
                    gap: 0.55rem;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    sessions = get_teacher_attendance_sessions(teacher_id)
    
    if not sessions:
        st.info("No attendance records found. Start taking attendance to see sessions here.")
        return
    
    # Helper function to convert UTC to IST
    def convert_to_ist(iso_timestamp):
        """Convert ISO UTC timestamp to IST."""
        try:
            utc_dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            ist = pytz.timezone('Asia/Kolkata')
            ist_dt = utc_dt.astimezone(ist)
            return ist_dt.strftime('%Y-%m-%d'), ist_dt.strftime('%H:%M:%S')
        except:
            return iso_timestamp[:10], iso_timestamp[11:19]
    
    # Display sessions
    for session in sessions:
        timestamp = session['timestamp']
        ist_date, ist_time = convert_to_ist(timestamp)
        subject = session['subject_name']
        section = session['section']
        present = session['present']
        absent = session['absent']
        total = present + absent

        card_col, action_col = st.columns([5.6, 1.4], gap="medium")

        with card_col:
            st.markdown(f"""
                <div class="attendance-log-row">
                    <div class="session-card">
                        <div class="session-card-content">
                            <div class="session-card-info">
                                <div class="session-card-subject">{subject}</div>
                                <div class="session-card-meta">
                                    <span class="session-card-meta-badge">
                                        <span class="material-symbols-rounded">calendar_month</span>
                                        {ist_date}
                                    </span>
                                    <span class="session-card-meta-badge">
                                        <span class="material-symbols-rounded">schedule</span>
                                        {ist_time}
                                    </span>
                                    <span class="session-card-meta-badge">
                                        <span class="material-symbols-rounded">groups</span>
                                        Section {section}
                                    </span>
                                </div>
                                <div class="session-card-hint">
                                    <span class="material-symbols-rounded">visibility</span>
                                    Open the detailed attendance view
                                </div>
                            </div>
                            <div class="session-card-stats">
                                <div class="session-stat">
                                    <div class="session-stat-value session-stat-value-present">{present}</div>
                                    <div class="session-stat-label">PRESENT</div>
                                </div>
                                <div style="width: 1px; height: 45px; background: rgba(255,255,255,0.1);"></div>
                                <div class="session-stat">
                                    <div class="session-stat-value session-stat-value-absent">{absent}</div>
                                    <div class="session-stat-label">ABSENT</div>
                                </div>
                                <div style="width: 1px; height: 45px; background: rgba(255,255,255,0.1);"></div>
                                <div class="session-stat">
                                    <div class="session-stat-value session-stat-value-total">{total}</div>
                                    <div class="session-stat-label">TOTAL</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with action_col:
            st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)
            if st.button(
                "View Details",
                key=f"view_{timestamp}",
                icon=":material/visibility:",
                help="Open detailed attendance dialog",
                width="stretch",
                type="primary",
            ):
                view_session_dialog(teacher_id, timestamp)


# ----------------------------
# MAIN SCREEN
# ----------------------------

def teacher_screen():
    apply_custom_css()
    _apply_dashboard_css()

    # --- Session guard ---
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Please login first to access the dashboard.")
        st.stop()

    if st.session_state.get('user_role') != 'teacher':
        st.error("🚫 Access denied. This dashboard is for teachers only.")
        st.stop()

    user_id = st.session_state.get('user_id')
    teacher_data = get_teacher_by_user_id(user_id)
    if not teacher_data:
        st.error("Teacher profile not found.")
        st.stop()
        
    teacher_id = teacher_data['teacher_id']

    # --- Dashboard header ---
    render_dashboard_header()

    # --- Welcome banner ---
    render_welcome_banner()

    # --- Quick stats row ---
    st.markdown('<div class="section-label">QUICK OVERVIEW</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    with s1:
        st.markdown(render_stat_card("—", "Total Classes"), unsafe_allow_html=True)
    with s2:
        st.markdown(render_stat_card("—", "Students"), unsafe_allow_html=True)
    with s3:
        st.markdown(render_stat_card("—", "Sessions Today"), unsafe_allow_html=True)
    with s4:
        st.markdown(render_stat_card("—", "Avg. Attendance"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Tabs for Navigation ---
    tab1, tab2, tab3 = st.tabs(["📸 Take Attendance", "📚 Manage Subjects", "📊 Attendance Records"])
    
    with tab1:
        section_take_attendance(teacher_id)
        
    with tab2:
        section_manage_subjects(teacher_id)
        
    with tab3:
        section_attendance_records(teacher_id)

    # --- Dashboard footer ---
    render_footer()
