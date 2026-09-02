from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from backend.llm_manager import LLMManager
from backend.evidence_requirements import check_evidence_completeness, check_evidence_completeness_grounded

import json

llm = LLMManager()

RISK_SYSTEM_PROMPT = """
You are a payment risk analyst.

Given a transaction dispute case, assess the case and return ONLY valid JSON.

Use exactly this structure:

{
  "severity": "low | medium | high",
  "reason_code": "fraud | not-received | not-as-described | duplicate | other",
  "confidence": 0.0,
  "supporting_evidence": ["evidence item 1"],
  "weakening_evidence": ["evidence item 1"],
  "recommendations": ["recommendation 1"]
}

Reason-code rules:
- fraud: Use when the customer explicitly claims the transaction was unauthorized,
  even if the merchant has strong evidence that the transaction was legitimate.
- not-received: Use when the customer claims they did not receive the product/service.
- not-as-described: Use when the customer says the product/service differs from what was promised or described.
- duplicate: Use when the same transaction appears to have been charged more than once.
- other: Use when the dispute does not clearly match any of the above categories.
  A customer saying they "do not recognize" a transaction by itself is NOT enough
  to classify it as fraud unless the case explicitly indicates unauthorized use.
  
Severity rules:
- Severity reflects the financial and reputational impact to the merchant
  if this dispute is decided against them.
- high: transaction amount is large (₹10,000+) AND evidence favors the customer,
  OR the case involves a repeat/pattern risk.
- medium: moderate amount, OR evidence is mixed/conflicting.
- low: small amount AND evidence clearly favors the merchant, OR the dispute
  is vague/unsubstantiated.
- Duplicate charges with clear, strong evidence are typically low severity —
  they are straightforward to resolve and rarely result in merchant loss.

Important:
- Classify based primarily on the customer's stated dispute reason.
- Evidence affects severity and confidence, but does not automatically change the reason code.
- Only use facts provided in the case.
- Do not invent policies, regulations, or evidence.
- confidence must be between 0 and 1.
- Be concise.
- Return JSON only. No Markdown.
"""


class RiskState(TypedDict):
    risk_description: str
    analysis: str
    severity: str
    llm_severity: str
    reason_code: str
    confidence: float
    evidence_completeness: float
    present_evidence: list[str]
    missing_evidence: list[str]
    evidence_justifications: dict
    supporting_evidence: list[str]
    weakening_evidence: list[str]
    recommendations: list[str]
    provider_used: str
    verification_provider: str
    verification_notes: str
    needs_human_review: bool

def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()

def analyze_risk(state: RiskState):
    description = state["risk_description"]

    result = llm.generate(
        prompt=description,
        system=RISK_SYSTEM_PROMPT
    )

    try:
        parsed = json.loads(_clean_json(result.text))

        return {
            "analysis": result.text,
            "llm_severity": parsed.get("severity", "medium"),
            "severity": parsed.get("severity", "medium"),
            "reason_code": parsed.get("reason_code", "other"),
            "confidence": float(parsed.get("confidence", 0.0)),
            "supporting_evidence": parsed.get("supporting_evidence", []),
            "weakening_evidence": parsed.get("weakening_evidence", []),
            "recommendations": parsed.get("recommendations", []),
            "provider_used": result.provider,
        }

    except (json.JSONDecodeError, ValueError, TypeError):
        print(
            f"[analyze_risk] Invalid JSON from {result.provider}:\n"
            f"{result.text}"
        )

        return {
            "analysis": "Analysis failed: provider returned invalid JSON.",
            "llm_severity": "medium",
            "severity": "medium",
            "reason_code": "other",
            "confidence": 0.0,
            "supporting_evidence": [],
            "weakening_evidence": [],
            "recommendations": [],
            "provider_used": result.provider,
        }


def check_evidence(state: RiskState):
    result = check_evidence_completeness_grounded(
        llm, state["risk_description"], state["reason_code"]
    )
    if result is None:
        result = check_evidence_completeness(
            state["reason_code"], state["supporting_evidence"]
        )
        result["justifications"] = {}

    return {
        "evidence_completeness": result["completeness"],
        "present_evidence": result["present"],
        "missing_evidence": result["missing"],
        "evidence_justifications": result.get("justifications", {}),
        "severity": state["llm_severity"],
    }

def route_after_evidence(state: RiskState):
    if state["reason_code"] == "other":
        return "verify_risk"

    if (
        state["confidence"] < 0.7
        or state["evidence_completeness"] < 0.5
    ):
        return "verify_risk"

    return END

VERIFY_SYSTEM_PROMPT = """
You are a second-pass reviewer checking another analyst's risk assessment.
Given the original case and their assessment, either CONFIRM it or FLAG it
for human review. Return ONLY valid JSON:

{
  "verified": true | false,
  "verification_notes": "why you agree or disagree",
  "needs_human_review": true | false
}

Only use facts in the case. Do not invent evidence.
"""

def verify_risk(state: RiskState):
    review_prompt = (
        f"Case: {state['risk_description']}\n\n"
        f"Original assessment: {state['analysis']}"
    )
    result = llm.generate(
        prompt=review_prompt,
        system=VERIFY_SYSTEM_PROMPT,
        exclude=[state["provider_used"]]
    )
    try:
        parsed = json.loads(_clean_json(result.text))
    except json.JSONDecodeError:
        print(f"[Verification] Invalid JSON from {result.provider}:")
        print(result.text)
        return {
            "verification_notes": "Verification failed because the provider returned invalid JSON.",
            "verification_provider": result.provider,
            "needs_human_review": True,
        }
    return {
        "verification_notes": parsed.get(
            "verification_notes",
            "Verification response was incomplete."
        ),
        "verification_provider": result.provider,
        "needs_human_review": parsed.get("needs_human_review", True),
    }

graph_builder = StateGraph(RiskState)
graph_builder.add_node("analyze_risk", analyze_risk)
graph_builder.add_node("check_evidence", check_evidence)
graph_builder.add_node("verify_risk", verify_risk)

graph_builder.add_edge(START, "analyze_risk")
graph_builder.add_edge("analyze_risk", "check_evidence")

graph_builder.add_conditional_edges("check_evidence", route_after_evidence, {
    "verify_risk": "verify_risk",
    END: END,
})
graph_builder.add_edge("verify_risk", END)
graph = graph_builder.compile()
