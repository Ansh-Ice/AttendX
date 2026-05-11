import streamlit as st
from src.components.footer import render_footer

def student_screen():
    st.title("Student Dashboard")
    st.write("This is the student screen of the AttendX application.")
    st.write("Here you can view your attendance records, check class schedules, and more.")
    
    # --- Footer ---
    render_footer()