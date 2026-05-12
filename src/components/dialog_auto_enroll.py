import streamlit as st
from src.database.db import get_subject_by_join_code, join_subject

@st.dialog("Auto Enroll")
def auto_enroll_dialog(join_code: str, student_id: int):
    subject = get_subject_by_join_code(join_code)
    if not subject:
        st.error("Invalid join code. The subject may not exist.")
        if st.button("Close"):
            st.session_state.pop('pending_join_code', None)
            st.rerun()
        return

    st.markdown(f"### {subject['name']}")
    st.markdown(f"**Section:** {subject['section']}")
    st.write("Do you want to join this class?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Join", type="primary", width="stretch"):
            res = join_subject(student_id, join_code)
            if res.get("success"):
                st.success("Successfully joined the class!")
                st.session_state.pop('pending_join_code', None)
                st.rerun()
            else:
                st.error(res.get("message"))
    with col2:
        if st.button("Cancel", width="stretch"):
            st.session_state.pop('pending_join_code', None)
            st.rerun()
