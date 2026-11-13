"""Local embedding adapter using Chroma's default real embedding model."""
from typing import Protocol

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Wrap Chroma's local all-MiniLM-L6-v2 embedding function."""

    def __init__(self, model_name: str) -> None:
        if model_name not in {"all-MiniLM-L6-v2", "default"}:
            raise ValueError(
                "This adapter uses Chroma's all-MiniLM-L6-v2 model; "
                "choose model_name='all-MiniLM-L6-v2'."
            )
        self.model_name = "all-MiniLM-L6-v2 (Chroma DefaultEmbeddingFunction)"
        self._function = DefaultEmbeddingFunction()
        self.dimensions = len(self._function(["dimension check"])[0])

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._function(texts)]

    def embed_query(self, question: str) -> list[float]:
        return self._function([question])[0].tolist()
