"""
teacher_screen.py — Premium Teacher Dashboard for AttendX.

Features:
    - Custom dashboard header with logo + logout
    - Sidebar navigation (Take Attendance, Manage Subjects, Attendance Records)
    - Reusable card components with icons, descriptions, and action buttons
    - Fully styled with the dark + gold theme
"""

import streamlit as st
import base64
import os
from src.ui.styles import apply_custom_css
from src.components.footer import render_footer


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
        if st.button("🚪 Logout", key="dash_logout", use_container_width=True):
            for key in ['logged_in', 'user_role', 'user_id', 'username', 'profile']:
                st.session_state[key] = False if key == 'logged_in' else None
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

def section_take_attendance():
    """Take Attendance section — camera + voice capture cards."""
    st.markdown('<div class="section-label">TAKE ATTENDANCE</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_card(
            icon="📸",
            title="Face Recognition",
            description="Capture a class photo and let AI identify present students using trained face embeddings. Fast, accurate, and proxy-proof."
        )
        if st.button("Start Face Attendance →", key="btn_face_attend", use_container_width=True, type="primary"):
            st.info("📸 Face attendance module coming soon!")

    with col2:
        render_card(
            icon="🎙️",
            title="Voice Recognition",
            description="Record a class audio session to identify students by their voice prints. Perfect for roll-call scenarios with AI verification."
        )
        if st.button("Start Voice Attendance →", key="btn_voice_attend", use_container_width=True, type="primary"):
            st.info("🎙️ Voice attendance module coming soon!")


def section_manage_subjects():
    """Manage Subjects section."""
    st.markdown('<div class="section-label">MANAGE SUBJECTS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_card(
            icon="📚",
            title="Your Subjects",
            description="View and manage the subjects you teach. Add new subjects, edit existing ones, or assign students to your courses."
        )
        if st.button("Manage Subjects →", key="btn_manage_subjects", use_container_width=True, type="primary"):
            st.info("📚 Subject management module coming soon!")

    with col2:
        render_card(
            icon="👥",
            title="Student Roster",
            description="View enrolled students across your subjects. See their registration status, biometric enrollment, and attendance summary."
        )
        if st.button("View Students →", key="btn_view_students", use_container_width=True, type="primary"):
            st.info("👥 Student roster module coming soon!")


def section_attendance_records():
    """Attendance Records section."""
    st.markdown('<div class="section-label">ATTENDANCE RECORDS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_card(
            icon="📊",
            title="Analytics & Reports",
            description="Access detailed attendance analytics — daily, weekly, monthly trends. Export reports as CSV or view interactive charts."
        )
        if st.button("View Analytics →", key="btn_view_analytics", use_container_width=True, type="primary"):
            st.info("📊 Analytics module coming soon!")

    with col2:
        render_card(
            icon="📋",
            title="Session History",
            description="Browse past attendance sessions. Review which students were present, absent, or marked via face/voice recognition."
        )
        if st.button("View History →", key="btn_view_history", use_container_width=True, type="primary"):
            st.info("📋 Session history module coming soon!")


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
        section_take_attendance()
        
    with tab2:
        section_manage_subjects()
        
    with tab3:
        section_attendance_records()

    # --- Dashboard footer ---
    render_footer()