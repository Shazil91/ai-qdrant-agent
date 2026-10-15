import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.core.gemini import ask_gemini_with_tools
from app.tools.product_search import ProductSearchTool
from app.tools.document_search import DocumentSearchTool


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.product_tool = ProductSearchTool()
    app.state.document_tool = DocumentSearchTool()

    logger.info("Product search tool initialized.")
    logger.info("Document search tool initialized.")

    try:
        yield
    finally:
        await app.state.product_tool.close()
        await app.state.document_tool.close()

        logger.info("Product search tool closed.")
        logger.info("Document search tool closed.")


app = FastAPI(
    title="AI Qdrant Agent",
    description=(
        "Product and document search using Qdrant "
        "and Gemini function calling."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class ProductQuestion(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description=(
            "Ask a question about products, documents, "
            "or another general topic."
        ),
    )


@app.get("/")
async def root():
    return {
        "message": "AI Qdrant Agent API is running.",
    }


@app.post("/ask")
async def ask_product_question(request: ProductQuestion):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = await ask_gemini_with_tools(
            question=question,
            product_tool=app.state.product_tool,
            document_tool=app.state.document_tool,
        )
    except Exception as exc:
        logger.exception("Failed to process the question.")
        raise HTTPException(
            status_code=502,
            detail=(
                "Failed to generate an answer. "
                "Check the application logs."
            ),
        ) from exc

    # Preserve the existing product-search response.
    tool_calls = result["tool_calls"]

    products = []
    seen_products = set()

    for tool_result in tool_calls:
        if not tool_result.get("success"):
            continue

        for product in tool_result.get("data", []):
            identity = (
                product.get("brand"),
                product.get("model"),
                product.get("release_date"),
            )

            if identity not in seen_products:
                seen_products.add(identity)
                products.append(product)

    latest_successful_search = next(
        (
            item
            for item in reversed(tool_calls)
            if item.get("success")
        ),
        {},
    )

    # Collect document-search results separately.
    document_tool_calls = result["document_tool_calls"]

    documents = []
    seen_documents = set()

    for tool_result in document_tool_calls:
        if not tool_result.get("success"):
            continue

        for document in tool_result.get("data", []):
            identity = (
                document.get("filename"),
                document.get("page_number"),
                document.get("row_number"),
                document.get("chunk_index"),
                document.get("text"),
            )

            if identity not in seen_documents:
                seen_documents.add(identity)
                documents.append(document)

    return {
        "question": question,
        "tool_calls_made": len(tool_calls),
        "products_found": len(products),
        "filters": latest_successful_search.get("filters", {}),
        "products": products,
        "document_tool_calls_made": len(document_tool_calls),
        "documents_found": len(documents),
        "documents": documents,
        "answer": result["answer"],
    }