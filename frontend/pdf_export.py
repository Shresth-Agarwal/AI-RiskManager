from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _safe_text(value) -> str:
    if value is None:
        return ""
    return escape(str(value))


def _format_percent(value) -> str:
    try:
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return "N/A"


def _build_styles():
    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#111827"),
            alignment=TA_LEFT,
            spaceAfter=4 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=7 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#111827"),
            spaceBefore=5 * mm,
            spaceAfter=3 * mm,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#6B7280"),
        ),
        "value": ParagraphStyle(
            "Value",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#111827"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=2 * mm,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#6B7280"),
        ),
        "recommendation": ParagraphStyle(
            "Recommendation",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#374151"),
        ),
    }


def _bullet_list(items, style):
    if not items:
        return [Paragraph("None identified.", style)]

    return [
        Paragraph(f"• {_safe_text(item)}", style)
        for item in items
    ]


def generate_risk_report_pdf(result: dict) -> bytes:
    """
    Generate a professional PDF report from an existing
    frontend risk-analysis result.

    No backend/API calls are made here.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="AI Risk Manager Report",
        author="AI Risk Manager",
    )

    styles = _build_styles()
    story = []

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "AI RISK MANAGER",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "AI-assisted payment dispute risk assessment",
            styles["subtitle"],
        )
    )

    # ---------------------------------------------------------
    # Risk Assessment
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "RISK ASSESSMENT",
            styles["section"],
        )
    )

    severity = str(result.get("severity", "Unknown")).upper()
    confidence = _format_percent(result.get("confidence"))
    reason = result.get("reason_code", "Not provided")
    review_required = result.get("needs_human_review", False)

    risk_data = [
        [
            Paragraph("RISK LEVEL", styles["label"]),
            Paragraph("CONFIDENCE", styles["label"]),
        ],
        [
            Paragraph(
                _safe_text(severity),
                styles["value"],
            ),
            Paragraph(
                _safe_text(confidence),
                styles["value"],
            ),
        ],
        [
            Paragraph("DISPUTE REASON", styles["label"]),
            Paragraph("HUMAN REVIEW", styles["label"]),
        ],
        [
            Paragraph(
                _safe_text(reason),
                styles["value"],
            ),
            Paragraph(
                "Required" if review_required else "Not required",
                styles["value"],
            ),
        ],
    ]

    risk_table = Table(
        risk_data,
        colWidths=[85 * mm, 85 * mm],
        hAlign="LEFT",
    )

    risk_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F9FAFB"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#E5E7EB"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#E5E7EB"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
            ]
        )
    )

    story.append(risk_table)

    # ---------------------------------------------------------
    # Evidence Assessment
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE ASSESSMENT",
            styles["section"],
        )
    )

    completeness = _format_percent(
        result.get("evidence_completeness", 0)
    )

    story.append(
        Paragraph(
            f"<b>Evidence completeness:</b> {completeness}",
            styles["body"],
        )
    )

    evidence_sections = [
        (
            "Present Evidence",
            result.get("present_evidence", []),
        ),
        (
            "Missing Evidence",
            result.get("missing_evidence", []),
        ),
        (
            "Supporting Evidence",
            result.get("supporting_evidence", []),
        ),
        (
            "Weakening Evidence",
            result.get("weakening_evidence", []),
        ),
    ]

    evidence_data = []

    for title, items in evidence_sections:
        content = [
            Paragraph(
                f"<b>{_safe_text(title)}</b>",
                styles["label"],
            )
        ]

        content.extend(
            _bullet_list(items, styles["small"])
        )

        evidence_data.append(content)

    evidence_table = Table(
        [
            [evidence_data[0], evidence_data[1]],
            [evidence_data[2], evidence_data[3]],
        ],
        colWidths=[85 * mm, 85 * mm],
        hAlign="LEFT",
    )

    evidence_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#E5E7EB"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#E5E7EB"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F9FAFB"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
            ]
        )
    )

    story.append(evidence_table)

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "RECOMMENDATIONS",
            styles["section"],
        )
    )

    recommendations = result.get("recommendations", [])

    if recommendations:
        recommendation_rows = []

        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            recommendation_rows.append(
                [
                    Paragraph(
                        f"<b>{index:02d}</b>",
                        styles["label"],
                    ),
                    Paragraph(
                        _safe_text(recommendation),
                        styles["recommendation"],
                    ),
                ]
            )

        recommendation_table = Table(
            recommendation_rows,
            colWidths=[12 * mm, 158 * mm],
            hAlign="LEFT",
        )

        recommendation_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor("#E5E7EB"),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#E5E7EB"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#F9FAFB"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                ]
            )
        )

        story.append(recommendation_table)
    else:
        story.append(
            Paragraph(
                "No recommendations provided.",
                styles["body"],
            )
        )

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    verification_provider = result.get(
        "verification_provider",
        "",
    )
    verification_notes = result.get(
        "verification_notes",
        "",
    )

    if verification_provider or verification_notes:
        story.append(
            Paragraph(
                "VERIFICATION",
                styles["section"],
            )
        )

        if verification_provider:
            story.append(
                Paragraph(
                    f"<b>Provider:</b> "
                    f"{_safe_text(verification_provider)}",
                    styles["body"],
                )
            )

        if verification_notes:
            story.append(
                Paragraph(
                    f"<b>Notes:</b> "
                    f"{_safe_text(verification_notes)}",
                    styles["body"],
                )
            )

    # ---------------------------------------------------------
    # Full Report
    # ---------------------------------------------------------

    report = result.get("report", "")

    if report:
        # Start the full report on a fresh page so the heading
        # and report content are never orphaned at the bottom
        # of the previous page.
        story.append(PageBreak())

        story.append(
            Paragraph(
                "FULL REPORT",
                styles["section"],
            )
        )

        for paragraph in str(report).split("\n"):
            paragraph = paragraph.strip()

            if not paragraph:
                story.append(Spacer(1, 2 * mm))
                continue

            story.append(
                Paragraph(
                    _safe_text(paragraph),
                    styles["body"],
                )
            )

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    def add_page_footer(canvas, doc):
        canvas.saveState()

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(
            colors.HexColor("#9CA3AF")
        )

        canvas.drawString(
            18 * mm,
            10 * mm,
            "AI Risk Manager",
        )

        canvas.drawRightString(
            A4[0] - 18 * mm,
            10 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )

    return buffer.getvalue()