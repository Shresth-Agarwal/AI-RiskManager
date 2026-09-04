from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        description="Natural-language description of the transaction dispute",
    )


class RiskResponse(BaseModel):
    case_id: str
    amount: float | None = None
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


class BatchRiskCase(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        description="Natural-language description of the transaction dispute",
    )
    amount: float = Field(
        ...,
        ge=0,
        description="Disputed transaction amount",
    )


class BatchRiskRequest(BaseModel):
    cases: list[BatchRiskCase]


class BatchRiskResponse(BaseModel):
    results: list[RiskResponse]
    total_cases: int
    total_amount: float
    severity_distribution: dict[str, int]
    reason_distribution: dict[str, int]
    human_review_rate: float
    average_evidence_completeness: float