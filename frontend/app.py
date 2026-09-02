import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from frontend.api_client import analyze_case, check_health
from frontend.components.report_view import render_full_report

st.set_page_config(
    page_title="AI Risk Manager",
    page_icon="🛡️",
    layout="wide",
)


st.title("🛡️ AI Risk Manager")
st.caption(
    "AI-powered payment dispute risk assessment"
)


# Backend health

if check_health():
    st.success("Backend connected")
else:
    st.error(
        "Backend is not available. "
        "Start FastAPI with: "
        "`uvicorn api.main:app --reload`"
    )
    st.stop()


# Case input

st.subheader("Analyze Payment Dispute")

description = st.text_area(
    "Dispute description",
    height=180,
    placeholder=(
        "Describe the customer's payment dispute..."
    ),
)


analyze_button = st.button(
    "Analyze Case",
    type="primary",
)


# Analysis

if analyze_button:

    if not description.strip():
        st.warning(
            "Please enter a dispute description."
        )
        st.stop()

    with st.spinner("Analyzing dispute..."):

        try:
            result = analyze_case(
                description.strip()
            )

            st.session_state["risk_result"] = result

        except Exception as exc:
            st.error(
                f"Analysis failed: {exc}"
            )
            st.stop()


# Results

if "risk_result" in st.session_state:

    st.divider()

    render_full_report(
        st.session_state["risk_result"]
    )