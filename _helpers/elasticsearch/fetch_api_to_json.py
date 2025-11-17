import os
import json
from pathlib import Path

from dotenv import load_dotenv
import httpx

load_dotenv()

BUSINESSES_API_RETRIEVAL_URL = os.getenv("BUSINESSES_API_RETRIEVAL_URL")
OUTPUT_FILE = Path(__file__).parent / "api_businesses.json"


def fetch_from_api():
    """Fetch businesses data from API endpoint."""
    response = httpx.get(BUSINESSES_API_RETRIEVAL_URL)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    data = fetch_from_api()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(data)} records to {OUTPUT_FILE}")
