import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>

        /* =========================================================
           Main application
        ========================================================= */

        .stApp {
            background: #0b0d12;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }


        /* =========================================================
           Typography
        ========================================================= */

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


        /* =========================================================
           Hide Streamlit branding
        ========================================================= */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }


        /* =========================================================
           Buttons
        ========================================================= */

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


        /* =========================================================
           Text areas
        ========================================================= */

        .stTextArea textarea {
            border-radius: 16px;
        }


        /* =========================================================
           File uploader
        ========================================================= */

        [data-testid="stFileUploader"] {
            border-radius: 18px;
        }


        /* =========================================================
           Metrics
        ========================================================= */

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.2rem;
        }


        /* =========================================================
           Expanders
        ========================================================= */

        [data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }


        /* =========================================================
           Tables
        ========================================================= */

        [data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }


        /* =========================================================
           Tabs
        ========================================================= */

        .stTabs [data-baseweb="tab-list"] {
            gap: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            font-weight: 650;
            padding: 0.8rem 0.2rem;
        }


        /* =========================================================
           Hero
        ========================================================= */

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


        /* =========================================================
           Risk Assessment
        ========================================================= */

        .section-label {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            opacity: 0.55;
            margin-bottom: 1rem;
        }

        .risk-card {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 2.5rem;
            background: rgba(255, 255, 255, 0.015);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }


        /* =========================================================
           Dynamic Risk Colors
        ========================================================= */

        .risk-high {
            border-color: rgba(239, 68, 68, 0.3);
            box-shadow: inset 0 0 12px rgba(239, 68, 68, 0.05);
        }

        .risk-high .risk-level {
            color: #ef4444;
        }

        .risk-high .risk-status {
            color: #fca5a5;
        }


        .risk-medium {
            border-color: rgba(234, 179, 8, 0.25);
            box-shadow: inset 0 0 12px rgba(234, 179, 8, 0.05);
        }

        .risk-medium .risk-level {
            color: #eab308;
        }

        .risk-medium .risk-status {
            color: #fef08a;
        }


        .risk-low {
            border-color: rgba(34, 197, 94, 0.2);
            box-shadow: inset 0 0 12px rgba(34, 197, 94, 0.03);
        }

        .risk-low .risk-level {
            color: #22c55e;
        }

        .risk-low .risk-status {
            color: #bbf7d0;
        }


        /* =========================================================
           Risk Card Layout
        ========================================================= */

        .risk-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .risk-label {
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            font-weight: 700;
            opacity: 0.45;
            margin-bottom: 0.4rem;
        }

        .risk-level {
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .confidence-box {
            text-align: right;
        }

        .confidence-value {
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #ffffff;
        }

        .risk-reason {
            margin-top: 2rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .risk-reason span {
            display: block;
            font-size: 0.8rem;
            opacity: 0.45;
            margin-bottom: 0.3rem;
        }

        .risk-reason strong {
            font-size: 1.25rem;
            color: #f3f4f6;
        }

        .risk-status {
            margin-top: 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }


        /* =========================================================
           Evidence Assessment
        ========================================================= */

        .evidence-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 0.8rem;
        }

        .evidence-score {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .evidence-caption {
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            font-weight: 700;
            opacity: 0.45;
        }

        .evidence-bar {
            height: 8px;
            width: 100%;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.08);
            overflow: hidden;
            margin-bottom: 1.8rem;
        }

        .evidence-bar-fill {
            height: 100%;
            border-radius: 999px;
            background: #3b82f6;
        }

        .evidence-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .evidence-card {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.25rem;
            background: rgba(255, 255, 255, 0.02);
            min-height: 130px;
        }

        .evidence-card-title {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-bottom: 0.9rem;
        }

        .evidence-present {
            border-color: rgba(34, 197, 94, 0.2);
        }

        .evidence-present .evidence-card-title {
            color: #86efac;
        }

        .evidence-missing {
            border-color: rgba(239, 68, 68, 0.2);
        }

        .evidence-missing .evidence-card-title {
            color: #fca5a5;
        }

        .evidence-supporting {
            border-color: rgba(59, 130, 246, 0.2);
        }

        .evidence-supporting .evidence-card-title {
            color: #93c5fd;
        }

        .evidence-weakening {
            border-color: rgba(234, 179, 8, 0.2);
        }

        .evidence-weakening .evidence-card-title {
            color: #fde68a;
        }

        .evidence-item {
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 0.45rem 0;
        }

        .evidence-empty {
            opacity: 0.45;
            font-size: 0.9rem;
        }


        /* =========================================================
           Responsive
        ========================================================= */

        @media (max-width: 800px) {

            .hero-title {
                font-size: 3.5rem !important;
            }

            .evidence-grid {
                grid-template-columns: 1fr;
            }

            .risk-card-top {
                gap: 1rem;
            }

            .risk-level,
            .confidence-value {
                font-size: 2rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )