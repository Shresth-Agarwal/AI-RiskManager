from fastapi import APIRouter
import uuid
from api.schemas import RiskRequest, RiskResponse
from backend.graph import graph
from backend.report import generate_report, save_report


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
        "evidence_justifications": {}, 
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

    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"

    report = generate_report(
        result,
        case_id=case_id,
    )

    save_report(
        report,
        case_id,
    )

    return RiskResponse(
        **result,
        report=report,
        case_id=case_id,
    )