import streamlit as st
import base64
import os

def _b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def header_home():
    """Full navbar built with st.columns, wrapped in .navbar-row for vertical centering."""
    logo_path = os.path.join("src", "assets", "logo_light.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("src", "assets", "logo.png")

    try:
        img_src = f"data:image/png;base64,{_b64(logo_path)}"
    except Exception:
        img_src = ""

    logged_in = st.session_state.get('logged_in', False)

    # Wrap in .navbar-row so CSS can force vertical centering on the columns
    st.markdown('<div class="navbar-row">', unsafe_allow_html=True)

    logo_col, links_col, btn_col, theme_col = st.columns([2, 4, 1.2, 1])

    with logo_col:
        st.markdown(f"""
            <div class="nav-logo">
                <img src="{img_src}" alt="AttendX">
            </div>
        """, unsafe_allow_html=True)

    with links_col:
        st.markdown("""
            <div class="nav-links-inline">
                <a href="#" class="nav-link active">Home</a>
                <a href="#" class="nav-link">Features</a>
                <a href="#" class="nav-link">Contact</a>
            </div>
        """, unsafe_allow_html=True)

    with btn_col:
        if logged_in:
            if st.button("Logout", key="nav_logout_btn", use_container_width=True):
                for key in ['logged_in', 'user_role', 'user_id', 'username', 'profile']:
                    st.session_state[key] = False if key == 'logged_in' else None
                st.session_state['page'] = 'home'
                st.rerun()
        else:
            if st.button("Login", key="nav_login_btn", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()

    with theme_col:
        st.markdown("""
            <div class="nav-toggle">
                <div class="toggle-icon">☀️</div>
                <div class="toggle-icon">🌙</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Subtle divider
    st.markdown('<hr style="margin: 0 0 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)