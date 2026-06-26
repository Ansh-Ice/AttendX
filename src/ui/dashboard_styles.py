"""
dashboard_styles.py — Shared CSS for Teacher and Student dashboards.

Eliminates the ~200 lines of duplicated CSS that was copy-pasted between
teacher_screen.py and student_screen.py.
"""

import streamlit as st


def apply_dashboard_css():
    """Shared dashboard CSS — tabs, header, welcome banner, stat cards, section labels, animations."""
    st.markdown("""
        <style>
            /* ===== TABS ===== */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0;
                width: 100%;
                background-color: transparent;
                border-bottom: 1px solid rgba(255,255,255,0.06);
            }
            .stTabs [data-baseweb="tab"] {
                flex: 1;
                display: flex;
                justify-content: center;
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 4px 4px 0 0;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
                color: #999;
                font-family: 'Poppins', sans-serif;
                font-size: 0.95rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: #D4AF37;
            }
            .stTabs [aria-selected="true"] {
                color: #D4AF37 !important;
                border-bottom: 2px solid #D4AF37 !important;
                background-color: rgba(212, 175, 55, 0.05);
            }
            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 2rem;
            }

            /* ===== DASHBOARD HEADER ===== */
            .dash-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.6rem 0 1rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                margin-bottom: 2rem;
            }
            .dash-header-logo img {
                height: 48px;
                object-fit: contain;
            }
            .dash-header-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.1rem;
                font-weight: 600;
                color: #f0f0f0;
                letter-spacing: 0.03em;
            }
            .dash-header-title span {
                color: #D4AF37;
            }

            /* ===== DASHBOARD CARDS ===== */
            .dash-card {
                background: #1A1A1A;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 2rem 1.8rem;
                transition: all 0.35s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
            }
            .dash-card:hover {
                border-color: rgba(212, 175, 55, 0.3);
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(212, 175, 55, 0.08);
            }
            .dash-card-icon {
                width: 56px;
                height: 56px;
                border-radius: 14px;
                background: rgba(212, 175, 55, 0.08);
                border: 1px solid rgba(212, 175, 55, 0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                margin-bottom: 1.2rem;
                transition: all 0.3s ease;
            }
            .dash-card:hover .dash-card-icon {
                background: rgba(212, 175, 55, 0.15);
                border-color: rgba(212, 175, 55, 0.4);
                box-shadow: 0 0 20px rgba(212, 175, 55, 0.12);
            }
            .dash-card-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.15rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.5rem;
            }
            .dash-card-desc {
                font-size: 0.88rem;
                color: #999;
                line-height: 1.6;
                margin-bottom: 1.5rem;
                flex: 1;
            }

            /* ===== WELCOME BANNER ===== */
            .welcome-banner {
                background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(212,175,55,0.02));
                border: 1px solid rgba(212, 175, 55, 0.15);
                border-radius: 16px;
                padding: 2rem 2.5rem;
                margin-bottom: 2rem;
            }
            .welcome-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.6rem;
                font-weight: 700;
                color: #f0f0f0;
                margin-bottom: 0.3rem;
            }
            .welcome-title .gold {
                background: linear-gradient(135deg, #D4AF37, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .welcome-subtitle {
                font-size: 0.95rem;
                color: #999;
                line-height: 1.6;
            }

            /* ===== STAT CARDS ===== */
            .stat-card {
                background: #141414;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
                padding: 1.4rem 1.6rem;
                text-align: center;
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                border-color: rgba(212, 175, 55, 0.2);
            }
            .stat-value {
                font-family: 'Poppins', sans-serif;
                font-size: 1.8rem;
                font-weight: 800;
                color: #D4AF37;
                margin-bottom: 0.2rem;
            }
            .stat-label {
                font-size: 0.8rem;
                color: #999;
                font-weight: 500;
                letter-spacing: 0.05em;
            }

            /* ===== SECTION LABEL ===== */
            .section-label {
                font-family: 'Poppins', sans-serif;
                font-size: 0.8rem;
                font-weight: 700;
                color: #D4AF37;
                letter-spacing: 0.15em;
                margin-bottom: 1.2rem;
                display: flex;
                align-items: center;
                gap: 0.7rem;
            }
            .section-label::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, rgba(212,175,55,0.3), transparent);
            }

            /* ===== ANIMATION ===== */
            .dash-animate {
                animation: fadeInUp 0.6s ease-out forwards;
                opacity: 0;
            }
            .dash-animate:nth-child(1) { animation-delay: 0.05s; }
            .dash-animate:nth-child(2) { animation-delay: 0.12s; }
            .dash-animate:nth-child(3) { animation-delay: 0.19s; }

            /* ===== RESPONSIVE DASHBOARD ===== */
            @media (max-width: 768px) {
                .welcome-banner {
                    padding: 1.5rem 1.2rem;
                }
                .welcome-title {
                    font-size: 1.3rem;
                }
                .stat-card {
                    padding: 1rem 1.2rem;
                }
                .stat-value {
                    font-size: 1.4rem;
                }
                .dash-card {
                    padding: 1.5rem 1.2rem;
                }
                .dash-header-title {
                    font-size: 0.95rem;
                }
                .dash-header-logo img {
                    height: 36px;
                }
                .stTabs [data-baseweb="tab"] {
                    font-size: 0.8rem;
                    height: 42px;
                    padding: 8px 4px;
                }
            }

            @media (max-width: 480px) {
                .welcome-banner {
                    padding: 1.2rem 1rem;
                }
                .welcome-title {
                    font-size: 1.1rem;
                }
                .welcome-subtitle {
                    font-size: 0.85rem;
                }
                .stat-value {
                    font-size: 1.2rem;
                }
                .stat-label {
                    font-size: 0.7rem;
                }
            }
        </style>
    """, unsafe_allow_html=True)
