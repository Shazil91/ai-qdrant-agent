import asyncio
import json

from app.rag.product_ingestion import ProductIngestion


async def main():
    ingestion = ProductIngestion()

    try:
        # Ingest the saved product JSON without calling the TechSpecs API.
        result = await ingestion.ingest_json("samsung_s22.json")

        print("\n--- LOCAL PRODUCT INGESTION RESULT ---")
        print(json.dumps(result, indent=2))

    except Exception as exc:
        print(f"\nIngestion failed: {type(exc).__name__}: {exc}")
        raise

    finally:
        await ingestion.close()


if __name__ == "__main__":
    asyncio.run(main())