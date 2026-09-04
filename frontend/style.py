import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>

        /* Main application */
        .stApp {
            background: #0b0d12;
        }

        /* Content width */
        .block-container {
            max-width: 1400px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        /* Typography */
        h1, h2, h3 {
            letter-spacing: -0.03em;
        }

        h1 {
            font-size: 3.8rem !important;
            line-height: 1.05 !important;
            font-weight: 800 !important;
        }

        h2 {
            font-size: 2.2rem !important;
            font-weight: 750 !important;
        }

        h3 {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }

        /* Hide Streamlit branding */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 999px;
            padding: 0.65rem 1.5rem;
            font-weight: 650;
            border: 1px solid rgba(255, 255, 255, 0.12);
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.3);
        }

        /* Text areas */
        .stTextArea textarea {
            border-radius: 16px;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            border-radius: 18px;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.2rem;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Tables */
        [data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            font-weight: 650;
            padding: 0.8rem 0.2rem;
        }
        
        
        /* Hero */

        .hero {
            padding: 4rem 0 3rem 0;
            max-width: 900px;
        }

        .hero-eyebrow {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            opacity: 0.6;
            margin-bottom: 1.5rem;
        }

        .hero-title {
            font-size: 5rem !important;
            line-height: 0.98 !important;
            letter-spacing: -0.055em !important;
            margin: 0 !important;
            font-weight: 850 !important;
        }

        .hero-title span {
            opacity: 0.55;
        }

        .hero-subtitle {
            max-width: 680px;
            margin-top: 1.8rem;
            font-size: 1.15rem;
            line-height: 1.7;
            opacity: 0.65;
        }

        .hero-pills {
            display: flex;
            gap: 0.7rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        .hero-pill {
            padding: 0.55rem 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.035);
            font-size: 0.82rem;
            font-weight: 600;
            opacity: 0.8;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )