
import asyncio
from app.tools.product_search import ProductSearchTool


async def main():
    tool = ProductSearchTool()

    try:
        queries = [
            "Samsung phone with 8 GB RAM",
            "Samsung phone with 128 GB storage",
            "Samsung smartphone released in 2012",
        ]

        for query in queries:
            print("\n" + "=" * 60)
            print(f"QUERY: {query}")
            print("=" * 60)

            result = await tool.run(query)

            print(f"Success: {result['success']}")
            print(f"Filters: {result.get('filters')}")
            print(f"Count: {result.get('count')}")

            if not result["success"]:
                print(f"Error: {result['error']}")
                continue

            for product in result["data"]:
                print(
                    f"{product['model']} | "
                    f"RAM: {product['ram']} | "
                    f"Storage: {product['storage']} | "
                    f"Year: {product['release_year']}"
                )

    finally:
        await tool.close()


if __name__ == "__main__":
    asyncio.run(main())
