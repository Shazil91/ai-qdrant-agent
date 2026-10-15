
import asyncio

from app.rag.embedding import LocalEmbedding
from app.rag.product_query_parser import parse_product_query
from app.rag.qdrantdb import QdrantDB


TEST_QUERIES = [
    {
        "query": "Samsung phone with 8 GB RAM",
        "expected_count": 1,
    },
    {
        "query": "Samsung phone with 128 GB storage",
        "expected_count": 1,
    },
    {
        "query": "Samsung smartphone released in 2012",
        "expected_count": 2,
    },
    {
        "query": "Samsung phone with 8 GB RAM and 128 GB storage",
        "expected_count": 1,
    },
]


async def main():
    embedding = LocalEmbedding()
    qdrant = QdrantDB()

    try:
        for test in TEST_QUERIES:
            query = test["query"]
            print("\n" + "=" * 65)
            print(f"QUERY: {query}")
            print("=" * 65)

            # 1. Extract structured filters from the user's query.
            filters = parse_product_query(query)
            print(f"Extracted filters: {filters}")

            # 2. Convert the query into an embedding.
            vector = embedding.create_embedding(query)

            # 3. Search Qdrant using both semantic search and filters.
            results = await qdrant.search(
                vector=vector,
                limit=10,
                record_type="product",
                **filters,
            )

            print(f"Products returned: {len(results)}")

            # 4. Display results and verify every metadata constraint.
            for point in results:
                payload = point.payload or {}

                print(
                    f"Model: {payload.get('model')} | "
                    f"RAM: {payload.get('ram_mb')} MB | "
                    f"Storage: {payload.get('storage_gb')} GB | "
                    f"Year: {payload.get('release_year')} | "
                    f"Score: {point.score:.4f}"
                )

                if "brand" in filters:
                    assert payload.get("brand") == filters["brand"]

                if "ram_mb" in filters:
                    assert payload.get("ram_mb") == filters["ram_mb"]

                if "storage_gb" in filters:
                    assert filters["storage_gb"] in (
                        payload.get("storage_gb") or []
                    )

                if "release_year" in filters:
                    assert (
                        payload.get("release_year")
                        == filters["release_year"]
                    )

            assert len(results) == test["expected_count"], (
                f"Expected {test['expected_count']} products, "
                f"but got {len(results)} for query: {query}"
            )

            print("PASS: Query parsing and filtered retrieval succeeded.")

        print("\nAll product search integration tests passed!")

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
