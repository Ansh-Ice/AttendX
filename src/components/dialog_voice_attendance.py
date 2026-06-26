# pyrefly: ignore [missing-import]
import streamlit as st
import numpy as np
from src.database.db import get_subject_students, mark_attendance
from src.database.config import supabase
from src.pipelines.voice_pipeline import process_bulk_audio
from src.ui.helpers import sanitize_html

@st.dialog("Take Voice Attendance")
def take_voice_attendance_dialog(subject_id: int):
    st.markdown("### Voice Recognition Attendance")
    st.caption("Record class audio (up to 5 mins) or upload an audio file.")
    
    # Initialize session states scoped to this dialog
    if 'voice_results' not in st.session_state:
        st.session_state['voice_results'] = None
    if 'voice_audio_bytes' not in st.session_state:
        st.session_state['voice_audio_bytes'] = None
        
    students = get_subject_students(subject_id)
    if not students:
        st.warning("No students are enrolled in this subject yet.")
        return
        
    input_method = st.radio("Input Method", ["Record Audio", "Upload Audio"], horizontal=True, label_visibility="collapsed")
    
    if input_method == "Record Audio":
        audio_source = st.audio_input("Record class session", key="voice_audio_input", label_visibility="collapsed")
        if audio_source:
            if st.button("Use this Recording", width="stretch"):
                st.session_state['voice_audio_bytes'] = audio_source.getvalue()
                st.success("Recording loaded!")
    else:
        uploaded_file = st.file_uploader("Upload an audio file (.wav, .mp3)", type=["wav", "mp3"], label_visibility="collapsed")
        if uploaded_file:
            if st.button("Use this File", width="stretch"):
                st.session_state['voice_audio_bytes'] = uploaded_file.getvalue()
                st.success("File loaded!")
                
    if st.session_state['voice_audio_bytes']:
        st.audio(st.session_state['voice_audio_bytes'])
        if st.button("Clear Audio", width="stretch"):
            st.session_state['voice_audio_bytes'] = None
            st.rerun()

    st.write("")
    
    if st.button("Analyze Audio", width="stretch", type="primary", disabled=st.session_state['voice_audio_bytes'] is None):
        with st.spinner("Running AI voice recognition..."):
            student_ids = [s['student_id'] for s in students if s.get('student_id')]
            candidates_dict = {}
            if student_ids:
                try:
                    res = supabase.table('students').select('student_id, voice_embedding').in_('student_id', student_ids).execute()
                    candidates_dict = {r['student_id']: r['voice_embedding'] for r in res.data if r.get('voice_embedding')}
                except Exception as e:
                    st.error(f"Error fetching student voice prints: {e}")
                    return
            
            if not candidates_dict:
                st.warning("No voice prints found for students in this class.")
                return
                
            try:
                # process_bulk_audio returns {sid: score}
                identified_results = process_bulk_audio(st.session_state['voice_audio_bytes'], candidates_dict)
                
                # Map to results
                results = {}
                for student in students:
                    sid = student['student_id']
                    results[sid] = sid in identified_results
                    
                st.session_state['voice_results'] = results
            except Exception as e:
                st.error(f"Error processing audio: {e}")
            
    # Display Results & Confirm
    if st.session_state['voice_results'] is not None:
        st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown("#### Attendance Preview")
        results = st.session_state['voice_results']
        
        present_count = sum(1 for v in results.values() if v)
        absent_count = len(results) - present_count
        
        st.caption(f"✅ {present_count} Present  |  ❌ {absent_count} Absent")
        
        with st.container(border=True):
            for student in students:
                sid = student['student_id']
                name = sanitize_html(student.get('name', 'Unknown'))
                is_present = results[sid]
                
                if is_present:
                    st.markdown(f"<div style='color: #4ade80; margin-bottom: 0.3rem;'>✅ <b>{name}</b> (ID: {sid})</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: #f87171; margin-bottom: 0.3rem;'>❌ <b>{name}</b> (ID: {sid})</div>", unsafe_allow_html=True)
                
        st.write("")
        if st.button("Confirm & Save Attendance", width="stretch", type="primary"):
            with st.spinner("Saving records..."):
                res = mark_attendance(subject_id, results)
                if res.get("success"):
                    st.success("Attendance marked successfully!")
                    st.session_state['voice_results'] = None
                    st.session_state['voice_audio_bytes'] = None
                    st.rerun()
                else:
                    st.error(res.get("message"))
