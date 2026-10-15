import asyncio
from app.tools.document_search import DocumentSearchTool


async def main():
    tool = DocumentSearchTool()

    try:
        query =  "Which routers support Wi-Fi 6E, 5400 Mbps, and 2.5GbE?"

        result = await tool.run(query)

        print("\nSuccess:", result.get("success"))
        print("Query:", result.get("query"))
        print("Results found:", result.get("count", 0))

        if not result.get("success"):
            print("Error:", result.get("error"))
            return

        for index, document in enumerate(result.get("data", []), start=1):
            print(f"\n--- Result {index} ---")
            print("Filename:", document.get("filename"))
            print("Source:", document.get("source"))
            print("Page:", document.get("page_number"))
            print("CSV row:", document.get("row_number"))
            print("Score:", document.get("score"))
            print("Text:", (document.get("text") or "")[:700])

    finally:
        await tool.close()


if __name__ == "__main__":
    asyncio.run(main())
