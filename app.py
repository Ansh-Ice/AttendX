# pyrefly: ignore [missing-import]
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
# pyrefly: ignore [missing-import]
from extra_streamlit_components import CookieManager


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
    cookie_manager = CookieManager()
    st.session_state['cookie_manager'] = cookie_manager
    
    init_state()

    # 3. RESTORE SESSION ON APP LOAD
    user_id = cookie_manager.get("user_id")
    role = cookie_manager.get("role")
    is_logged_in = cookie_manager.get("is_logged_in")

    if is_logged_in == "true" and not st.session_state.get("logged_in") and user_id:
        try:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = int(user_id)
            st.session_state['user_role'] = role
            
            # Fetch profile
            from src.database.db import get_teacher_by_user_id, get_student_by_user_id
            if role == "teacher":
                profile = get_teacher_by_user_id(int(user_id))
            elif role == "student":
                profile = get_student_by_user_id(int(user_id))
            else:
                profile = None
                
            st.session_state['profile'] = profile
            st.session_state['username'] = profile['name'] if profile else "User"
            
            if st.session_state['page'] in ('home', 'login', 'register_student', 'register_teacher'):
                st.session_state['page'] = f"{role}_dashboard"
        except Exception:
            # If cookies are invalid, force login by doing nothing
            pass

    # Handle auto-enroll via URL
    join_code = st.query_params.get("join-code")
    if join_code:
        if not st.session_state.get('logged_in'):
            # User is not logged in in this session. Redirect to login instead of registration.
            st.session_state['page'] = 'login'
            st.session_state['pending_join_code'] = join_code
            if "join-code" in st.query_params:
                del st.query_params["join-code"]
        elif st.session_state.get('user_role') == 'student':
            st.session_state['pending_join_code'] = join_code
            if "join-code" in st.query_params:
                del st.query_params["join-code"]

    # Handle email verification via URL
    verify_token_param = st.query_params.get("verify-token")
    if verify_token_param:
        from src.database.db import verify_and_commit_registration
        result = verify_and_commit_registration(verify_token_param)
        if result.get("success"):
            st.session_state['verification_status'] = 'success'
        else:
            st.session_state['verification_status'] = 'failed'
            st.session_state['verification_message'] = result.get('message', 'Verification failed.')
        if "verify-token" in st.query_params:
            del st.query_params["verify-token"]

    # Show verification status banner if just verified
    verification_status = st.session_state.pop('verification_status', None)
    if verification_status == 'success':
        st.success("✅ Email verified successfully! You can now log in.")
        st.session_state['page'] = 'login'
    elif verification_status == 'failed':
        msg = st.session_state.pop('verification_message', 'Verification failed.')
        st.error(f"❌ {msg}")

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