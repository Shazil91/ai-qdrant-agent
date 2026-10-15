
import asyncio

from app.rag.qdrantdb import QdrantDB
from qdrant_client.models import FieldCondition, Filter, MatchValue


async def main():
    qdrant = QdrantDB()

    try:
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

        for point in points:
            payload = point.payload or {}

            print(
                f"{payload.get('model', 'Unknown')}: "
                f"RAM MB={payload.get('ram_mb')}, "
                f"Storage GB={payload.get('storage_gb')}, "
                f"Year={payload.get('release_year')}"
            )

    finally:
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(main())
