import streamlit as st
import base64
import os

def _b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def footer():
    logo_path = os.path.join("src", "assets", "logo_light.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("src", "assets", "logo.png")

    try:
        img_src = f"data:image/png;base64,{_b64(logo_path)}"
    except Exception:
        img_src = ""

    st.markdown(f"""
        <div class="site-footer">
            <div class="footer-logo">
                <img src="{img_src}" alt="AttendX">
            </div>
            <div class="footer-tagline">
                <span class="footer-tagline-icon">✅</span>
                <span>Built for Accuracy. Designed for Trust.<br>Empowering Education with AI.</span>
            </div>
            <div class="footer-socials">
                <a href="#" class="social-icon">f</a>
                <a href="#" class="social-icon">📷</a>
                <a href="#" class="social-icon">𝕏</a>
                <a href="#" class="social-icon">in</a>
            </div>
        </div>
    """, unsafe_allow_html=True)
