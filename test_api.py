
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Samsung Galaxy S22 product ID from your earlier search results
product_id = "63e96260ff7af4b68a303f3f"

url = f"https://api.techspecs.io/v5/products/{product_id}"

headers = {
    "x-api-id": os.getenv("API_ID"),
    "x-api-key": os.getenv("TEXTSPECS_API_KEY"),
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

    print("Status:", response.status_code)
    response.raise_for_status()

    data = response.json()

    # Save the API response in your project root
    output_file = Path("samsung_s22.json")
    output_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Product data saved to: {output_file.resolve()}")
    print("Response preview:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])

except requests.RequestException as exc:
    print("API request failed:", exc)

except ValueError as exc:
    print("Could not parse the API response as JSON:", exc)