import streamlit as st
import time
from src.database.auth import commit_signup, commit_student_signup, login as auth_login
from src.pipelines.face_pipeline import train_classifier

@st.dialog("Verify Your Email")
def otp_verify_dialog():
    st.markdown("### Enter Verification Code")
    st.write("We just sent a 6-digit code to your email. Please enter it below to complete registration.")
    
    # Check if we have pending data
    if 'pending_registration_data' not in st.session_state:
        st.error("No pending registration found. Please close and try again.")
        return
        
    pending = st.session_state['pending_registration_data']
    
    code = st.text_input("6-Digit Code", max_chars=6, key="otp_input")
    
    if st.button("Verify & Create Account", type="primary", width="stretch"):
        if code == pending['otp']:
            st.success("✅ Code verified!")
            
            with st.spinner("Creating your account..."):
                role = pending['role']
                is_student = (role == "student")
                
                if is_student:
                    result = commit_student_signup(
                        name=pending['name'],
                        email=pending['email'],
                        password=pending['password'],
                        face_embedding=pending['face_embedding'],
                        voice_embedding=pending['voice_embedding']
                    )
                else:
                    result = commit_signup(
                        name=pending['name'],
                        email=pending['email'],
                        password=pending['password'],
                        role=role
                    )
                    
                if result["success"]:
                    if is_student:
                        with st.spinner("Training classifiers..."):
                            train_classifier()
                            
                    # Auto login
                    login_result = auth_login(pending['email'], pending['password'])
                    if login_result["success"]:
                        # Cleanup
                        for key in ['reg_face_embedding', 'reg_voice_embedding', 'pending_registration_data', 'show_otp_dialog']:
                            st.session_state.pop(key, None)
                            
                        cookie_manager = st.session_state.get('cookie_manager')
                        if cookie_manager:
                            cookie_manager.set("user_id", str(login_result['user_id']), key="reg_set_user_id_otp")
                            cookie_manager.set("role", login_result['role'], key="reg_set_role_otp")
                            cookie_manager.set("is_logged_in", "true", key="reg_set_logged_in_otp")
                            
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = login_result['user_id']
                        st.session_state['user_role'] = login_result['role']
                        st.session_state['profile'] = login_result['profile']
                        st.session_state['username'] = pending['name']
                        st.session_state['page'] = 'student_dashboard' if is_student else 'teacher_dashboard'
                        st.session_state['transition'] = True
                        st.rerun()
                    else:
                        st.error("Account created, but failed to auto-login. Please refresh.")
                else:
                    st.error(result["message"])
        else:
            st.error("❌ Incorrect code. Please try again.")

    if st.button("Cancel", key="otp_cancel"):
        st.session_state['show_otp_dialog'] = False
        st.rerun()
