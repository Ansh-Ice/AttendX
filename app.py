import streamlit as st

st.set_page_config(
    page_title="AttendX - AI Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from src.screens.home_screen import home_screen
from src.screens.login_screen import login_screen
from src.screens.register_screen import register_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen

def init_state():
    defaults = {
        'page': 'home',           # home | login | register_student | register_teacher | student_dashboard | teacher_dashboard
        'logged_in': False,
        'user_role': None,        # student | teacher | admin
        'user_id': None,          # user_id from users table
        'username': None,         # display name
        'profile': None,          # full profile dict from teachers/students table
        'transition': False,      # triggers fade animation on page change
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def navigate(page):
    """Set transition flag then switch page."""
    st.session_state['transition'] = True
    st.session_state['page'] = page

def main():
    init_state()

    page = st.session_state['page']

    if page == 'home':
        home_screen()
    elif page == 'login':
        login_screen()
    elif page in ('register_student', 'register_teacher'):
        register_screen()
    elif page == 'student_dashboard':
        student_screen()
    elif page == 'teacher_dashboard':
        teacher_screen()
    else:
        home_screen()

main()