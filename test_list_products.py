
import asyncio
from app.rag.qdrantdb import QdrantDB


async def main():
    qdrant = QdrantDB()

    try:
        await qdrant.ensure_collection()

        result = await qdrant.client.scroll(
            collection_name=qdrant.COLLECTION_NAME,
            scroll_filter={
                "must": [
                    {
                        "key": "record_type",
                        "match": {"value": "product"},
                    }
                ]
            },
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

        points, _ = result

        print(f"\nProducts found: {len(points)}")

        for point in points:
            payload = point.payload or {}

            print("\n----------------------------")
            print("Point ID:", point.id)
            print("Product ID:", payload.get("product_id"))
            print("Brand:", payload.get("brand"))
            print("Model:", payload.get("model"))
            print("Processor:", payload.get("processor"))
            print("RAM:", payload.get("ram"))
            print("Storage:", payload.get("storage"))
            print("Release date:", payload.get("release_date"))

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
