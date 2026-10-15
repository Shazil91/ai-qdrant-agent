import json
from pathlib import Path

from app.tools.product_normalizer import normalize_product

# Save the successful product-details API response as:
# samsung_s22.json in your project root.

file_path = Path("samsung_s22.json")

with file_path.open("r", encoding="utf-8") as file:
    api_response = json.load(file)

product = normalize_product(api_response)

print("\n--- STRUCTURED PRODUCT DATA ---")
print(json.dumps(
    product["structured"],
    indent=2,
    ensure_ascii=False,
))

print("\n--- SEARCHABLE PRODUCT TEXT ---")
print(product["text"][:5000])