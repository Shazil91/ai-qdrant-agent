
from app.tools.base import BaseTool
from app.rag.embedding import LocalEmbedding
from app.rag.product_query_parser import parse_product_query
from app.rag.qdrantdb import QdrantDB


class ProductSearchTool(BaseTool):
    def __init__(self):
        self.embedding = LocalEmbedding()
        self.qdrant = QdrantDB()

    async def run(self, query: str = "") -> dict:
        if not isinstance(query, str) or not query.strip():
            return {
                "tool": "product_search",
                "success": False,
                "error": "Please provide a product search query.",
                "data": [],
            }

        try:
            filters = parse_product_query(query)
            vector = self.embedding.create_embedding(query)

            results = await self.qdrant.search(
                vector=vector,
                limit=10,
                record_type="product",
                **filters,
            )

            products = []

            for point in results:
                payload = point.payload or {}

                products.append({
                    "model": payload.get("model"),
                    "brand": payload.get("brand"),
                    "processor": payload.get("processor"),
                    "ram": payload.get("ram"),
                    "ram_mb": payload.get("ram_mb"),
                    "storage": payload.get("storage"),
                    "storage_gb": payload.get("storage_gb"),
                    "release_date": payload.get("release_date"),
                    "release_year": payload.get("release_year"),
                    "score": point.score,
                })

            return {
                "tool": "product_search",
                "success": True,
                "query": query,
                "filters": filters,
                "count": len(products),
                "data": products,
            }

        except Exception as exc:
            return {
                "tool": "product_search",
                "success": False,
                "error": str(exc),
                "data": [],
            }

    async def close(self) -> None:
        await self.qdrant.close()
