import json
import sys
from pathlib import Path


sys.path.insert(
    0,
    str(Path(__file__).parent.parent),
)


from backend.llm_manager import LLMManager
from backend.evidence_requirements import (
    check_evidence_completeness,
    check_evidence_completeness_grounded,
)


llm = LLMManager()

DATA_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "evidence_grounding_cases.json"
)


def collapse(status):
    """
    Old matcher is binary, so UNKNOWN and ABSENT
    are both treated as missing for comparison.
    """
    return (
        "present"
        if status == "present"
        else "missing"
    )


with open(DATA_PATH, encoding="utf-8") as file:
    cases = json.load(file)


old_correct = 0
new_correct = 0
total_items = 0


for case in cases:

    reason_code = case["reason_code"]
    description = case["description"]
    expected = case["expected"]

    old = check_evidence_completeness(
        reason_code,
        [description],
    )

    new = check_evidence_completeness_grounded(
        llm,
        description,
        reason_code,
    )

    print(
        f"\n{case['case_id']} "
        f"({reason_code})"
    )

    if new is None:
        print("  NEW GROUNDING FAILED")
        continue

    for item, expected_status in expected.items():

        old_status = (
            "present"
            if item in old["present"]
            else "missing"
        )

        new_status = (
            new["justifications"]
            .get(item, {})
            .get("status", "unknown")
        )

        old_ok = (
            old_status
            == collapse(expected_status)
        )

        new_ok = (
            new_status
            == expected_status
        )

        old_correct += int(old_ok)
        new_correct += int(new_ok)
        total_items += 1

        print(
            f"  {item:35s} "
            f"expected={expected_status:8s} "
            f"old={old_status:8s}"
            f"({'OK' if old_ok else 'X'}) "
            f"new={new_status:8s}"
            f"({'OK' if new_ok else 'X'})"
        )

        if not new_ok:
            justification = (
                new["justifications"]
                .get(item, {})
                .get("justification", "")
            )

            print(
                f"    justification: {justification}"
            )


print("\n=== RESULTS ===")

print(
    f"Old heuristic: "
    f"{old_correct}/{total_items} "
    f"({old_correct / total_items:.0%})"
)

print(
    f"New grounder: "
    f"{new_correct}/{total_items} "
    f"({new_correct / total_items:.0%})"
)