# backend/evidence_requirements.py

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
        "authentication_record",  # OTP/3DS
        "device_fingerprint_match",
        "purchase_history_consistency",
    ],
    "other": [],  # no defined evidence bar — always needs human review
}

def check_evidence_completeness(reason_code: str, supporting_evidence: list[str]):
    required = EVIDENCE_REQUIREMENTS.get(reason_code, [])

    if not required:
        return {
            "completeness": 0.0,
            "present": [],
            "missing": [],
        }

    # Combine all evidence into one lowercase text block
    evidence_text = " ".join(supporting_evidence).lower()

    present = []
    missing = []

    # Phrases that indicate the evidence is explicitly absent
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

    for item in required:
        # Convert schema name into searchable words
        keywords = item.replace("_", " ").lower()

        # Check whether the evidence is explicitly described as missing
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

    completeness = len(present) / len(required)

    return {
        "completeness": completeness,
        "present": present,
        "missing": missing,
    }