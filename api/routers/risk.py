from fastapi import APIRouter

from api.schemas import RiskRequest, RiskResponse
from backend.graph import graph
from backend.report import generate_report


router = APIRouter(
    prefix="/risk",
    tags=["Risk Assessment"],
)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/analyze", response_model=RiskResponse)
def analyze_risk(request: RiskRequest):
    result = graph.invoke({
        "risk_description": request.description,
        "analysis": "",
        "severity": "",
        "llm_severity": "",
        "evidence_completeness": 0.0,
        "present_evidence": [],
        "missing_evidence": [],
        "reason_code": "",
        "confidence": 0.0,
        "supporting_evidence": [],
        "weakening_evidence": [],
        "recommendations": [],
        "provider_used": "",
        "verification_provider": "",
        "verification_notes": "",
        "needs_human_review": False,
    })

    report = generate_report(result)

    return RiskResponse(
        **result,
        report=report,
        case_id="N/A",
    )