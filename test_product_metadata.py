import json

from app.tools.product_normailzer import normalize_product

with open("samsung_s22.json", "r", encoding="utf-8") as file:
    api_response = json.load(file)

result = normalize_product(api_response)
structured = result["structured"]

print("Model:", structured.get("model"))
print("RAM:", structured.get("ram"))
print("RAM MB:", structured.get("ram_mb"))
print("Storage:", structured.get("storage"))
print("Storage GB:", structured.get("storage_gb"))
print("Release year:", structured.get("release_year"))