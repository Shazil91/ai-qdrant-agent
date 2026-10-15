
import asyncio

from app.rag.qdrantdb import QdrantDB
from app.rag.product_metadata import build_product_metadata
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)


async def main():
    qdrant = QdrantDB()

    try:
        await qdrant.ensure_collection()

        result = await qdrant.client.scroll(
            collection_name=qdrant.COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="record_type",
                        match=MatchValue(value="product"),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

        points, _ = result
        updated = 0

        for point in points:
            payload = point.payload or {}
            metadata = build_product_metadata(payload)

            if not metadata:
                print(
                    f"Skipped {payload.get('model', point.id)}: "
                    "no metadata could be extracted."
                )
                continue

            await qdrant.client.set_payload(
                collection_name=qdrant.COLLECTION_NAME,
                payload=metadata,
                points=[point.id],
                wait=True,
            )

            updated += 1

            print(
                f"Updated: {payload.get('model', 'Unknown')} | "
                f"RAM MB: {metadata.get('ram_mb')} | "
                f"Storage GB: {metadata.get('storage_gb')} | "
                f"Year: {metadata.get('release_year')}"
            )

        print(f"\nMigration complete. Updated {updated} products.")

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
