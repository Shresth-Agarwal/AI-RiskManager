from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        description="Natural-language description of the transaction dispute",
    )


class RiskResponse(BaseModel):
    case_id: str
    severity: str
    llm_severity: str
    reason_code: str
    confidence: float
    evidence_completeness: float
    present_evidence: list[str]
    supporting_evidence: list[str]
    weakening_evidence: list[str]
    missing_evidence: list[str]
    recommendations: list[str]
    needs_human_review: bool
    verification_notes: str
    verification_provider: str
    provider_used: str
    report: str
