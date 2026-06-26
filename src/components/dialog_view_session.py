"""
dialog_view_session.py — Session Details Dialog for AttendX.

Displays attendance details for a specific session with a clean, themed view.
"""

import streamlit as st
from src.database.db import get_session_details
from src.ui.helpers import convert_to_ist, sanitize_html


@st.dialog("Session Attendance Details")
def view_session_dialog(teacher_id: int, timestamp: str):
    """Dialog to view detailed attendance for a specific session."""
    
    session = get_session_details(teacher_id, timestamp)
    
    if not session:
        st.error("Failed to load session details.")
        return
    
    ist_date, ist_time = convert_to_ist(timestamp)
    
    # Header section
    st.markdown("""
        <style>
            .session-header {
                background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(212,175,55,0.02));
                border: 1px solid rgba(212, 175, 55, 0.15);
                border-radius: 12px;
                padding: 1.5rem 1.8rem;
                margin-bottom: 1.5rem;
            }
            .session-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.3rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.5rem;
            }
            .session-meta {
                display: flex;
                gap: 2rem;
                flex-wrap: wrap;
                margin-top: 1rem;
                font-size: 0.85rem;
                color: #999;
            }
            .session-meta-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .session-stats {
                display: flex;
                gap: 1.5rem;
                margin-top: 1.2rem;
                justify-content: flex-start;
                flex-wrap: wrap;
            }
            .stat-box {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
                padding: 1rem 1.5rem;
                text-align: center;
                min-width: 100px;
            }
            .stat-number {
                font-size: 1.8rem;
                font-weight: 800;
                margin-bottom: 0.3rem;
                line-height: 1;
            }
            .stat-number-present {
                color: #4ade80;
            }
            .stat-number-absent {
                color: #f87171;
            }
            .stat-number-total {
                color: #D4AF37;
            }
            .stat-label {
                font-size: 0.7rem;
                color: #999;
                font-weight: 600;
                letter-spacing: 0.05em;
            }
            .attendance-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.6rem;
                transition: all 0.2s ease;
            }
            .attendance-item:hover {
                border-color: rgba(212, 175, 55, 0.2);
                background: rgba(255,255,255,0.05);
            }
            .attendance-status {
                font-size: 1.3rem;
                min-width: 24px;
            }
            .attendance-name {
                flex: 1;
                font-weight: 500;
                color: #f0f0f0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="session-header">
            <div class="session-title">{session['subject_name']}</div>
            <div class="session-meta">
                <div class="session-meta-item">📅 {ist_date}</div>
                <div class="session-meta-item">🕐 {ist_time}</div>
                <div class="session-meta-item">📍 Section {session['section']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Attendance records section
    st.markdown("### Attendance Records")
    
    if session['records']:
        for record in session['records']:
            status_icon = "✅" if record['is_present'] else "❌"
            status_class = "stat-number-present" if record['is_present'] else "stat-number-absent"
            
            st.markdown(f"""
                <div class="attendance-item">
                    <div class="attendance-status">{status_icon}</div>
                    <div class="attendance-name">{record['student_name']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No attendance records found for this session.")
    
    st.markdown("<br>", unsafe_allow_html=True)
