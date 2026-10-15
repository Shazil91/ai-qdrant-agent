
import asyncio
import json

from app.rag.product_ingestion import ProductIngestion


async def main():
    ingestion = ProductIngestion()

    try:
        result = await ingestion.ingest_json(
            "samsung_s22.json"
        )

        print("\n--- INGESTION RESULT ---")
        print(json.dumps(result, indent=2))

    finally:
        await ingestion.close()


if __name__ == "__main__":
    asyncio.run(main())