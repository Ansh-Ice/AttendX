import streamlit as st

def render_footer():
    """Renders a common footer for all screens with some spacing before it."""
    st.markdown("""
        <style>
            .common-footer {
                margin-top: 4rem;
                padding: 1.5rem 0;
                border-top: 1px solid rgba(255,255,255,0.06);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            .common-footer-left {
                font-size: 0.75rem;
                color: #555;
                font-family: 'Inter', sans-serif;
            }
            .common-footer-right {
                font-size: 0.75rem;
                color: #444;
                font-family: 'Inter', sans-serif;
            }
            .common-footer-right span {
                color: #D4AF37;
            }
        </style>
        <div class="common-footer">
            <div class="common-footer-left">
                © 2026 AttendX · AI-Powered Attendance System
            </div>
            <div class="common-footer-right">
                Built with <span>♦</span> for Education
            </div>
        </div>
    """, unsafe_allow_html=True)
