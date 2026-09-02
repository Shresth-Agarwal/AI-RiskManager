import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.environ.get(
    "API_BASE_URL",
    "http://localhost:8000",
)


def analyze_case(description: str) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/risk/analyze",
        json={"description": description},
        timeout=120,
    )

    resp.raise_for_status()
    return resp.json()


def check_health() -> bool:
    try:
        resp = requests.get(
            f"{API_BASE_URL}/risk/health",
            timeout=5,
        )

        return resp.status_code == 200

    except requests.RequestException:
        return False