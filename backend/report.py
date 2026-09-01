# backend/report.py
"""
Formats a completed RiskState into a human-readable dispute report.
No new fields needed — this consumes what analyze_risk / check_evidence /
verify_risk already produced.
"""

from datetime import datetime


def generate_report(state: dict, case_id: str = "N/A") -> str:
    severity = state.get("severity", "unknown")
    llm_severity = state.get("llm_severity", severity)
    reason_code = state.get("reason_code", "unknown")
    confidence = state.get("confidence", 0.0)
    completeness = state.get("evidence_completeness", 0.0)
    present = state.get("present_evidence", [])
    missing = state.get("missing_evidence", [])
    recommendations = state.get("recommendations", [])
    needs_review = state.get("needs_human_review", False)
    verification_notes = state.get("verification_notes", "")
    verification_provider = state.get("verification_provider", "")
    provider_used = state.get("provider_used", "")

    lines = []
    lines.append(f"# Dispute Risk Report — {case_id}")
    lines.append(f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")

    lines.append("## Case")
    lines.append(state.get("risk_description", "").strip() + "\n")

    lines.append("## Verdict")
    lines.append(f"- **Reason code:** {reason_code}")
    lines.append(f"- **Severity:** {severity}" + (
        f"  _(LLM initially assessed: {llm_severity})_"
        if llm_severity != severity else ""
    ))
    lines.append(f"- **Model confidence:** {confidence:.2f}")
    lines.append(f"- **Evidence completeness:** {completeness:.0%}\n")

    lines.append("## Evidence Checklist")
    if present or missing:
        for item in present:
            lines.append(f"- [x] {item.replace('_', ' ')}")
        for item in missing:
            lines.append(f"- [ ] {item.replace('_', ' ')}  ⚠ missing")
    else:
        lines.append("_No structured evidence requirements apply to this reason code._")
    lines.append("")

    lines.append("## Recommendations")
    if recommendations:
        for rec in recommendations:
            lines.append(f"- {rec}")
    else:
        lines.append("_None provided._")
    lines.append("")

    if needs_review:
        lines.append("## ⚠ Flagged for Human Review")
        lines.append(
            verification_notes or
            "Escalated due to low model confidence or incomplete evidence."
        )
        if verification_provider:
            lines.append(f"\n_Verified by: {verification_provider}_")
        lines.append("")
    else:
        lines.append("## Review Status")
        lines.append("No escalation needed — confidence and evidence both met threshold.\n")

    lines.append("---")
    lines.append(f"_Primary analysis by: {provider_used}_")

    return "\n".join(lines)


def save_report(report_text: str, case_id: str, output_dir: str = "reports") -> str:
    import os
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{case_id}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return path


if __name__ == "__main__":
    from backend.graph import graph

    result = graph.invoke({
        "risk_description": (
            "Customer disputes a ₹12,000 transaction claiming the purchase was not authorized. "
            "The merchant has no delivery confirmation, no customer communication history, "
            "and no clear authentication record. The customer has previously made one dispute "
            "but the available evidence is incomplete."
        ),
        "analysis": "", "severity": "", "llm_severity": "",
        "evidence_completeness": 0.0, "present_evidence": [], "missing_evidence": [],
        "reason_code": "", "confidence": 0.0, "supporting_evidence": [],
        "weakening_evidence": [], "recommendations": [], "provider_used": "",
        "verification_notes": "", "verification_provider": "", "needs_human_review": False,
    })

    report = generate_report(result, case_id="DEMO-001")
    print(report)
    path = save_report(report, "DEMO-001")
    print(f"\nSaved to {path}")