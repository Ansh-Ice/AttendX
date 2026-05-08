import streamlit as st
import base64
import os

def _b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

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
            st.markdown('<a class="btn-gold" href="#">Explore Features &nbsp;&rarr;</a>', unsafe_allow_html=True)
        with btn2:
            st.markdown('<a class="btn-outline" href="#">Learn More</a>', unsafe_allow_html=True)

    with col2:
        icon_path = os.path.join("src", "assets", "logo_app_icon.png")
        try:
            img_src = f"data:image/png;base64,{_b64(icon_path)}"
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
