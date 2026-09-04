from api.schemas import (
    RiskRequest,
    RiskResponse,
    BatchRiskRequest,
    BatchRiskResponse,
)
from fastapi import APIRouter
import uuid
from backend.graph import graph
from backend.report import generate_report, save_report

batch_router = APIRouter(
    prefix="/risk",
    tags=["Batch Risk Assessment"],
)

@batch_router.post("/batch", response_model=BatchRiskResponse)
def analyze_batch(request: BatchRiskRequest):
    results = []

    for case in request.cases:
        result = graph.invoke({
            "risk_description": case.description,
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

        save_report(report, case_id)

        results.append(
            RiskResponse(
                **result,
                report=report,
                case_id=case_id,
                amount=case.amount,
            )
        )
    if not results:
        return BatchRiskResponse(
            results=[], total_cases=0, total_amount=0,
            severity_distribution={"high": 0, "medium": 0, "low": 0},
            reason_distribution={}, human_review_rate=0.0,
            average_evidence_completeness=0.0,
        )
    total_cases = len(results)
    total_amount = sum(case.amount for case in request.cases)

    severity_distribution = {
        "high": sum(r.severity == "high" for r in results),
        "medium": sum(r.severity == "medium" for r in results),
        "low": sum(r.severity == "low" for r in results),
    }

    reason_distribution = {}

    for result in results:
        reason = result.reason_code
        reason_distribution[reason] = (
            reason_distribution.get(reason, 0) + 1
        )

    human_review_rate = (
        sum(r.needs_human_review for r in results) / total_cases
    )

    average_evidence_completeness = (
        sum(r.evidence_completeness for r in results) / total_cases
    )

    return BatchRiskResponse(
        results=results,
        total_cases=total_cases,
        total_amount=total_amount,
        severity_distribution=severity_distribution,
        reason_distribution=reason_distribution,
        human_review_rate=human_review_rate,
        average_evidence_completeness=average_evidence_completeness,
    )