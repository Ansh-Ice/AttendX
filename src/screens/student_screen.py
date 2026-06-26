"""
student_screen.py — Premium Student Dashboard for AttendX.

Features:
    - My Subjects (view & leave)
    - Join Subject via code
    - Attendance Records
    - Update Biometrics (face & voice re-registration)
"""

import streamlit as st
import numpy as np
from PIL import Image
from src.ui.styles import apply_custom_css
from src.ui.dashboard_styles import apply_dashboard_css
from src.ui.helpers import get_logo_src, sanitize_html
from src.components.footer import render_footer
from src.database.db import (
    get_student_by_user_id,
    get_student_subjects,
    join_subject,
    leave_subject,
    get_student_attendance,
    update_student_embeddings
)
from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding


# ----------------------------
# REUSABLE COMPONENTS
# ----------------------------

def render_dashboard_header():
    logo_src = get_logo_src("light")
    username = sanitize_html(st.session_state.get('username', 'Student'))

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
    username = sanitize_html(st.session_state.get('username', 'Student'))
    st.markdown(f"""
        <div class="welcome-banner dash-animate">
            <div class="welcome-title">Welcome back, <span class="gold">{username}</span> 👋</div>
            <div class="welcome-subtitle">
                View your enrolled subjects, track attendance records, and manage your biometric data.
            </div>
        </div>
    """, unsafe_allow_html=True)


# ----------------------------
# SECTION VIEWS
# ----------------------------

@st.dialog("Leave Subject")
def leave_subject_dialog(student_id: int, subject_id: int, subject_name: str):
    st.warning(f"Are you sure you want to leave **{sanitize_html(subject_name)}**?")
    
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


@st.dialog("Update Face Data")
def update_face_dialog(student_id: int):
    """Dialog to update face biometric data."""
    st.markdown("### Re-register Your Face")
    st.caption("Take a new photo to update your face embedding. Your attendance history will remain unchanged.")
    
    face_input_method = st.radio("Input Method", options=["Use Camera", "Upload Image"], horizontal=True, label_visibility="collapsed")
    
    photo_source = None
    if face_input_method == "Use Camera":
        photo_source = st.camera_input("Capture your face", key="update_face_capture", label_visibility="collapsed")
    else:
        photo_source = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="update_face_upload", label_visibility="collapsed")
    
    if photo_source is not None:
        # Validate file size (max 5MB)
        if len(photo_source.getvalue()) > 5 * 1024 * 1024:
            st.error("File too large. Maximum size is 5MB.")
            return
            
        img = np.array(Image.open(photo_source))
        
        with st.spinner("Detecting face..."):
            encodings = get_face_embeddings(img)
        
        if len(encodings) == 0:
            st.error("❌ No face detected. Please try again with better lighting.")
        elif len(encodings) > 1:
            st.error("❌ Multiple faces detected. Please ensure only your face is visible.")
        else:
            face_embedding = encodings[0].tolist()
            st.success("✅ Face detected successfully!")
            
            if st.button("Update Face Data", type="primary", width="stretch"):
                with st.spinner("Updating face embedding..."):
                    res = update_student_embeddings(
                        student_id=student_id,
                        face_embedding=face_embedding
                    )
                    if res.get("success"):
                        # Retrain the classifier with the updated embedding
                        train_classifier()
                        st.success("✅ Face data updated successfully! Your attendance history is preserved.")
                        st.rerun()
                    else:
                        st.error(f"Failed to update: {res.get('message')}")


@st.dialog("Update Voice Data")
def update_voice_dialog(student_id: int):
    """Dialog to update voice biometric data."""
    st.markdown("### Re-register Your Voice")
    st.caption('Record a 5-10 second voice sample. Speak clearly: "My name is [your name] and I am updating my voice for AttendX."')
    st.caption("Your attendance history will remain unchanged.")
    
    audio_source = st.audio_input("Record your voice", key="update_voice_capture", label_visibility="collapsed")
    
    if audio_source is not None:
        audio_bytes = audio_source.getvalue()
        
        # Validate file size (max 10MB)
        if len(audio_bytes) > 10 * 1024 * 1024:
            st.error("Recording too large. Maximum size is 10MB.")
            return
        
        with st.spinner("Processing voice..."):
            voice_embedding = get_voice_embedding(audio_bytes)
        
        if voice_embedding is None:
            st.error("❌ Could not process audio. Please try again with a clearer recording.")
        else:
            st.success("✅ Voice sample processed successfully!")
            
            if st.button("Update Voice Data", type="primary", width="stretch"):
                with st.spinner("Updating voice embedding..."):
                    res = update_student_embeddings(
                        student_id=student_id,
                        voice_embedding=voice_embedding
                    )
                    if res.get("success"):
                        st.success("✅ Voice data updated successfully! Your attendance history is preserved.")
                        st.rerun()
                    else:
                        st.error(f"Failed to update: {res.get('message')}")


def section_my_subjects(student_id: int):
    st.markdown('<div class="section-label">MY SUBJECTS</div>', unsafe_allow_html=True)
    
    subjects = get_student_subjects(student_id)
    if not subjects:
        st.info("You haven't joined any subjects yet. Use the 'Join Subject' tab to enroll.")
    else:
        for sub in subjects:
            with st.container(border=True):
                c_info, c_leave = st.columns([5, 1])
                with c_info:
                    st.markdown(f"**{sub.get('subject_code', '')} - {sub.get('name', '')}**")
                    st.caption(f"Section {sub.get('section', 'N/A')}")
                with c_leave:
                    if st.button("Leave", key=f"leave_{sub['subject_id']}", width="stretch"):
                        leave_subject_dialog(student_id, sub['subject_id'], sub.get('name', ''))


def section_join_subject(student_id: int):
    st.markdown('<div class="section-label">JOIN SUBJECT</div>', unsafe_allow_html=True)
    
    st.markdown("Got a join code from your teacher? Join the subject to start tracking your attendance.")
    if st.button("➕ Join New Subject", type="primary"):
        join_subject_dialog(student_id)


def section_attendance_records(student_id: int):
    st.markdown('<div class="section-label">ATTENDANCE RECORDS</div>', unsafe_allow_html=True)
    
    logs = get_student_attendance(student_id)
    if not logs:
        st.info("No attendance records found. Your records will appear here once your teachers take attendance.")
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


def section_update_biometrics(student_id: int, student_data: dict):
    """Section for updating face and voice biometric data."""
    st.markdown('<div class="section-label">UPDATE BIOMETRICS</div>', unsafe_allow_html=True)
    
    st.markdown("""
        Update your face or voice biometric data below. This is useful if your initial registration
        data has degraded or if you want to improve recognition accuracy.
        
        **Your attendance history will remain unchanged** — only the stored embeddings are replaced.
    """)
    
    # Show current biometric status
    has_face = bool(student_data.get('face_embedding'))
    has_voice = bool(student_data.get('voice_embedding'))
    
    st.markdown(f"""
        <div style="display: flex; gap: 2rem; margin: 1.5rem 0; flex-wrap: wrap;">
            <div style="background: #141414; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1.2rem 1.5rem; flex: 1; min-width: 200px;">
                <div style="font-size: 0.75rem; color: #999; letter-spacing: 0.1em; margin-bottom: 0.5rem;">FACE DATA</div>
                <div style="font-size: 1.1rem; color: {'#4ade80' if has_face else '#f87171'};">
                    {'✅ Registered' if has_face else '❌ Not Registered'}
                </div>
            </div>
            <div style="background: #141414; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1.2rem 1.5rem; flex: 1; min-width: 200px;">
                <div style="font-size: 0.75rem; color: #999; letter-spacing: 0.1em; margin-bottom: 0.5rem;">VOICE DATA</div>
                <div style="font-size: 1.1rem; color: {'#4ade80' if has_voice else '#f87171'};">
                    {'✅ Registered' if has_voice else '❌ Not Registered'}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if st.button("📸 Update Face Data", width="stretch", type="primary"):
            update_face_dialog(student_id)
    
    with col2:
        if st.button("🎙️ Update Voice Data", width="stretch", type="primary"):
            update_voice_dialog(student_id)


# ----------------------------
# MAIN SCREEN
# ----------------------------

def student_screen():
    apply_custom_css()
    apply_dashboard_css()

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

    tab1, tab2, tab3, tab4 = st.tabs(["📚 My Subjects", "➕ Join Subject", "📊 Attendance", "🔄 Update Biometrics"])
    
    with tab1:
        section_my_subjects(student_id)
        
    with tab2:
        section_join_subject(student_id)
        
    with tab3:
        section_attendance_records(student_id)
    
    with tab4:
        section_update_biometrics(student_id, student_data)

    render_footer()