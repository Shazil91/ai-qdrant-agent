
import asyncio

from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


TEST_QUERIES = [
    "Samsung Galaxy S22",
    "Samsung phone with 8 GB RAM",
    "Phone with Qualcomm Snapdragon S2 processor",
    "Samsung phone with 128 GB storage",
    "Samsung smartphone released in 2012",
]


async def main():
    embedding = LocalEmbedding()
    qdrant = QdrantDB()

    try:
        for query in TEST_QUERIES:
            print("\n" + "=" * 70)
            print(f"QUERY: {query}")
            print("=" * 70)

            # Convert the query into a 768-dimensional vector.
            vector = embedding.create_embedding(query)

            # Search only product records, not PDF/CSV document chunks.
            results = await qdrant.search(
                vector=vector,
                limit=5,
                record_type="product",
            )

            if not results:
                print("No products found.")
                continue

            for rank, point in enumerate(results, start=1):
                payload = point.payload or {}

                print(f"\nRank: {rank}")
                print(f"Score: {point.score:.4f}")
                print(f"Model: {payload.get('model')}")
                print(f"Brand: {payload.get('brand')}")
                print(f"Processor: {payload.get('processor')}")
                print(f"RAM: {payload.get('ram')}")
                print(f"Storage: {payload.get('storage')}")
                print(f"Release date: {payload.get('release_date')}")

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
