import streamlit as st
from src.ui.styles import apply_custom_css
from src.components.header import header_home
from src.components.hero import hero_section
from src.components.login_cards import login_selection
from src.components.footer import footer

def home_screen():
    apply_custom_css()

    header_home()

    hero_section()

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    login_selection()

    footer()