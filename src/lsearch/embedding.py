"""Embedding model management."""

from functools import lru_cache
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """Manages local embedding models."""

    MODELS = {
        "all-MiniLM-L6-v2": {
            "name": "all-MiniLM-L6-v2",
            "dim": 384,
            "description": "Fast, good for English (70MB)",
        },
        "bge-small-zh": {
            "name": "BAAI/bge-small-zh",
            "dim": 512,
            "description": "Optimized for Chinese (300MB)",
        },
        "bge-small-en": {
            "name": "BAAI/bge-small-en",
            "dim": 384,
            "description": "Optimized for English (130MB)",
        },
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            model_key = self.model_name
            if model_key not in self.MODELS:
                raise ValueError(f"Unknown model: {model_key}")

            model_id = self.MODELS[model_key]["name"]
            self._model = SentenceTransformer(model_id)

        return self._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        return self.embed([text])[0]

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.MODELS.get(self.model_name, {}).get("dim", 384)

    @classmethod
    def list_models(cls) -> dict:
        """List available models."""
        return cls.MODELS.copy()


@lru_cache(maxsize=1)
def get_embedding_manager(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingManager:
    """Get cached embedding manager instance."""
    return EmbeddingManager(model_name)
