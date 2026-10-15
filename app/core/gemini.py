import asyncio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
load_dotenv()

GEMINI_MODEL = "gemini-3.8-flash"

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add GEMINI_API_KEY to your .env file."
    )

client = genai.Client(api_key=API_KEY)

MAX_TOOL_ROUNDS = 5


PRODUCT_SEARCH_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_products",
            description=(
                "Search the structured product database for matching "
                "products. Use this for product names, brands, RAM, "
                "storage, release years, and product specifications. "
                "Preserve the user's product requirements in the query."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": (
                            "Product search query including relevant "
                            "brand, RAM, storage, and release-year requirements."
                        ),
                    }
                },
                "required": ["query"],
            },
        )
    ]
)


DOCUMENT_SEARCH_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_documents",
            description=(
                "Search PDF and CSV document chunks stored in Qdrant. "
                "Use this for information from the electronics catalog "
                "and inventory documents, including prices, stock status, "
                "stock quantities, and supporting document details. "
                "Use the user's specific requirements in the query."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": (
                            "A focused natural-language query for relevant "
                            "information in PDF and CSV documents."
                        ),
                    }
                },
                "required": ["query"],
            },
        )
    ]
)


TOOL_CONFIG = types.GenerateContentConfig(
    tools=[
        PRODUCT_SEARCH_TOOL,
        DOCUMENT_SEARCH_TOOL,
    ],
    system_instruction=(
        "You are a product research assistant. "
        "Use search_products for structured product database searches. "
        "Use search_documents for PDF and CSV catalog or inventory data. "
        "If a question requires both product specifications and inventory "
        "information, use both tools when needed. "
        "Use the returned tool results as evidence. "
        "Do not repeat an identical search query when its results are "
        "already available. Once you have enough information, answer "
        "the user directly instead of calling more tools. "
        "If information is missing, clearly state that it could not "
        "be verified from the available results."
    ),
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    ),
)


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return its text response."""
    if not prompt or not prompt.strip():
        raise ValueError("Gemini prompt cannot be empty.")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


async def ask_gemini_with_tools(
    question: str,
    product_tool,
    document_tool,
) -> dict:
    """
    Let Gemini choose between product search and document search.

    Returns the final answer and separate results for each tool.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=question.strip())],
        )
    ]

    product_search_results = []
    document_search_results = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=contents,
            config=TOOL_CONFIG,
        )

        if not response.candidates:
            raise RuntimeError("Gemini returned no response candidates.")

        model_content = response.candidates[0].content
        function_calls = response.function_calls or []

        # Gemini has finished and produced its final answer.
        if not function_calls:
            if not response.text:
                raise RuntimeError("Gemini returned an empty answer.")

            return {
                "answer": response.text,
                "tool_calls": product_search_results,
                "document_tool_calls": document_search_results,
            }

        # Preserve Gemini's function-call message.
        contents.append(model_content)

        function_response_parts = []

        for function_call in function_calls:
            arguments = function_call.args or {}
            query = arguments.get("query", "")

            if function_call.name == "search_products":
                result = await product_tool.run(query)
                product_search_results.append(result)

            elif function_call.name == "search_documents":
                result = await document_tool.run(query)
                document_search_results.append(result)

            else:
                result = {
                    "tool": function_call.name,
                    "success": False,
                    "error": "Unknown tool requested by Gemini.",
                    "data": [],
                }

            function_response_parts.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": result},
                )
            )

                # Build a standalone prompt from the collected tool results.
        # This avoids sending the potentially invalid tool-call history
        # back to Gemini.
        final_prompt = (
            "You are a product research assistant.\n\n"
            f"Original question:\n{question}\n\n"
            "Product search results:\n"
            f"{json.dumps(product_search_results, ensure_ascii=False, default=str)}\n\n"
            "Document search results:\n"
            f"{json.dumps(document_search_results, ensure_ascii=False, default=str)}\n\n"
            "Answer the original question using these results as evidence. "
            "Do not call tools. Do not invent product specifications, "
            "prices, or stock availability. Clearly state when information "
            "is missing or cannot be verified."
        )

        final_response = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            ),
        )

        if not final_response.text:
            raise RuntimeError(
                "Gemini returned an empty final answer."
            )

        return {
            "answer": final_response.text,
            "tool_calls": product_search_results,
            "document_tool_calls": document_search_results,
        }