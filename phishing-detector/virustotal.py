import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VT_API_KEY", "")
BASE = "https://www.virustotal.com/api/v3"
_MAX_RETRIES = 2


def virustotal_check(url: str) -> dict:
    """
    Submits URL for analysis and returns engine results.
    Returns dict with 'stats' and 'engines' keys, or 'error' on failure.
    """
    if not VT_API_KEY:
        return {"error": "No VT_API_KEY found — add it to your .env file"}

    headers = {"x-apikey": VT_API_KEY}

    # Submit URL
    r = requests.post(f"{BASE}/urls", headers=headers, data={"url": url}, timeout=15)

    if r.status_code == 204:
        return {"error": "VirusTotal quota exceeded (429). Try again in a minute."}
    if r.status_code != 200:
        return {"error": f"Submission failed: HTTP {r.status_code}"}

    analysis_id = r.json()["data"]["id"]

    # Poll for results with retry
    delay = 2
    for attempt in range(_MAX_RETRIES + 1):
        time.sleep(delay)
        r2 = requests.get(
            f"{BASE}/analyses/{analysis_id}", headers=headers, timeout=15
        )
        if r2.status_code == 204:
            if attempt < _MAX_RETRIES:
                delay = min(delay * 2, 60)
                continue
            return {"error": "VirusTotal quota exceeded while fetching results."}
        if r2.status_code != 200:
            return {"error": f"Fetch failed: HTTP {r2.status_code}"}

        data = r2.json()["data"]["attributes"]
        if data.get("status") == "queued" and attempt < _MAX_RETRIES:
            delay = min(delay * 2, 60)
            continue

        return {
            "stats": data["stats"],
            "engines": {
                k: v["result"]
                for k, v in data["results"].items()
                if v["result"] not in (None, "unrated")
            },
        }

    return {"error": "Analysis timed out — try again shortly."}
