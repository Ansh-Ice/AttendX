"""
helpers.py — Shared utility functions for AttendX UI.

Centralizes common operations like base64 encoding, logo loading, and timezone conversion
to eliminate code duplication across screens and components.
"""

import streamlit as st
import base64
import os
from datetime import datetime
import pytz


@st.cache_data
def b64_encode(path: str) -> str:
    """Read a file and return its base64-encoded string. Cached to avoid repeated disk I/O."""
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


@st.cache_data
def get_logo_src(variant: str = "light") -> str:
    """Get base64-encoded logo image source.
    
    Args:
        variant: 'light' for logo_light.png, 'flat' for logo_flat.png, etc.
    """
    logo_path = os.path.join("src", "assets", f"logo_{variant}.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("src", "assets", "logo.png")
    try:
        return f"data:image/png;base64,{b64_encode(logo_path)}"
    except Exception:
        return ""


def convert_to_ist(iso_timestamp: str) -> tuple[str, str]:
    """Convert ISO UTC timestamp to IST date and time strings.
    
    Returns:
        Tuple of (date_str, time_str) in 'YYYY-MM-DD' and 'HH:MM:SS' format.
    """
    try:
        utc_dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        ist = pytz.timezone('Asia/Kolkata')
        ist_dt = utc_dt.astimezone(ist)
        return ist_dt.strftime('%Y-%m-%d'), ist_dt.strftime('%H:%M:%S')
    except Exception:
        return iso_timestamp[:10], iso_timestamp[11:19] if len(iso_timestamp) > 19 else ""


def sanitize_html(text: str) -> str:
    """Sanitize user-supplied text before embedding in HTML to prevent XSS."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
