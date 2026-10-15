import asyncio
import json

from app.rag.product_ingestion import ProductIngestion


async def main():
    ingestion = ProductIngestion()

    try:
        result = await ingestion.ingest_batch(
            query="Samsung Galaxy",
            category="Smartphones",
            limit=10,
        )

        print("\n--- BATCH INGESTION SUMMARY ---")
        print(json.dumps(result, indent=2))

    finally:
        await ingestion.close()


if __name__ == "__main__":
    asyncio.run(main())
