import streamlit as st
import numpy as np
from PIL import Image

from src.ui.styles import apply_custom_css
from src.database.auth import signup, signup_student_with_biometrics, login as auth_login
from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.components.footer import render_footer


def register_screen():
    apply_custom_css()

    page = st.session_state.get('page', 'register_student')
    is_student = page == 'register_student'
    role = "student" if is_student else "teacher"
    role_label = "Student" if is_student else "Teacher"
    icon = "🎓" if is_student else "👨‍🏫"

    # Back to home — top-left
    b1, _, _ = st.columns([1, 3, 1])
    with b1:
        if st.button("← Home", key="reg_back_home"):
            st.session_state['page'] = 'home'
            st.rerun()

    # --- Centered register form ---
    _, center, _ = st.columns([1.2, 2, 1.2])

    with center:
        st.markdown(f"""
            <div class="auth-header animate-in">
                <div class="auth-icon">{icon}</div>
                <h2 class="auth-title">{role_label} Registration</h2>
                <p class="auth-subtitle">Create your AttendX {role_label.lower()} account</p>
            </div>
        """, unsafe_allow_html=True)

        # ---- FORM FIELDS ----

        # Full Name
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">Full Name</p>', unsafe_allow_html=True)
        name = st.text_input(
            "Name",
            placeholder="Enter your full name",
            label_visibility="collapsed",
            key="reg_name"
        )

        # Email
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Email</p>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            label_visibility="collapsed",
            key="reg_email"
        )

        # Password
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Password</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password (min 6 characters)",
            label_visibility="collapsed",
            key="reg_password"
        )

        # Confirm Password
        st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; margin-top: 1rem; font-family: Poppins, sans-serif;">Confirm Password</p>', unsafe_allow_html=True)
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            label_visibility="collapsed",
            key="reg_confirm_password"
        )

        # ---- BIOMETRIC CAPTURE (Students Only) ----
        if is_student:
            st.markdown("""
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
                    <p style="color: #D4AF37; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.15em; font-family: Poppins, sans-serif; margin-bottom: 1rem;">
                        BIOMETRIC VERIFICATION
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # --- FACE CAPTURE ---
            st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">📸 Face Capture</p>', unsafe_allow_html=True)
            st.caption("Position your face clearly in the center. Only one face should be visible.")

            photo_source = st.camera_input("Capture your face", key="reg_face_capture", label_visibility="collapsed")

            # Process face capture
            face_embedding = None
            if photo_source is not None:
                img = np.array(Image.open(photo_source))

                with st.spinner("Detecting face..."):
                    encodings = get_face_embeddings(img)

                if len(encodings) == 0:
                    st.error("❌ No face detected. Please try again with better lighting.")
                elif len(encodings) > 1:
                    st.error("❌ Multiple faces detected. Please ensure only your face is visible.")
                else:
                    face_embedding = encodings[0].tolist()
                    st.success("✅ Face captured successfully!")
                    # Store in session state so it persists across reruns
                    st.session_state['reg_face_embedding'] = face_embedding

            # Retrieve from session state if already captured
            if 'reg_face_embedding' in st.session_state and face_embedding is None:
                face_embedding = st.session_state['reg_face_embedding']
                st.info("✅ Face already captured.")

            st.write("")

            # --- VOICE CAPTURE ---
            st.markdown('<p style="color: #999; font-size: 0.85rem; margin-bottom: 0.3rem; font-family: Poppins, sans-serif;">🎙️ Voice Sample</p>', unsafe_allow_html=True)
            st.caption("Record a 5-10 second voice sample. Speak clearly: \"My name is [your name] and I am registering for AttendX.\"")

            audio_source = st.audio_input("Record your voice", key="reg_voice_capture", label_visibility="collapsed")

            # Process voice capture
            voice_embedding = None
            if audio_source is not None:
                audio_bytes = audio_source.getvalue()

                with st.spinner("Processing voice..."):
                    voice_embedding = get_voice_embedding(audio_bytes)

                if voice_embedding is None:
                    st.error("❌ Could not process audio. Please try again with a clearer recording.")
                else:
                    st.success("✅ Voice sample captured successfully!")
                    st.session_state['reg_voice_embedding'] = voice_embedding

            # Retrieve from session state if already captured
            if 'reg_voice_embedding' in st.session_state and voice_embedding is None:
                voice_embedding = st.session_state['reg_voice_embedding']
                st.info("✅ Voice already captured.")

            st.markdown('<div style="margin-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.06);"></div>', unsafe_allow_html=True)

        st.write("")

        # ---- SUBMIT ----
        if st.button(f"Create {role_label} Account  →", key="btn_register", use_container_width=True, type="primary"):
            with st.spinner("Creating your account..."):
                if is_student:
                    # Get embeddings from session state (in case they were captured before this rerun)
                    final_face = face_embedding or st.session_state.get('reg_face_embedding')
                    final_voice = voice_embedding or st.session_state.get('reg_voice_embedding')

                    result = signup_student_with_biometrics(
                        name=name,
                        email=email,
                        password=password,
                        confirm_password=confirm_password,
                        face_embedding=final_face,
                        voice_embedding=final_voice
                    )
                else:
                    # Teacher — no biometrics needed
                    result = signup(name, email, password, confirm_password, role)

            if result["success"]:
                st.success(result["message"])

                # Retrain face classifier with the new student's data
                if is_student:
                    with st.spinner("Training classifiers with your biometric data..."):
                        train_classifier()

                # Auto-login after registration
                login_result = auth_login(email, password)

                if login_result["success"]:
                    # Clean up biometric session state
                    for key in ['reg_face_embedding', 'reg_voice_embedding']:
                        st.session_state.pop(key, None)

                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = login_result['user_id']
                    st.session_state['user_role'] = login_result['role']
                    st.session_state['profile'] = login_result['profile']
                    st.session_state['username'] = name
                    st.session_state['page'] = 'student_dashboard' if is_student else 'teacher_dashboard'
                    st.session_state['transition'] = True
                    st.rerun()
                else:
                    st.info("Account created! Please sign in.")
                    st.session_state['page'] = 'login'
                    st.rerun()
            else:
                st.error(result["message"])

        # Link to login
        st.write("")
        st.markdown("""
            <div style="text-align: center; margin-top: 0.5rem;">
                <p style="color: #999; font-size: 0.88rem;">
                    Already have an account?
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Sign In Instead", key="reg_to_login", use_container_width=True):
            # Clean up biometric state on navigate away
            for key in ['reg_face_embedding', 'reg_voice_embedding']:
                st.session_state.pop(key, None)
            st.session_state['page'] = 'login'
            st.rerun()

    # --- Footer ---
    render_footer()
