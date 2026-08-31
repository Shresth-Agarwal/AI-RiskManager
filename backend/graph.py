from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from backend.llm_manager import LLMManager
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
    reason_code: str
    confidence: float
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
            "severity": "medium",
            "reason_code": "other",
            "confidence": 0.0,
            "supporting_evidence": [],
            "weakening_evidence": [],
            "recommendations": [],
            "provider_used": result.provider,
        }

def route_by_confidence(state: RiskState):
    return "verify_risk" if state["confidence"] < 0.7 else END

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
        "verification_notes": parsed["verification_notes"],
        "verification_provider": result.provider,
        "needs_human_review": parsed["needs_human_review"]
    }

graph_builder = StateGraph(RiskState)
graph_builder.add_node("analyze_risk", analyze_risk)
graph_builder.add_node("verify_risk", verify_risk)
graph_builder.add_edge(START, "analyze_risk")
graph_builder.add_conditional_edges("analyze_risk", route_by_confidence, {
    "verify_risk": "verify_risk",
    END: END,
})
graph_builder.add_edge("verify_risk", END)
graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
    "risk_description": (
        "Customer disputes a ₹12,000 transaction claiming the purchase was not authorized. "
        "The merchant has no delivery confirmation, no customer communication history, "
        "and no clear authentication record. The customer has previously made one dispute "
        "but the available evidence is incomplete."
    ),
    "analysis": "",
    "severity": "",
    "reason_code": "",
    "confidence": 0.0,
    "supporting_evidence": [],
    "weakening_evidence": [],
    "recommendations": [],
    "provider_used": "",
    "verification_notes": "",
    "verification_provider": "",
    "needs_human_review": False
    })
    print(result)