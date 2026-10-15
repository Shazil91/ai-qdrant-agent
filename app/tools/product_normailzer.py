import json
import re
from typing import Any
from app.rag.product_metadata import build_product_metadata

def is_missing(value: Any) -> bool:
    """Identify empty or placeholder values returned by the API."""
    if value is None:
        return True

    if isinstance(value, str):
        cleaned = value.strip().lower()

        if not cleaned:
            return True

        placeholders = {
            "n/a",
            "na",
            "none",
            "null",
            "not available",
            "not specified",
            "the data will be added shortly",
        }

        return cleaned in placeholders

    return False


def flatten_specs(
    value: Any,
    prefix: str = "",
) -> list[str]:
    """Convert nested dictionaries and lists into readable text."""
    lines = []

    if isinstance(value, dict):
        for key, item in value.items():
            if is_missing(item):
                continue

            label = f"{prefix} {key}".strip()

            if isinstance(item, (dict, list)):
                lines.extend(flatten_specs(item, label))
            else:
                lines.append(f"{label}: {item}")

    elif isinstance(value, list):
        for item in value:
            lines.extend(flatten_specs(item, prefix))

    elif not is_missing(value):
        lines.append(f"{prefix}: {value}")

    return lines


def find_field(data: Any, *field_names: str) -> Any:
    """Find a field recursively, ignoring capitalization."""
    if isinstance(data, dict):
        normalized_names = {
            name.casefold() for name in field_names
        }

        for key, value in data.items():
            if key.casefold() in normalized_names:
                if not is_missing(value):
                    return value

        for value in data.values():
            result = find_field(value, *field_names)

            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_field(item, *field_names)

            if result is not None:
                return result

    return None

def find_product_model(product_data: dict, product_info: dict) -> Any:
    """Prefer specific product-name fields over a generic model field."""

    # Check more descriptive names first.
    preferred_fields = [
        "Marketing Name",
        "Commercial Name",
        "Product Name",
        "Model Name",
        "Title",
    ]

    for field in preferred_fields:
        value = find_field(product_data, field)

        if not is_missing(value):
            return value

    # Fall back to the standard TechSpecs Product.Model field.
    return product_info.get("Model")


def normalize_product(api_response: dict) -> dict:
    """Normalize a TechSpecs product-details response."""

    product_data = api_response.get("data", api_response)

    if not isinstance(product_data, dict):
        raise ValueError("Unexpected TechSpecs response format")

    product_info = product_data.get("Product", {})
    if not isinstance(product_info, dict):
        product_info = {}

    inside = product_data.get("Inside", {})
    if not isinstance(inside, dict):
        inside = {}

    processor_info = inside.get("Processor", {})
    ram_info = inside.get("RAM", {})
    storage_info = inside.get("Storage", {})
    design = product_data.get("Design", {})
    battery_info = design.get("Battery", {})
    display_info = design.get("Display", {})

    # Some API versions may place display and battery elsewhere.
    # Fall back to recursive lookup if the expected section is absent.
    if not isinstance(display_info, dict) or not display_info:
        display_info = find_field(product_data, "Display") or {}

    if not isinstance(battery_info, dict) or not battery_info:
        battery_info = find_field(product_data, "Battery") or {}

    def value_or_none(value):
        return None if is_missing(value) else value

    structured = {
        "product_id": product_data.get("_id")
        or product_info.get("id"),
        "brand": product_info.get("Brand"),
        "model": find_product_model(product_data, product_info),
        "version": product_info.get("Version"),
        "category": product_info.get("Category"),
        "manufacturer": product_info.get("Manufacturer"),
        "region": product_info.get("Region"),
        "country": product_info.get("Country"),
        "release_date": find_field(product_data, "Release Date"),
        "processor": value_or_none(processor_info.get("CPU")),
        "gpu": value_or_none(processor_info.get("GPU")),
        "ram": value_or_none(ram_info.get("Capacity")),
        "storage": value_or_none(storage_info.get("Capacity")),
        "display_type": value_or_none(display_info.get("Type")),
        "display_size": value_or_none(display_info.get("Diagonal")),
        "display_resolution": value_or_none(
            display_info.get("Resolution (H x W)")
        ),
        "refresh_rate": value_or_none(
            display_info.get("Refresh Rate")
        ),
        "battery_capacity": value_or_none(
            battery_info.get("Capacity")
        ),
        "charging_power": value_or_none(
            battery_info.get("Charging Power")
        ),
        # Keep MSRP as returned; it may contain multiple prices.
        "msrp": find_field(product_data, "MSRP", "Launch Price"),
        "source": "TechSpecs",
    }

    structured = {
        key: value
        for key, value in structured.items()
        if value is not None and not is_missing(value)
    }
    structured.update(build_product_metadata(structured))

    # Use only actual, available values in the embedding text.
    searchable_fields = [
        ("Brand", structured.get("brand")),
        ("Model", structured.get("model")),
        ("Version", structured.get("version")),
        ("Category", structured.get("category")),
        ("Manufacturer", structured.get("manufacturer")),
        ("Release date", structured.get("release_date")),
        ("Processor", structured.get("processor")),
        ("GPU", structured.get("gpu")),
        ("RAM", structured.get("ram")),
        ("Storage", structured.get("storage")),
        ("Display type", structured.get("display_type")),
        ("Display size", structured.get("display_size")),
        ("Display resolution", structured.get("display_resolution")),
        ("Refresh rate", structured.get("refresh_rate")),
        ("Battery capacity", structured.get("battery_capacity")),
        ("Charging power", structured.get("charging_power")),
        ("MSRP", structured.get("msrp")),
    ]

    text = "\n".join(
        f"{label}: {value}"
        for label, value in searchable_fields
        if value is not None and not is_missing(value)
    )

    # Preserve the original API data for debugging and future fields.
    return {
        "structured": structured,
        "text": text,
        "raw": product_data,
    }