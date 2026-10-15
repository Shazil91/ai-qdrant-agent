import os
import requests
from dotenv import load_dotenv

import json
from pathlib import Path
load_dotenv()

API_ID = os.getenv("API_ID")
API_KEY = os.getenv("TEXTSPECS_API_KEY")

# Samsung Galaxy S22 product ID from your search response
product_id = "63e96260ff7af4b68a303f3f"

url = f"https://api.techspecs.io/v5/products/{product_id}"

headers = {
    "x-api-id": API_ID,
    "x-api-key": API_KEY,
}

params = {
    "lang": "en",
    "keepCasing": "true",
}

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    product = response.json()
    

    Path("samsung_s22.json").write_text(
    json.dumps(product, indent=2, ensure_ascii=False),
    encoding="utf-8",
    )

    print("Saved API response to samsung_s22.json")

    print("Product details retrieved successfully!")
    print(response.text[:15000])

except requests.RequestException as e:
    print(f"API request failed: {e}")