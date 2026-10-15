
import hashlib
from pathlib import Path

from qdrant_client.models import PointStruct

from app.ingestion.csv_ingestion import CSVIngestion
from app.ingestion.pdf_ingestion import PDFIngestion
from app.rag.embedding import LocalEmbedding
from app.rag.qdrantdb import QdrantDB


class RAGIngestion:
    def __init__(
        self,
        pdf_directory: str | Path = "app/data",
        csv_directory: str | Path = "app/csv",
    ):
        self.embedding = LocalEmbedding()
        self.qdrant = QdrantDB()

        self.pdf_directory = Path(pdf_directory)
        self.csv_directory = Path(csv_directory)

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[str]:
        if not text or not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be >= 0 and smaller than chunk_size."
            )

        text = text.strip()
        chunks = []
        step = chunk_size - overlap

        for start in range(0, len(text), step):
            chunk = text[start : start + chunk_size].strip()

            if chunk:
                chunks.append(chunk)

            if start + chunk_size >= len(text):
                break

        return chunks

    @staticmethod
    def make_point_id(
        document: dict,
        chunk_index: int,
    ) -> str:
        identity = "|".join(
            [
                str(document.get("source", "")),
                str(document.get("filename", "")),
                str(document.get("page_number", "")),
                str(document.get("row_number", "")),
                str(chunk_index),
            ]
        )

        return hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:32]

    async def run(self) -> dict:
        documents: list[dict] = []

        if self.pdf_directory.exists():
            documents.extend(
                PDFIngestion(self.pdf_directory).ingest_all()
            )

        if self.csv_directory.exists():
            documents.extend(
                CSVIngestion(self.csv_directory).ingest_all()
            )

        points: list[PointStruct] = []

        for document in documents:
            chunks = self.chunk_text(document.get("text", ""))

            for chunk_index, chunk in enumerate(chunks):
                vector = self.embedding.create_embedding(chunk)

                if len(vector) != self.qdrant.VECTOR_SIZE:
                    raise ValueError(
                        f"Expected {self.qdrant.VECTOR_SIZE} embedding "
                        f"dimensions, got {len(vector)}."
                    )

                point_id = self.make_point_id(
                    document,
                    chunk_index,
                )

                payload = {
                    "record_type": "document",
                    "text": chunk,
                    "source": document.get("source", "unknown"),
                    "filename": document.get("filename"),
                    "page_number": document.get("page_number"),
                    "row_number": document.get("row_number"),
                    "chunk_index": chunk_index,
                }

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                )

        await self.qdrant.save_many(points)

        return {
            "success": True,
            "documents": len(documents),
            "chunks": len(points),
        }
