import asyncio
import json

from app.rag.qdrantdb import QdrantDB


async def main():
    db = QdrantDB()

    try:
        print("Collection:", db.COLLECTION_NAME)

        await db.ensure_collection()

        result = await db.client.scroll(
            collection_name=db.COLLECTION_NAME,
            limit=10,
            with_payload=True,
            with_vectors=False,
        )

        points, _ = result

        for point in points:
            payload = point.payload or {}

            if payload.get("product_id") == "63e96260ff7af4b68a303f3f":
                print("\n--- MATCHING PRODUCT PAYLOAD ---")
                print(json.dumps(payload, indent=2))
                print("\n--- FILTER FIELD VALUES ---")
                print("record_type:", repr(payload.get("record_type")))
                print("brand:", repr(payload.get("brand")))
                print("ram:", repr(payload.get("ram")))
                print("ram_mb:", repr(payload.get("ram_mb")))
                return

        print("Samsung Galaxy S22 was not found in the first 10 points.")
        print("The collection may contain more points, or the wrong collection may be selected.")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())