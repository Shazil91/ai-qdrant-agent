import os
import logging
import asyncio
import httpx
from dotenv import load_dotenv
from app.tools.base import BaseTool

load_dotenv()

logger = logging.getLogger(__name__)

API_ID = os.getenv("TEXTSPECS_API_ID")
API_KEY = os.getenv("TEXTSPECS_API_KEY")


class TechSpecsTool(BaseTool):

    BASE_URL = "https://api.techspecs.io/v5/products/search"

    SEARCHES = [
        ("display", None),
        ("laptops", "Laptops"),
        ("tablets", "Tablets"),
        ("smartphones", "Smartphones"),
        ("smartwatches", "Smartwatches"),
        ("GPUs", None),
    ]

    async def run(self):
        if not API_ID or not API_KEY:
            return {
                "tool": "techspecs",
                "success": False,
                "error": "TechSpecs API credentials are missing.",
                "data": [],
            }

        headers = {
            "x-api-id": API_ID,
            "x-api-key": API_KEY,
        }

        results = []
        errors = []

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            for query, category in self.SEARCHES:
                params = {
                    "query": query,
                    "page": 0,
                    "size": 10,
                }

                if category:
                    params["category"] = category

                try:
                    response = await client.get(
                        self.BASE_URL,
                        params=params,
                        headers=headers,
                    )

                    response.raise_for_status()
                    data = response.json()

                    results.append({
                        "query": query,
                        "category": category,
                        "response": data,
                    })

                except (
                    httpx.HTTPError,
                    ValueError,
                ) as exc:
                    logger.warning(
                        "TechSpecs search failed for %s: %s",
                        query,
                        exc,
                    )
                    errors.append({
                        "query": query,
                        "error": str(exc),
                    })

        return {
            "tool": "techspecs",
            "success": len(results) > 0,
            "data": results,
            "errors": errors,
        }