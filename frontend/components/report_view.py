import streamlit as st


def render_verdict(result: dict) -> None:
    st.subheader("Risk Verdict")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Severity",
            result.get("severity", "N/A"),
        )

    with col2:
        st.metric(
            "Reason",
            result.get("reason_code", "N/A"),
        )

    with col3:
        confidence = result.get("confidence", 0.0)

        st.metric(
            "Confidence",
            f"{confidence:.0%}",
        )


def render_evidence(result: dict) -> None:
    st.subheader("Evidence Assessment")

    completeness = result.get("evidence_completeness", 0.0)

    st.write(
        f"Evidence completeness: **{completeness:.0%}**"
    )

    st.progress(completeness)

    present = result.get("present_evidence", [])
    supporting = result.get("supporting_evidence", [])
    weakening = result.get("weakening_evidence", [])
    missing = result.get("missing_evidence", [])

    with st.expander("Present Evidence"):
        if present:
            for item in present:
                st.write(f"- {item}")
        else:
            st.write("None identified.")

    with st.expander("Supporting Evidence"):
        if supporting:
            for item in supporting:
                st.write(f"- {item}")
        else:
            st.write("None identified.")

    with st.expander("Weakening Evidence"):
        if weakening:
            for item in weakening:
                st.write(f"- {item}")
        else:
            st.write("None identified.")

    with st.expander("Missing Evidence"):
        if missing:
            for item in missing:
                st.write(f"- {item}")
        else:
            st.write("None identified.")


def render_recommendations(result: dict) -> None:
    st.subheader("Recommendations")

    recommendations = result.get("recommendations", [])

    if recommendations:
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    else:
        st.write("No recommendations provided.")


def render_review_flag(result: dict) -> None:
    needs_review = result.get("needs_human_review", False)

    if needs_review:
        st.error(
            "⚠️ Human review required"
        )
    else:
        st.success(
            "No human review required"
        )

    verification_provider = result.get(
        "verification_provider",
        "",
    )

    verification_notes = result.get(
        "verification_notes",
        "",
    )

    if verification_provider:
        st.write(
            f"Verification provider: **{verification_provider}**"
        )

    if verification_notes:
        with st.expander("Verification Notes"):
            st.write(verification_notes)


def render_full_report(result: dict) -> None:
    render_verdict(result)

    st.divider()

    render_evidence(result)

    st.divider()

    render_recommendations(result)

    st.divider()

    render_review_flag(result)

    st.divider()

    st.subheader("Full Report")

    report = result.get("report", "")

    if report:
        st.markdown(report)
    else:
        st.write("No report available.")