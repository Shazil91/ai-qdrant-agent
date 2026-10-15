from app.rag.product_query_parser import parse_product_query


tests = [
    (
        "Samsung phone with 8 GB RAM",
        {"brand": "Samsung", "ram_mb": 8192},
    ),
    (
        "Samsung phone with 128 GB storage",
        {"brand": "Samsung", "storage_gb": 128},
    ),
    (
        "Samsung smartphone released in 2012",
        {"brand": "Samsung", "release_year": 2012},
    ),
    (
        "Phone with 512 MB RAM",
        {"ram_mb": 512},
    ),
    (
        "Samsung phone with 8 GB RAM and 128 GB storage",
        {
            "brand": "Samsung",
            "ram_mb": 8192,
            "storage_gb": 128,
        },
    ),
    (
        "Find Samsung Galaxy S22",
        {"brand": "Samsung"},
    ),
]

for query, expected in tests:
    actual = parse_product_query(query)

    print(f"\nQuery: {query}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")

    assert actual == expected, (
        f"Failed for {query!r}: expected {expected}, got {actual}"
    )

print("\nAll product query parser tests passed!")
