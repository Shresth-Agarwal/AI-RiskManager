import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import json
from backend.graph import graph

DATA_DIR = Path(__file__).parent.parent / "data"

def run_eval(filename: str, label: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        cases = json.load(f)
    reason_correct = severity_correct = human_review_count = 0
    for case in cases:
        result = graph.invoke({
            "risk_description": case["description"],
            "analysis": "",
            "severity": "",
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
        print(
            case["case_id"],
            "EXPECTED:", case["expected_reason_code"], case["expected_severity"],
            "GOT:", result["reason_code"], result["severity"],
            "CONF:", result["confidence"],
            "EVIDENCE:", result["evidence_completeness"],
            "PRESENT:", result["present_evidence"],      
            "MISSING:", result["missing_evidence"],       
            "PROVIDER:", result["provider_used"],         
            "VERIFY_PROVIDER:", result["verification_provider"],
            "SUPPORTING:", result["supporting_evidence"],  
            "REVIEW:", result["needs_human_review"],
            "LLM_SEVERITY:", result["llm_severity"]
        )
        if result["reason_code"] == case["expected_reason_code"]:
            reason_correct += 1
        if result["severity"] == case["expected_severity"]:
            severity_correct += 1
        if result["needs_human_review"]:
            human_review_count += 1

    n = len(cases)
    print(f"\n=== {label} (n={n}) ===")
    print(f"Reason-code accuracy: {reason_correct/n*100:.1f}%")
    print(f"Severity accuracy: {severity_correct/n*100:.1f}%")
    print(f"Flagged for human review: {human_review_count}/{n}")

if __name__ == "__main__":
    run_eval("risk_cases.json", "Dev set (prompt-tuned)")
    run_eval("heldout_cases.json", "Held-out set (untouched)")