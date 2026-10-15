
import asyncio

from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


async def main():
    embedding = LocalEmbedding()
    qdrant = QdrantDB()

    tests = [
        {
            "name": "Samsung phone with 8 GB RAM",
            "query": "Samsung phone with 8 GB RAM",
            "filters": {"brand": "Samsung", "ram_mb": 8192},
            "expected_models": {"Samsung Galaxy S22"},
        },
        {
            "name": "Samsung phone with 128 GB storage",
            "query": "Samsung phone with 128 GB storage",
            "filters": {"brand": "Samsung", "storage_gb": 128},
            "expected_models": {"Samsung Galaxy S22"},
        },
        {
            "name": "Samsung smartphone released in 2012",
            "query": "Samsung smartphone released in 2012",
            "filters": {"brand": "Samsung", "release_year": 2012},
            "expected_models": {"Samsung Galaxy"},
        },
    ]

    try:
        for test in tests:
            print("\n" + "=" * 65)
            print(f"TEST: {test['name']}")
            print("=" * 65)

            vector = embedding.create_embedding(test["query"])

            results = await qdrant.search(
                vector=vector,
                limit=10,
                record_type="product",
                **test["filters"],
            )

            print(f"Products returned: {len(results)}")

            if not results:
                print("FAIL: No matching products found.")
                continue

            for point in results:
                payload = point.payload or {}

                print(
                    f"Model: {payload.get('model')} | "
                    f"RAM: {payload.get('ram_mb')} MB | "
                    f"Storage: {payload.get('storage_gb')} GB | "
                    f"Year: {payload.get('release_year')} | "
                    f"Score: {point.score:.4f}"
                )

            # Validate the actual metadata constraints.
            passed = True

            for point in results:
                payload = point.payload or {}

                if payload.get("brand") != test["filters"]["brand"]:
                    passed = False

                if "ram_mb" in test["filters"]:
                    if payload.get("ram_mb") != test["filters"]["ram_mb"]:
                        passed = False

                if "storage_gb" in test["filters"]:
                    if test["filters"]["storage_gb"] not in (
                        payload.get("storage_gb") or []
                    ):
                        passed = False

                if "release_year" in test["filters"]:
                    if payload.get("release_year") != test["filters"]["release_year"]:
                        passed = False

            if passed:
                print("PASS: All returned products satisfy the filters.")
            else:
                print("FAIL: A returned product violates a filter.")

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
