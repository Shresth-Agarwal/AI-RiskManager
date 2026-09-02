import json


EVIDENCE_REQUIREMENTS = {
    "not-received": [
        "delivery_confirmation",
        "tracking_matches_shipping_address",
        "signature_or_photo_proof",
    ],
    "not-as-described": [
        "product_listing_screenshot",
        "customer_photos_or_description_of_issue",
        "pre_shipment_condition_proof",
    ],
    "duplicate": [
        "transaction_ids_for_both_charges",
        "timestamp_proximity",
    ],
    "fraud": [
        "authentication_record",
        "device_fingerprint_match",
        "purchase_history_consistency",
    ],
    "other": [],
}


EVIDENCE_DESCRIPTIONS = {
    "not-received": {
        "delivery_confirmation":
            "confirmation that the package was delivered",
        "tracking_matches_shipping_address":
            "tracking showing the package went to the address on file",
        "signature_or_photo_proof":
            "a signature or photo proof of delivery",
    },

    "not-as-described": {
        "product_listing_screenshot":
            "the original product listing or description shown to the customer",

        "customer_photos_or_description_of_issue":
            "supporting customer photos or a detailed description documenting the specific product problem",

        "pre_shipment_condition_proof":
            "proof of the product's condition before shipping",
    },

    "duplicate": {
        "transaction_ids_for_both_charges":
            "transaction IDs for both charges",
        "timestamp_proximity":
            "timestamps showing both charges happened close together",
    },

    "fraud": {
        "authentication_record":
            "an authentication record such as OTP or 3-D Secure",
        "device_fingerprint_match":
            "a device fingerprint matching the customer's known device",
        "purchase_history_consistency":
            "evidence of prior purchase history with the merchant",
    },
}

GROUNDING_SYSTEM_PROMPT = '''
You are an evidence auditor.

Given a dispute case and a list of required evidence items, determine for
EACH item whether the case establishes that the evidence is:

- "present": the case explicitly states that this specific evidence exists,
  was provided, or was obtained.

- "absent": the case explicitly states that this specific evidence does not
  exist, was not provided, was unavailable, or could not be obtained.

- "unknown": the case does not establish whether this specific evidence
  exists or not.

IMPORTANT DISTINCTION:

"unknown" is NOT the same as "absent".

If the case simply does not mention an evidence item, classify it as
"unknown".

Statements such as:
- "No further details were provided"
- "The case contains no additional information"
- "The merchant did not mention..."
- "There is no information about..."
do NOT prove that the evidence itself is absent. These should normally be
"unknown".

Only use "absent" when the case explicitly refers to the evidence itself
and says that it was not provided, does not exist, is unavailable, or could
not be obtained.

Evidence must match the required item specifically. Do not mark an item
"present" merely because the case contains related or supporting facts.

Important distinction for delivery evidence:

"tracking showing the shipment reached the customer's address" is NOT the
same as "delivery confirmation".

If the case only states that tracking/courier records show the shipment
reached or was routed to the address, mark:
- tracking_matches_shipping_address = present
- delivery_confirmation = unknown

Only mark delivery_confirmation = present when the case explicitly states
that delivery was confirmed, completed, delivered, or otherwise provides
specific confirmation of delivery.

For example:
- "Shipment reached the exact address" supports
  tracking_matches_shipping_address = present.
- It does NOT by itself prove
  delivery_confirmation = present.

If the case says:
"The merchant did not provide delivery confirmation, tracking information,
or signature/photo proof"
then ALL THREE corresponding evidence items are "absent".

Only use facts explicitly stated in the case.
Never infer evidence that is not stated.

Return ONLY valid JSON:

{
  "item_key": {
    "status": "present|absent|unknown",
    "justification": "short explanation based only on the case"
  }
}

No markdown. No extra text.'''


def _clean_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")

        if text.lower().startswith("json"):
            text = text[4:]

    return text.strip()


def ground_evidence(
    llm,
    risk_description: str,
    reason_code: str,
):
    descriptions = EVIDENCE_DESCRIPTIONS.get(
        reason_code,
        {},
    )

    if not descriptions:
        return {}

    items_text = "\n".join(
        f"- {key}: {description}"
        for key, description in descriptions.items()
    )

    prompt = (
        f"Case:\n{risk_description}\n\n"
        f"Required evidence items:\n{items_text}"
    )

    try:
        result = llm.generate(
            prompt=prompt,
            system=GROUNDING_SYSTEM_PROMPT,
        )

        parsed = json.loads(
            _clean_json(result.text)
        )

    except (
        Exception
    ) as exc:
        print(
            f"[Evidence Grounder] Failed: {exc}"
        )
        return None

    cleaned = {}

    for key in descriptions:
        entry = parsed.get(key, {})

        if not isinstance(entry, dict):
            entry = {}

        status = entry.get("status", "unknown")

        if status not in (
            "present",
            "absent",
            "unknown",
        ):
            status = "unknown"

        cleaned[key] = {
            "status": status,
            "justification": entry.get(
                "justification",
                "",
            ),
        }

    return cleaned


def check_evidence_completeness_grounded(
    llm,
    risk_description: str,
    reason_code: str,
):
    required = list(
        EVIDENCE_DESCRIPTIONS.get(
            reason_code,
            {},
        ).keys()
    )

    if not required:
        return {
            "completeness": 0.0,
            "present": [],
            "missing": [],
            "justifications": {},
        }

    grounded = ground_evidence(
        llm,
        risk_description,
        reason_code,
    )

    if grounded is None:
        return None

    present = [
        key
        for key, value in grounded.items()
        if value["status"] == "present"
    ]

    missing = [
        key
        for key in required
        if key not in present
    ]

    return {
        "completeness": (
            len(present) / len(required)
        ),
        "present": present,
        "missing": missing,
        "justifications": grounded,
    }


# Existing heuristic matcher — kept as fallback

def check_evidence_completeness(
    reason_code: str,
    supporting_evidence: list[str],
):
    required = EVIDENCE_REQUIREMENTS.get(
        reason_code,
        [],
    )

    if not required:
        return {
            "completeness": 0.0,
            "present": [],
            "missing": [],
        }

    evidence_text = " ".join(
        supporting_evidence
    ).lower()

    negative_phrases = [
        "no ",
        "not ",
        "without ",
        "missing ",
        "lack of ",
        "lacks ",
        "unavailable",
        "unavailable evidence",
    ]

    present = []
    missing = []

    for item in required:
        keywords = item.replace(
            "_",
            " ",
        ).lower()

        is_negative = any(
            phrase + keywords in evidence_text
            for phrase in negative_phrases
        )

        if is_negative:
            missing.append(item)

        elif keywords in evidence_text:
            present.append(item)

        else:
            missing.append(item)

    completeness = (
        len(present) / len(required)
    )

    return {
        "completeness": completeness,
        "present": present,
        "missing": missing,
    }