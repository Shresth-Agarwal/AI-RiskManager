import streamlit as st


def render_verdict(result):
    severity = result["severity"].lower()
    reason = result["reason_code"]
    confidence = result["confidence"]
    review_required = result["needs_human_review"]

    severity_label = {
        "high": "HIGH RISK",
        "medium": "MEDIUM RISK",
        "low": "LOW RISK",
    }.get(severity, severity.upper())

    # Dynamic status variable prevents logic indents inside the HTML string
    status_text = "⚠️ Human review required" if review_required else "✅ No human review required"

    st.markdown(
        '<div class="section-label">RISK ASSESSMENT</div>',
        unsafe_allow_html=True,
    )


    html_content = f"""
<div class="risk-card risk-{severity}">
<div class="risk-card-top">
<div>
<div class="risk-label">RISK LEVEL</div>
<div class="risk-level">{severity_label}</div>
</div>
<div class="confidence-box">
<div class="risk-label">CONFIDENCE</div>
<div class="confidence-value">{confidence * 100:.0f}%</div>
</div>
</div>
<div class="risk-reason">
<span>Dispute reason</span>
<strong>{reason}</strong>
</div>
<div class="risk-status">
{status_text}
</div>
</div>
"""

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


def render_evidence(result: dict) -> None:
    st.subheader("Evidence Assessment")

    completeness = result.get("evidence_completeness", 0.0)

    present = result.get("present_evidence", [])
    supporting = result.get("supporting_evidence", [])
    weakening = result.get("weakening_evidence", [])
    missing = result.get("missing_evidence", [])
    
    evidence_labels = {
        "transaction_ids_for_both_charges": "Transaction IDs for both charges",
        "timestamp_proximity": "Timestamp proximity",
        "delivery_confirmation": "Delivery confirmation",
        "tracking_matches_shipping_address": "Tracking matches shipping address",
        "signature_or_photo_proof": "Signature or photo proof",
        "product_listing_screenshot": "Product listing screenshot",
        "customer_photos_or_description_of_issue": "Customer photos or description of issue",
        "pre_shipment_condition_proof": "Pre-shipment condition proof",
        "authentication_record": "Authentication record",
        "device_fingerprint_match": "Device fingerprint match",
        "purchase_history_consistency": "Purchase history consistency",
    }

    def render_items(items):
        if not items:
            return '<div class="evidence-empty">None identified.</div>'

        return "".join(
            f'<div class="evidence-item">• {evidence_labels.get(item, item)}</div>'
            for item in items
        )

    html_content = f"""
<div class="evidence-header">
<div class="evidence-caption">EVIDENCE COMPLETENESS</div>
<div class="evidence-score">{completeness:.0%}</div>
</div>
<div class="evidence-bar">
<div class="evidence-bar-fill" style="width: {completeness * 100:.0f}%"></div>
</div>
<div class="evidence-grid">
<div class="evidence-card evidence-present">
<div class="evidence-card-title">✓ PRESENT EVIDENCE</div>
{render_items(present)}
</div>
<div class="evidence-card evidence-missing">
<div class="evidence-card-title">⚠ MISSING EVIDENCE</div>
{render_items(missing)}
</div>
<div class="evidence-card evidence-supporting">
<div class="evidence-card-title">✅ SUPPORTING EVIDENCE</div>
{render_items(supporting)}
</div>
<div class="evidence-card evidence-weakening">
<div class="evidence-card-title">❌ WEAKENING EVIDENCE</div>
{render_items(weakening)}
</div>
</div>
"""

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


def render_recommendations(result: dict) -> None:
    st.markdown(
        '<div class="section-label">RECOMMENDATIONS</div>',
        unsafe_allow_html=True,
    )

    recommendations = result.get("recommendations", [])

    if not recommendations:
        html_content = """
<div class="recommendations-card">
<div class="recommendation-empty">No recommendations provided.</div>
</div>
"""
    else:
        recommendation_items = "".join(
            f"""
<div class="recommendation-item">
<div class="recommendation-number">{index:02d}</div>
<div class="recommendation-text">{recommendation}</div>
</div>
"""
            for index, recommendation in enumerate(recommendations, start=1)
        )

        html_content = f"""
<div class="recommendations-card">
{recommendation_items}
</div>
"""

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


def render_review_flag(result: dict) -> None:
    needs_review = result.get("needs_human_review", False)

    if needs_review:
        st.error("⚠️ Human review required")
    else:
        st.success("No human review required")

    verification_provider = result.get("verification_provider", "")
    verification_notes = result.get("verification_notes", "")

    if verification_provider:
        st.write(f"Verification provider: **{verification_provider}**")

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
