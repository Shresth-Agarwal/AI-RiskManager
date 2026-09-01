# backend/evidence_requirements.py
# Simplified from Visa/Mastercard Compelling Evidence guidance — 
# not legal advice, just a structured approximation for demo purposes.

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

def check_evidence_completeness(
    reason_code: str,
    supporting_evidence: list[str]
) -> dict:

    required = EVIDENCE_REQUIREMENTS.get(reason_code, [])

    if not required:
        return {
            "completeness": 0.0,
            "missing": [],
            "present": []
        }

    evidence_text = " ".join(supporting_evidence).lower()

    keywords = {
        "delivery_confirmation": [
            "delivery",
            "delivered",
            "delivery confirmation",
        ],
        "tracking_matches_shipping_address": [
            "tracking",
            "shipping address",
            "delivery address",
        ],
        "signature_or_photo_proof": [
            "signature",
            "photo",
            "photograph",
        ],
        "product_listing_screenshot": [
            "product listing",
            "listing",
            "advertised",
        ],
        "customer_photos_or_description_of_issue": [
            "customer photo",
            "customer photograph",
            "damage",
            "different specifications",
        ],
        "pre_shipment_condition_proof": [
            "pre-shipment",
            "before shipment",
            "before shipping",
        ],
        "transaction_ids_for_both_charges": [
            "transaction id",
            "transaction ids",
            "two transactions",
        ],
        "timestamp_proximity": [
            "timestamp",
            "within two minutes",
            "two minutes",
        ],
        "authentication_record": [
            "authentication",
            "otp",
            "3-d secure",
            "3ds",
        ],
        "device_fingerprint_match": [
            "device",
            "device fingerprint",
            "registered device",
        ],
        "purchase_history_consistency": [
            "previous purchases",
            "purchase history",
            "similar purchases",
        ],
    }

    present = []

    for requirement in required:
        if any(
            keyword in evidence_text
            for keyword in keywords.get(requirement, [])
        ):
            present.append(requirement)

    missing = [
        requirement
        for requirement in required
        if requirement not in present
    ]

    return {
        "completeness": len(present) / len(required),
        "present": present,
        "missing": missing,
    }