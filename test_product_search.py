import asyncio
from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


async def main():
    embedding = LocalEmbedding()
    qdrant = QdrantDB()

    try:
        query = "Samsung phone with a powerful processor and 8 GB RAM"

        query_vector = embedding.create_embedding(query)

        results = await qdrant.search(
            vector=query_vector,
            limit=5,
            record_type="product",
        )

        print("\n--- SEARCH RESULTS ---")

        if not results:
            print("No matching products or documents found.")
            return

        for result in results:
            payload = result.payload or {}

            print(f"\nScore: {result.score:.4f}")
            print(f"Type: {payload.get('record_type', 'document')}")
            print(f"Brand: {payload.get('brand', 'N/A')}")
            print(f"Model: {payload.get('model', 'N/A')}")
            print(f"Processor: {payload.get('processor', 'N/A')}")
            print(f"RAM: {payload.get('ram', 'N/A')}")
            print(f"Text: {payload.get('text', '')[:300]}")

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())