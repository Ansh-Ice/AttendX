import streamlit as st
import numpy as np
from PIL import Image
from src.database.db import get_subject_students, mark_attendance
from src.pipelines.face_pipeline import predict_attendance
from src.ui.helpers import sanitize_html

@st.dialog("Take Attendance")
def take_attendance_dialog(subject_id: int):
    st.markdown("### Facial Recognition Attendance")
    
    # Initialize session states scoped to this dialog
    if 'attendance_results' not in st.session_state:
        st.session_state['attendance_results'] = None
    if 'attendance_images' not in st.session_state:
        st.session_state['attendance_images'] = []
        
    students = get_subject_students(subject_id)
    if not students:
        st.warning("No students are enrolled in this subject yet.")
        return
        
    # Option to select input method
    input_method = st.radio("Input Method", ["Use Camera", "Upload Images"], horizontal=True, label_visibility="collapsed")
    
    if input_method == "Use Camera":
        cam_source = st.camera_input("Capture class photo", key="cam_input", label_visibility="collapsed")
        if cam_source:
            if st.button("Add Photo to Batch", width="stretch"):
                st.session_state['attendance_images'].append(cam_source.getvalue())
                st.success("Photo added to batch!")
    else:
        uploaded_files = st.file_uploader("Upload class photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            if st.button("Add Photos to Batch", width="stretch"):
                for f in uploaded_files:
                    st.session_state['attendance_images'].append(f.getvalue())
                st.success(f"Added {len(uploaded_files)} photos to batch!")

    # Display accumulated images
    if st.session_state['attendance_images']:
        st.markdown(f"**Selected Photos ({len(st.session_state['attendance_images'])})**")
        cols = st.columns(4)
        for i, img_bytes in enumerate(st.session_state['attendance_images']):
            cols[i % 4].image(img_bytes, width="stretch")
            
        if st.button("Clear Batch", width="stretch"):
            st.session_state['attendance_images'] = []
            st.session_state['attendance_results'] = None
            st.rerun()

    st.write("")
    
    # Analyze Button
    if st.button("Analyze Photos", width="stretch", type="primary", disabled=len(st.session_state['attendance_images']) == 0):
        with st.spinner("Running AI face recognition..."):
            all_detected = {}
            from io import BytesIO
            for img_bytes in st.session_state['attendance_images']:
                try:
                    img = np.array(Image.open(BytesIO(img_bytes)).convert('RGB'))
                    detected, _, _ = predict_attendance(img)
                    all_detected.update(detected)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
            
            # Map detected faces to enrolled students
            results = {}
            for student in students:
                sid = student['student_id']
                results[sid] = all_detected.get(sid, False)
                
            st.session_state['attendance_results'] = results
            
    # Display Results & Confirm
    if st.session_state['attendance_results'] is not None:
        st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown("#### Attendance Preview")
        results = st.session_state['attendance_results']
        
        # Display students in a clean list
        present_count = sum(1 for v in results.values() if v)
        absent_count = len(results) - present_count
        
        st.caption(f"✅ {present_count} Present  |  ❌ {absent_count} Absent")
        
        with st.container(border=True):
            for student in students:
                sid = student['student_id']
                name = sanitize_html(student.get('name', 'Unknown'))
                is_present = results[sid]
                
                if is_present:
                    st.markdown(f"<div style='color: #4ade80; margin-bottom: 0.3rem;'>✅ <b>{name}</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: #f87171; margin-bottom: 0.3rem;'>❌ <b>{name}</b></div>", unsafe_allow_html=True)
                
        st.write("")
        if st.button("Confirm & Save Attendance", width="stretch", type="primary"):
            with st.spinner("Saving records..."):
                res = mark_attendance(subject_id, results)
                if res.get("success"):
                    st.success("Attendance marked successfully!")
                    st.session_state['attendance_results'] = None
                    st.session_state['attendance_images'] = []
                    st.rerun()
                else:
                    st.error(res.get("message"))
