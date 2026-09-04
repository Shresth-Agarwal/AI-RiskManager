import pandas as pd
import streamlit as st

from frontend.api_client import analyze_batch


def render_portfolio():
    st.subheader("Portfolio Risk Analysis")
    st.caption("Analyze multiple payment disputes at once.")

    uploaded_file = st.file_uploader(
        "Upload dispute CSV",
        type=["csv"],
        help="CSV must contain: description, amount",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to analyze your dispute portfolio.")
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        return

    required_columns = {"description", "amount"}

    if not required_columns.issubset(df.columns):
        st.error(
            "CSV must contain these columns: "
            "`description` and `amount`."
        )
        return

    if df.empty:
        st.warning("The uploaded CSV contains no cases.")
        return

    if df["description"].isna().any():
        st.error("Every case must have a description.")
        return

    if df["amount"].isna().any():
        st.error("Every case must have an amount.")
        return

    try:
        df["amount"] = pd.to_numeric(df["amount"])
    except Exception:
        st.error("Amount must contain valid numbers.")
        return

    if (df["amount"] < 0).any():
        st.error("Amount cannot be negative.")
        return

    st.write(f"**{len(df)} cases detected**")

    if st.button("Analyze Portfolio", type="primary"):
        cases = [
            {
                "description": str(row["description"]),
                "amount": float(row["amount"]),
            }
            for _, row in df.iterrows()
        ]

        with st.spinner(
            f"Analyzing {len(cases)} disputes..."
        ):
            try:
                result = analyze_batch(cases)
            except Exception as exc:
                st.error(f"Portfolio analysis failed: {exc}")
                return

        st.session_state["portfolio_result"] = result

    if "portfolio_result" in st.session_state:
        render_portfolio_results(
            st.session_state["portfolio_result"]
        )


def render_portfolio_results(result: dict):
    st.divider()

    st.subheader("Portfolio Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Disputes",
        result["total_cases"],
    )

    col2.metric(
        "Total Disputed Amount",
        f"₹{result['total_amount']:,.0f}",
    )

    col3.metric(
        "Human Review Rate",
        f"{result['human_review_rate'] * 100:.1f}%",
    )

    col4.metric(
        "Avg. Evidence Completeness",
        f"{result['average_evidence_completeness'] * 100:.1f}%",
    )

    st.subheader("Risk Distribution")

    severity = result["severity_distribution"]

    col1, col2, col3 = st.columns(3)

    col1.metric("High", severity.get("high", 0))
    col2.metric("Medium", severity.get("medium", 0))
    col3.metric("Low", severity.get("low", 0))

    st.subheader("Reason Distribution")

    reason_distribution = result["reason_distribution"]

    if reason_distribution:
        reason_df = pd.DataFrame(
            {
                "Reason": list(reason_distribution.keys()),
                "Cases": list(reason_distribution.values()),
            }
        )

        st.bar_chart(
            reason_df.set_index("Reason")
        )

    st.subheader("Dispute Portfolio")

    rows = []

    for case in result["results"]:
        rows.append(
            {
                "Case ID": case["case_id"],
                "Severity": case["severity"].upper(),
                "Reason": case["reason_code"],
                "Confidence": f"{case['confidence'] * 100:.0f}%",
                "Evidence": f"{case['evidence_completeness'] * 100:.0f}%",
                "Human Review": (
                    "YES"
                    if case["needs_human_review"]
                    else "NO"
                ),
            }
        )

    results_df = pd.DataFrame(rows)

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )