import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    The model must already exist in the local Hugging Face cache.
    """

    logger.info(
        "Loading local embedding model: %s",
        MODEL_NAME,
    )

    try:
        model = SentenceTransformer(
            MODEL_NAME,
            local_files_only=True,
        )

    except Exception as exc:
        raise RuntimeError(
            f"Unable to load local embedding model "
            f"'{MODEL_NAME}'. "
            f"Make sure the model has been downloaded "
            f"into the Hugging Face cache before running "
            f"the application."
        ) from exc

    if model.get_sentence_embedding_dimension() != EMBEDDING_DIMENSION:
        raise RuntimeError(
            "Unexpected embedding dimension. "
            f"Expected {EMBEDDING_DIMENSION}, "
            f"got {model.get_sentence_embedding_dimension()}."
        )

    logger.info(
        "Embedding model loaded successfully. "
        "Dimension=%d",
        EMBEDDING_DIMENSION,
    )

    return model


class LocalEmbedding:
    """
    Local sentence-transformer embedding service.
    """

    def create_embedding(
        self,
        text: str,
    ) -> list[float]:

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot create an embedding from empty text."
            )

        model = get_embedding_model()

        vector = model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return vector.tolist()

    @property
    def dimension(self) -> int:
        return EMBEDDING_DIMENSION