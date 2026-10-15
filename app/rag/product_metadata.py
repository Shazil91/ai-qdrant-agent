import re
from typing import Any


def parse_ram_mb(value: Any) -> int | None:
    """Convert a RAM value such as 8 GB or 512 MB to MB."""
    if not isinstance(value, str):
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(GB|MB)\b",
        value,
        re.IGNORECASE,
    )

    if not match:
        return None

    amount = float(match.group(1))
    unit = match.group(2).upper()

    if unit == "GB":
        return round(amount * 1024)

    return round(amount)


def parse_storage_gb(value: Any) -> list[int]:
    """Extract storage capacities, including multiple options."""
    if not isinstance(value, str):
        return []

    capacities = []

    for match in re.finditer(
        r"(\d+(?:\.\d+)?)\s*(TB|GB|MB)\b",
        value,
        re.IGNORECASE,
    ):
        amount = float(match.group(1))
        unit = match.group(2).upper()

        if unit == "TB":
            amount *= 1024
        elif unit == "MB":
            amount /= 1024

        capacities.append(round(amount))

    return sorted(set(capacities))


def parse_release_year(value: Any) -> int | None:
    """Extract a four-digit year from an ISO-style date."""
    if not isinstance(value, str):
        return None

    match = re.match(r"^\s*(\d{4})-\d{2}-\d{2}", value)

    if not match:
        return None

    return int(match.group(1))


def build_product_metadata(payload: dict) -> dict:
    """Build additional searchable metadata from a product payload."""
    metadata = {}

    ram_mb = parse_ram_mb(payload.get("ram"))
    if ram_mb is not None:
        metadata["ram_mb"] = ram_mb

    storage_gb = parse_storage_gb(payload.get("storage"))
    if storage_gb:
        metadata["storage_gb"] = storage_gb

    release_year = parse_release_year(payload.get("release_date"))
    if release_year is not None:
        metadata["release_year"] = release_year

    return metadata
