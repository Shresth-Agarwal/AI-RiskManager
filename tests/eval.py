import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from backend.graph import graph

DATA_PATH = Path(__file__).parent.parent / "data" / "risk_cases.json"


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    correct = 0

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

        predicted = result["reason_code"]
        expected = case["expected_reason_code"]

        passed = predicted == expected

        if passed:
            correct += 1

        print(
            f"{case['case_id']} | "
            f"Expected: {expected:<15} | "
            f"Predicted: {predicted:<15} | "
            f"{'PASS' if passed else 'FAIL'}"
        )
        if not passed:
            print(f"  Description: {case['description']}")
            print(f"  Analysis: {result['analysis']}")
            print()

    accuracy = correct / len(cases) * 100

    print("\n--------------------")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Passed: {correct}/{len(cases)}")


if __name__ == "__main__":
    main()