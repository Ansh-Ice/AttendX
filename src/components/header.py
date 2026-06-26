import streamlit as st
from src.ui.helpers import get_logo_src

def header_home():
    """Full navbar built with st.columns, wrapped in .navbar-row for vertical centering."""
    img_src = get_logo_src("light")
    logged_in = st.session_state.get('logged_in', False)

    # Wrap in .navbar-row so CSS can force vertical centering on the columns
    st.markdown('<div class="navbar-row">', unsafe_allow_html=True)

    logo_col, links_col, btn_col = st.columns([2, 4, 1.5])

    with logo_col:
        st.markdown(f"""
            <div class="nav-logo">
                <img src="{img_src}" alt="AttendX">
            </div>
        """, unsafe_allow_html=True)

    with links_col:
        st.markdown("""
            <div class="nav-links-inline">
                <a href="#smart-attendance" class="nav-link active">Home</a>
                <a href="#about-this-website" class="nav-link">Features</a>
                <a href="#register-to-continue" class="nav-link">Register</a>
            </div>
        """, unsafe_allow_html=True)

    with btn_col:
        if logged_in:
            if st.button("Dashboard", key="nav_dash_btn", width="stretch"):
                role = st.session_state.get('user_role', 'student')
                st.session_state['page'] = f'{role}_dashboard'
                st.rerun()
        else:
            if st.button("Login", key="nav_login_btn", width="stretch"):
                st.session_state['page'] = 'login'
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Subtle divider
    st.markdown('<hr style="margin: 0 0 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)