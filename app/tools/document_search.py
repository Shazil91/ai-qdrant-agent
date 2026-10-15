from app.tools.base import BaseTool
from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


class DocumentSearchTool(BaseTool):
    def __init__(self):
        self.embedding = LocalEmbedding()
        self.qdrant = QdrantDB()

    async def run(self, query: str = "") -> dict:
        if not isinstance(query, str) or not query.strip():
            return {
                "tool": "document_search",
                "success": False,
                "error": "Please provide a document search query.",
                "data": [],
            }

        try:
            query = query.strip()
            vector = self.embedding.create_embedding(query)

            results = await self.qdrant.search(
                vector=vector,
                limit=5,
                record_type="document",
            )

            documents = []

            for point in results:
                payload = point.payload or {}

                documents.append({
                    "text": payload.get("text", ""),
                    "source": payload.get("source"),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "row_number": payload.get("row_number"),
                    "chunk_index": payload.get("chunk_index"),
                    "score": point.score,
                })

            return {
                "tool": "document_search",
                "success": True,
                "query": query,
                "count": len(documents),
                "data": documents,
            }

        except Exception as exc:
            return {
                "tool": "document_search",
                "success": False,
                "error": str(exc),
                "data": [],
            }

    async def close(self) -> None:
        await self.qdrant.close()
