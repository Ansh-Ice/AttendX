import streamlit as st
from src.ui.helpers import b64_encode
import os

def hero_section():
    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown("""
            <div style="padding-top: 2rem;" class="animate-in">
                <div class="hero-badge">AI-POWERED &nbsp;•&nbsp; SMART &nbsp;•&nbsp; SECURE</div>
                <div class="hero-heading">
                    Smart Attendance.<br>
                    <span class="gold-gradient">Smarter Future.</span>
                </div>
                <div class="hero-desc">
                    AttendX uses advanced Face Recognition and intelligent
                    analytics to make attendance tracking easier, faster,
                    and more reliable for everyone.
                </div>
            </div>
        """, unsafe_allow_html=True)

        btn1, btn2, _ = st.columns([1.2, 1, 1.5])
        with btn1:
            if st.button("Get Started  →", key="hero_get_started", type="primary"):
                st.session_state['page'] = 'login'
                st.rerun()
        with btn2:
            st.markdown('<a class="btn-outline" href="#about-this-website">Learn More</a>', unsafe_allow_html=True)

    with col2:
        icon_path = os.path.join("src", "assets", "logo_app_icon.png")
        try:
            img_src = f"data:image/png;base64,{b64_encode(icon_path)}"
            st.markdown(f"""
                <div class="hero-image-container animate-in">
                    <div class="hero-image-wrapper">
                        <div class="hero-image-inner">
                            <img src="{img_src}" alt="AttendX AI">
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.markdown("""
                <div class="hero-image-container" style="font-size: 7rem; color: var(--gold);">
                    🤖
                </div>
            """, unsafe_allow_html=True)
