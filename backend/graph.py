from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm_manager import LLMManager
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
  "supporting_evidence": ["evidence item 1", "evidence item 2"],
  "weakening_evidence": ["evidence item 1", "evidence item 2"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}

Rules:
- severity must be exactly low, medium, or high.
- reason_code must be one of the listed values.
- confidence must be a number between 0 and 1.
- Only use facts provided in the case.
- Do not invent policies, regulations, or evidence.
- supporting_evidence should contain evidence that supports the merchant's position.
- weakening_evidence should contain evidence that weakens the merchant's position.
- recommendations should identify useful next steps for evaluating or strengthening the case.
- Be concise.
- Return JSON only. No Markdown and no explanation outside the JSON.
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
    except json.JSONDecodeError:
        raise ValueError(
            f"LLM returned invalid JSON:\n{result.text}"
        )

    return {
        "analysis": result.text,
        "severity": parsed["severity"],
        "reason_code": parsed["reason_code"],
        "confidence": float(parsed["confidence"]),
        "supporting_evidence": parsed["supporting_evidence"],
        "weakening_evidence": parsed["weakening_evidence"],
        "recommendations": parsed["recommendations"],
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
    parsed = json.loads(_clean_json(result.text))
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