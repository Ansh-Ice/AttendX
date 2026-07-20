import streamlit as st

def about_section():
    # --- About label + description (left) and 4 feature cards (right) in 2x2 ---
    left, right = st.columns([1, 2.5])

    with left:
        st.markdown("""
            <div id="about-this-website" class="about-text-panel animate-in">
                <div class="about-label">ABOUT THIS WEBSITE</div>
                <p>
                    AttendX is designed to help educational institutions and organizations
                    manage attendance with accuracy, transparency, and intelligence.<br><br>
                    It combines AI technology with real-time analytics to prevent proxy
                    attendance and empower data-driven decisions.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with right:
        # Row 1
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)

        with r1c1:
            st.markdown("""
                <div class="feature-card animate-in">
                    <div class="feature-icon">👤</div>
                    <div class="feature-title">Face Recognition</div>
                    <div class="feature-desc">Real-time face detection and recognition for accurate attendance.</div>
                </div>
            """, unsafe_allow_html=True)

        with r1c2:
            st.markdown("""
                <div class="feature-card animate-in">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Smart Analytics</div>
                    <div class="feature-desc">Powerful insights and reports to track attendance trends.</div>
                </div>
            """, unsafe_allow_html=True)

        with r1c3:
            st.markdown("""
                <div class="feature-card animate-in">
                    <div class="feature-icon">🛡️</div>
                    <div class="feature-title">Secure & Reliable</div>
                    <div class="feature-desc">Advanced security measures to prevent proxy and ensure trust.</div>
                </div>
            """, unsafe_allow_html=True)

        with r1c4:
            st.markdown("""
                <div class="feature-card animate-in">
                    <div class="feature-icon">👆</div>
                    <div class="feature-title">Easy to Use</div>
                    <div class="feature-desc">Intuitive interface for students, teachers, and administrators.</div>
                </div>
            """, unsafe_allow_html=True)

