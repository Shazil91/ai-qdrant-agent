
import json
import os
import uuid
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from qdrant_client.models import PointStruct

from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB
from app.tools.product_normailzer import normalize_product


load_dotenv()

SEARCH_URL = "https://api.techspecs.io/v5/products/search"
DETAILS_URL = "https://api.techspecs.io/v5/products"


class ProductIngestion:
    """Ingest individual or multiple TechSpecs products into Qdrant."""

    def __init__(self):
        self.embedding = LocalEmbedding()
        self.qdrant = QdrantDB()

        api_id = os.getenv("API_ID") or os.getenv("TEXTSPECS_API_ID")
        api_key = os.getenv("TEXTSPECS_API_KEY")

        if not api_id or not api_key:
            raise ValueError(
                "Set API_ID (or TEXTSPECS_API_ID) and "
                "TEXTSPECS_API_KEY in your .env file."
            )

        self.headers = {
            "x-api-id": api_id,
            "x-api-key": api_key,
        }

    @staticmethod
    def make_point_id(product_id: str) -> str:
        """Create a stable UUID so reruns update the same product."""
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"techspecs:{product_id}",
            )
        )

    async def ingest_json(
        self,
        json_path: str | Path,
    ) -> dict[str, Any]:
        """Ingest one product from a saved JSON file."""
        path = Path(json_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Product JSON file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            api_response = json.load(file)

        normalized = normalize_product(api_response)
        structured = normalized["structured"]
        searchable_text = normalized["text"]
        product_id = structured.get("product_id")

        if not product_id:
            raise ValueError("The product has no product_id.")

        if not searchable_text.strip():
            raise ValueError("The product has no searchable text.")

        vector = self.embedding.create_embedding(searchable_text)

        payload = {
            **structured,
            "text": searchable_text,
            "source": "TechSpecs",
            "record_type": "product",
        }

        await self.qdrant.save(
            record_id=self.make_point_id(str(product_id)),
            vector=vector,
            payload=payload,
        )

        return {
            "success": True,
            "product_id": product_id,
            "model": structured.get("model"),
            "vector_dimension": len(vector),
        }

    async def ingest_batch(
        self,
        query: str = "Samsung Galaxy",
        category: str = "Smartphones",
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search TechSpecs, fetch product details, and save products."""
        if not 1 <= limit <= 10:
            raise ValueError("limit must be between 1 and 10.")

        response = requests.get(
            SEARCH_URL,
            params={
                "query": query,
                "category": category,
                "page": 0,
                "size": 10,
            },
            headers=self.headers,
            timeout=30,
        )
        if response.status_code != 200:
           print("HTTP Status:", response.status_code)
           print("API Error:", response.text)
           response.raise_for_status()
        search_data = response.json()

        if search_data.get("status") != "success":
            raise RuntimeError(
                f"TechSpecs search failed: {search_data}"
            )

        products = search_data.get("data", [])
        if not isinstance(products, list):
            raise ValueError(
                "Unexpected TechSpecs search response: "
                "'data' is not a list."
            )

        points: list[PointStruct] = []
        failures: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for item in products:
            product_info = item.get("Product", {})
            product_id = (
                product_info.get("id")
                or item.get("_id")
                or item.get("id")
            )

            if not product_id:
                failures.append({
                    "product": str(
                        product_info.get("Model", "Unknown")
                    ),
                    "error": "No product ID in search result.",
                })
                continue

            product_id = str(product_id)

            if product_id in seen_ids:
                continue
            seen_ids.add(product_id)

            if len(points) + len(failures) >= limit:
                break

            try:
                detail_response = requests.get(
                    f"{DETAILS_URL}/{product_id}",
                    headers=self.headers,
                    timeout=30,
                )
                detail_response.raise_for_status()

                detail_data = detail_response.json()

                if detail_data.get("status") != "success":
                    raise ValueError(
                        "TechSpecs did not return success status."
                    )

                normalized = normalize_product(detail_data)
                structured = normalized["structured"]
                searchable_text = normalized["text"]

                if not searchable_text.strip():
                    raise ValueError("Product has no searchable text.")

                vector = self.embedding.create_embedding(
                    searchable_text
                )

                payload = {
                    **structured,
                    "text": searchable_text,
                    "source": "TechSpecs",
                    "record_type": "product",
                }

                points.append(
                    PointStruct(
                        id=self.make_point_id(product_id),
                        vector=vector,
                        payload=payload,
                    )
                )

                print(
                    f"Prepared {len(points)}: "
                    f"{structured.get('model', product_id)}"
                )

            except Exception as exc:
                failures.append({
                    "product_id": product_id,
                    "error": str(exc),
                })
                print(f"Failed {product_id}: {exc}")

        # Save all successfully prepared products in one Qdrant upsert.
        if points:
            await self.qdrant.save_many(points)

        return {
            "success": len(points) > 0,
            "query": query,
            "category": category,
            "requested": limit,
            "ingested": len(points),
            "failed": len(failures),
            "products": [
                {
                    "product_id": str(
                        point.payload.get("product_id", "")
                    ),
                    "model": point.payload.get("model"),
                    "brand": point.payload.get("brand"),
                }
                for point in points
            ],
            "failures": failures,
        }

    async def close(self) -> None:
        await self.qdrant.close()
