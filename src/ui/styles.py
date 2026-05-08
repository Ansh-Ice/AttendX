import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

            /* ===== GLOBAL VARIABLES ===== */
            :root {
                --bg-primary: #0a0a0a;
                --bg-secondary: #111111;
                --bg-card: #141414;
                --bg-card-alt: #1a1a1a;
                --gold: #D4AF37;
                --gold-light: #FFD700;
                --gold-dark: #B8960C;
                --warm-gold: #e8c547;
                --text-primary: #f0f0f0;
                --text-secondary: #999999;
                --text-muted: #666666;
                --border: rgba(212, 175, 55, 0.15);
                --border-subtle: rgba(255, 255, 255, 0.06);
                --glow-gold: rgba(212, 175, 55, 0.15);
            }

            /* ===== GLOBAL RESET ===== */
            .stApp {
                background-color: var(--bg-primary) !important;
                font-family: 'Inter', sans-serif !important;
                color: var(--text-primary);
            }
            
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Poppins', sans-serif !important;
            }

            /* Kill Streamlit defaults */
            header[data-testid="stHeader"] { display: none !important; }
            footer { display: none !important; }
            #MainMenu { display: none !important; }

            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 0 !important;
                max-width: 1200px !important;
            }

            /* ===== NAVBAR ===== */
            .navbar-row {
                padding: 0.5rem 0 0.5rem 0;
            }
            /* Force ALL nested Streamlit containers to vertically center */
            .navbar-row [data-testid="stHorizontalBlock"] {
                align-items: center !important;
            }
            .navbar-row [data-testid="stVerticalBlock"] {
                gap: 0 !important;
                justify-content: center !important;
            }
            .navbar-row [data-testid="stColumn"] {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            .navbar-row [data-testid="stColumn"] > div {
                width: 100%;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            /* Keep logo left-aligned */
            .navbar-row [data-testid="stColumn"]:first-child,
            .navbar-row [data-testid="stColumn"]:first-child > div {
                justify-content: flex-start !important;
            }
            .nav-logo img {
                height: 55px;
                object-fit: contain;
                vertical-align: middle;
            }
            .nav-links-inline {
                display: flex;
                gap: 2.5rem;
                align-items: center;
                justify-content: center;
                height: 100%;
            }
            a.nav-link, a.nav-link:visited {
                color: var(--text-secondary) !important;
                text-decoration: none !important;
                font-size: 0.95rem;
                font-weight: 500;
                font-family: 'Poppins', sans-serif;
                transition: color 0.3s ease;
                letter-spacing: 0.02em;
            }
            a.nav-link:hover {
                color: var(--gold) !important;
            }
            a.nav-link.active, a.nav-link.active:visited {
                color: var(--gold) !important;
            }
            .nav-toggle {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            .toggle-icon {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid var(--border);
                background: var(--bg-card);
            }
            .toggle-icon:hover {
                border-color: var(--gold);
                background: rgba(212, 175, 55, 0.1);
            }

            /* ===== HERO SECTION ===== */
            .hero-badge {
                display: inline-block;
                padding: 0.4rem 1.2rem;
                border: 1px solid var(--gold);
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                letter-spacing: 0.15em;
                color: var(--gold);
                font-family: 'Poppins', sans-serif;
                margin-bottom: 1.5rem;
                background: rgba(212, 175, 55, 0.08);
            }
            .hero-heading {
                font-size: 3.4rem;
                font-weight: 800;
                line-height: 1.15;
                margin-bottom: 1.5rem;
                color: var(--text-primary);
                font-family: 'Poppins', sans-serif;
            }
            .hero-heading .gold-gradient {
                background: linear-gradient(135deg, #D4AF37, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .hero-desc {
                font-size: 1.05rem;
                color: var(--text-secondary);
                line-height: 1.7;
                margin-bottom: 2rem;
                max-width: 480px;
            }
            .hero-image-container {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 420px;
                padding: 2rem 1rem;
                position: relative;
            }
            .hero-image-wrapper {
                position: relative;
                display: inline-block;
                padding: 4px;
                border-radius: 22px;
                background: conic-gradient(
                    from var(--shimmer-angle, 0deg),
                    transparent 0%,
                    #D4AF37 10%,
                    #FFD700 20%,
                    transparent 30%,
                    transparent 50%,
                    #D4AF37 60%,
                    #FFD700 70%,
                    transparent 80%
                );
                animation: shimmerRotate 3s linear infinite;
                box-shadow:
                    0 0 30px rgba(212, 175, 55, 0.15),
                    0 0 60px rgba(212, 175, 55, 0.08),
                    inset 0 0 20px rgba(212, 175, 55, 0.05);
            }
            .hero-image-wrapper::before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: 22px;
                padding: 3px;
                background: conic-gradient(
                    from calc(var(--shimmer-angle, 0deg) + 180deg),
                    transparent 0%,
                    rgba(255, 215, 0, 0.4) 15%,
                    transparent 30%
                );
                animation: shimmerRotate 3s linear infinite;
                filter: blur(8px);
                z-index: -1;
            }
            .hero-image-inner {
                background: var(--bg-card);
                border-radius: 18px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1.2rem;
            }
            .hero-image-inner img {
                max-width: 100%;
                max-height: 340px;
                object-fit: contain;
                border-radius: 12px;
            }

            @property --shimmer-angle {
                syntax: '<angle>';
                initial-value: 0deg;
                inherits: false;
            }
            @keyframes shimmerRotate {
                0%   { --shimmer-angle: 0deg; }
                100% { --shimmer-angle: 360deg; }
            }
            /* Fallback shimmer for browsers without @property */
            @supports not (background: conic-gradient(from 0deg, red, blue)) {
                .hero-image-wrapper {
                    border: 2px solid var(--gold);
                    box-shadow:
                        0 0 20px rgba(212, 175, 55, 0.3),
                        0 0 40px rgba(212, 175, 55, 0.15),
                        0 0 80px rgba(212, 175, 55, 0.08);
                    animation: glowPulse 2s ease-in-out infinite alternate;
                }
            }
            @keyframes glowPulse {
                0%   { box-shadow: 0 0 20px rgba(212,175,55,0.2), 0 0 40px rgba(212,175,55,0.1); }
                100% { box-shadow: 0 0 30px rgba(212,175,55,0.4), 0 0 60px rgba(212,175,55,0.2), 0 0 90px rgba(212,175,55,0.1); }
            }

            /* ===== BUTTONS ===== */
            .btn-group {
                display: flex;
                gap: 1rem;
                margin-top: 0.5rem;
            }
            .btn-gold {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.7rem 1.8rem;
                background: linear-gradient(135deg, #D4AF37, #B8960C);
                color: #000 !important;
                border: none;
                border-radius: 8px;
                font-size: 0.9rem;
                font-weight: 600;
                font-family: 'Poppins', sans-serif;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none !important;
            }
            .btn-gold:hover {
                background: linear-gradient(135deg, #e8c547, #D4AF37);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
            }
            .btn-outline {
                display: inline-flex;
                align-items: center;
                padding: 0.7rem 1.8rem;
                background: transparent;
                color: var(--gold) !important;
                border: 1.5px solid var(--gold);
                border-radius: 8px;
                font-size: 0.9rem;
                font-weight: 600;
                font-family: 'Poppins', sans-serif;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none !important;
            }
            .btn-outline:hover {
                background: rgba(212, 175, 55, 0.1);
                transform: translateY(-2px);
            }

            /* Streamlit button overrides */
            div[data-testid="stButton"] > button {
                background: transparent !important;
                color: var(--gold) !important;
                border: 1.5px solid var(--gold) !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                font-family: 'Poppins', sans-serif !important;
                padding: 0.55rem 1.5rem !important;
                transition: all 0.3s ease !important;
                font-size: 0.9rem !important;
            }
            div[data-testid="stButton"] > button:hover {
                background: var(--gold) !important;
                color: #000 !important;
                border-color: var(--gold) !important;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
            }
            div[data-testid="stButton"] > button[kind="primary"] {
                background: linear-gradient(135deg, #D4AF37, #B8960C) !important;
                color: #000 !important;
                border: none !important;
            }
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #e8c547, #D4AF37) !important;
            }

            /* ===== ABOUT SECTION ===== */
            .about-container {
                display: flex;
                gap: 1.5rem;
                margin-top: 2rem;
            }
            .about-text-panel {
                background: var(--bg-card);
                border: 1px solid var(--border-subtle);
                border-radius: 14px;
                padding: 2rem 1.8rem;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .about-label {
                font-size: 0.8rem;
                font-weight: 700;
                color: var(--gold);
                letter-spacing: 0.15em;
                font-family: 'Poppins', sans-serif;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }
            .about-label::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, var(--gold), transparent);
                opacity: 0.5;
            }
            .about-text-panel p {
                font-size: 0.92rem;
                color: var(--text-secondary);
                line-height: 1.75;
                margin: 0;
            }
            
            /* Feature Cards */
            .feature-card {
                background: var(--bg-card);
                border: 1px solid var(--border-subtle);
                border-radius: 14px;
                padding: 1.6rem 1rem;
                text-align: center;
                transition: all 0.35s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .feature-card:hover {
                border-color: rgba(212, 175, 55, 0.35);
                transform: translateY(-5px);
                box-shadow: 0 12px 35px var(--glow-gold);
            }
            .feature-icon {
                font-size: 1.6rem;
                margin-bottom: 0.9rem;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 54px;
                height: 54px;
                background: rgba(212, 175, 55, 0.08);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: 14px;
                transition: all 0.3s ease;
            }
            .feature-card:hover .feature-icon {
                background: rgba(212, 175, 55, 0.15);
                border-color: rgba(212, 175, 55, 0.4);
                box-shadow: 0 0 15px rgba(212, 175, 55, 0.15);
            }
            .feature-title {
                font-size: 0.95rem;
                font-weight: 700;
                color: var(--text-primary);
                font-family: 'Poppins', sans-serif;
                margin-bottom: 0.5rem;
            }
            .feature-desc {
                font-size: 0.8rem;
                color: var(--text-secondary);
                line-height: 1.55;
            }

            /* ===== LOGIN SECTION ===== */
            .login-section-title {
                text-align: center;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.2em;
                color: var(--gold);
                font-family: 'Poppins', sans-serif;
                margin: 3rem 0 2rem 0;
                display: flex;
                align-items: center;
                gap: 1rem;
                justify-content: center;
            }
            .login-section-title::before,
            .login-section-title::after {
                content: '';
                flex: 0 0 80px;
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--gold), transparent);
            }
            .login-card {
                background: var(--bg-card);
                border: 1px solid var(--border-subtle);
                border-radius: 16px;
                padding: 1.8rem;
                display: flex;
                align-items: center;
                gap: 1.5rem;
                transition: all 0.35s ease;
                height: 100%;
            }
            .login-card:hover {
                border-color: var(--border);
                transform: translateY(-4px);
                box-shadow: 0 12px 35px var(--glow-gold);
            }
            .login-card-img {
                width: 130px;
                height: 130px;
                border-radius: 14px;
                object-fit: cover;
                flex-shrink: 0;
            }
            .login-card-content {
                flex: 1;
            }
            .login-card-title {
                font-size: 1.4rem;
                font-weight: 700;
                color: var(--text-primary);
                font-family: 'Poppins', sans-serif;
                margin-bottom: 0.4rem;
            }
            .login-card-desc {
                font-size: 0.88rem;
                color: var(--text-secondary);
                line-height: 1.5;
                margin-bottom: 1rem;
            }

            /* ===== FOOTER ===== */
            .site-footer {
                margin-top: 3rem;
                padding: 2rem 0;
                border-top: 1px solid var(--border-subtle);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }
            .footer-logo img {
                height: 45px;
                object-fit: contain;
            }
            .footer-tagline {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                color: var(--text-secondary);
                font-size: 0.88rem;
                line-height: 1.5;
            }
            .footer-tagline-icon {
                font-size: 1.2rem;
                color: var(--gold);
            }
            .footer-socials {
                display: flex;
                gap: 0.7rem;
            }
            .social-icon {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: var(--bg-card-alt);
                border: 1px solid var(--border-subtle);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.9rem;
                color: var(--text-secondary);
                text-decoration: none !important;
                transition: all 0.3s ease;
            }
            .social-icon:hover {
                border-color: var(--gold);
                color: var(--gold) !important;
                background: rgba(212, 175, 55, 0.1);
            }

            /* ===== SECTION DIVIDER ===== */
            .section-gap {
                margin: 2.5rem 0;
            }

            /* ===== ANIMATIONS ===== */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(25px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideInLeft {
                from { opacity: 0; transform: translateX(-30px); }
                to { opacity: 1; transform: translateX(0); }
            }
            @keyframes slideInRight {
                from { opacity: 0; transform: translateX(30px); }
                to { opacity: 1; transform: translateX(0); }
            }
            @keyframes scaleIn {
                from { opacity: 0; transform: scale(0.92); }
                to { opacity: 1; transform: scale(1); }
            }
            @keyframes pulseGlow {
                0%, 100% { box-shadow: 0 0 20px rgba(212,175,55,0.1); }
                50% { box-shadow: 0 0 40px rgba(212,175,55,0.25); }
            }
            .animate-in {
                animation: fadeInUp 0.7s ease-out forwards;
            }
            .animate-scale {
                animation: scaleIn 0.5s ease-out forwards;
            }
            .animate-slide-left {
                animation: slideInLeft 0.6s ease-out forwards;
            }
            .animate-slide-right {
                animation: slideInRight 0.6s ease-out forwards;
            }

            /* ===== NAV-RIGHT (Login btn area) ===== */
            .nav-right {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            /* ===== AUTH PAGES (Login / Register) ===== */
            .auth-page {
                min-height: 60vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .auth-header {
                text-align: center;
                margin-bottom: 2rem;
                animation: scaleIn 0.5s ease-out;
            }
            .auth-icon {
                font-size: 3rem;
                margin-bottom: 0.8rem;
                display: inline-block;
                animation: pulseGlow 2s ease-in-out infinite;
                width: 72px;
                height: 72px;
                line-height: 72px;
                border-radius: 50%;
                background: rgba(212, 175, 55, 0.08);
                border: 1px solid var(--border);
            }
            .auth-title {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text-primary) !important;
                font-family: 'Poppins', sans-serif !important;
                margin-bottom: 0.3rem;
            }
            .auth-subtitle {
                font-size: 0.95rem;
                color: var(--text-secondary);
            }

            /* Streamlit input overrides for auth forms */
            div[data-testid="stTextInput"] input {
                background: var(--bg-card) !important;
                border: 1px solid var(--border-subtle) !important;
                border-radius: 10px !important;
                color: var(--text-primary) !important;
                padding: 0.7rem 1rem !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.95rem !important;
                transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: var(--gold) !important;
                box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.15) !important;
                outline: none !important;
            }
            div[data-testid="stTextInput"] input::placeholder {
                color: var(--text-muted) !important;
            }

            /* Select box overrides */
            div[data-testid="stSelectbox"] > div > div {
                background: var(--bg-card) !important;
                border: 1px solid var(--border-subtle) !important;
                border-radius: 10px !important;
                color: var(--text-primary) !important;
                transition: border-color 0.3s ease !important;
            }
            div[data-testid="stSelectbox"] > div > div:focus-within {
                border-color: var(--gold) !important;
                box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.15) !important;
            }

            /* Warning / Error messages */
            div[data-testid="stAlert"] {
                border-radius: 10px !important;
                animation: fadeInUp 0.4s ease-out;
            }

            /* ===== SCROLLBAR ===== */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: var(--bg-primary); }
            ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: var(--gold); }

            /* ===== RESPONSIVE ===== */
            @media (max-width: 768px) {
                .navbar {
                    flex-wrap: wrap;
                    gap: 0.8rem;
                }
                .nav-links {
                    gap: 1.2rem;
                    order: 3;
                    width: 100%;
                    justify-content: center;
                }
                .hero-heading {
                    font-size: 2.2rem;
                }
                .hero-desc {
                    font-size: 0.95rem;
                }
                .hero-image-container {
                    min-height: 250px;
                    padding: 1rem 0;
                }
                .login-card {
                    flex-direction: column;
                    text-align: center;
                    padding: 1.5rem;
                }
                .login-card-img {
                    width: 100px;
                    height: 100px;
                }
                .login-card-title {
                    font-size: 1.2rem;
                }
                .auth-title {
                    font-size: 1.6rem;
                }
                .site-footer {
                    flex-direction: column;
                    text-align: center;
                }
            }

            @media (max-width: 480px) {
                .block-container {
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                }
                .hero-heading {
                    font-size: 1.8rem;
                }
                .hero-badge {
                    font-size: 0.65rem;
                    padding: 0.3rem 0.8rem;
                }
                .nav-logo img {
                    height: 40px;
                }
                a.nav-link {
                    font-size: 0.8rem;
                }
            }

        </style>
    """, unsafe_allow_html=True)
