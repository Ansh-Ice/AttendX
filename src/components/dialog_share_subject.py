# pyrefly: ignore [missing-import]
import streamlit as st
import io
# pyrefly: ignore [missing-import]
import segno

BASE_URL = st.secrets.get("APP_BASE_URL", "https://attendx-046.streamlit.app")

@st.dialog("Share Class Link")
def share_subject_dialog(subject_name: str, section: str, join_code: str):
    final_link = f"{BASE_URL}/?join-code={join_code}"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Copy Link")
        st.markdown(f"**{subject_name} (Section {section})**")
        st.code(final_link, language=None)
        st.markdown("**Join Code**")
        st.code(join_code, language=None)
        st.caption("Copy this link to share via WhatsApp or Email")
        
    with col2:
        try:
            st.markdown("### Scan QR Code")
            qr = segno.make(final_link)
            out = io.BytesIO()
            qr.save(out, kind="png", scale=4)
            out.seek(0)
            st.image(out, caption=f"QR Code for {subject_name}", width="stretch")
        except Exception as e:
            st.error(f"Failed to generate QR code: {e}")
