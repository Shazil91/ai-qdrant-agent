
import re


def parse_product_query(query: str) -> dict:
    """
    Extract supported exact-match product filters from a query.

    Supported filters:
    - Brand
    - RAM in GB or MB
    - Storage in GB
    - Release year
    """

    filters = {}
    text = query.strip()

    # Brand: currently recognize Samsung in our product catalog.
    if re.search(r"\bsamsung\b", text, re.IGNORECASE):
        filters["brand"] = "Samsung"

    # RAM: examples: "8 GB RAM", "512 MB RAM"
    ram_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(GB|MB)\s+(?:of\s+)?RAM\b",
        text,
        re.IGNORECASE,
    )

    if ram_match:
        amount = float(ram_match.group(1))
        unit = ram_match.group(2).upper()

        filters["ram_mb"] = round(
            amount * 1024 if unit == "GB" else amount
        )

    # Storage: examples: "128 GB storage", "1 TB storage"
    storage_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(TB|GB|MB)\s+storage\b",
        text,
        re.IGNORECASE,
    )

    if storage_match:
        amount = float(storage_match.group(1))
        unit = storage_match.group(2).upper()

        if unit == "TB":
            amount *= 1024
        elif unit == "MB":
            amount /= 1024

        filters["storage_gb"] = round(amount)

    # Release year: examples: "released in 2012"
    year_match = re.search(
        r"\b(?:released|release|launched)\s+(?:in\s+)?(19\d{2}|20\d{2})\b",
        text,
        re.IGNORECASE,
    )

    if year_match:
        filters["release_year"] = int(year_match.group(1))

    return filters
