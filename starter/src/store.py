"""Persistent Chroma vector store with cosine search and metadata filters."""
import re
from pathlib import Path
from typing import Any

import chromadb

from .models import Chunk


class ChromaStore:
    def __init__(self, path: Path | str, dimensions: int) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions
        self.client = chromadb.PersistentClient(path=str(path))
        self._collections: dict[str, Any] = {}

    def _collection(self, strategy: str) -> Any:
        if strategy not in self._collections:
            name = re.sub(r"[^a-zA-Z0-9_-]", "_", strategy.lower())[:60]
            if len(name) < 3:
                name = f"day6_{name}"
            self._collections[strategy] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine", "strategy": strategy},
                embedding_function=None,
            )
        return self._collections[strategy]

    def upsert(self, strategy: str, chunks: list[Chunk],
               vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("each chunk must have exactly one embedding")
        if any(len(vector) != self.dimensions for vector in vectors):
            raise ValueError(f"all vectors must have {self.dimensions} dimensions")
        if not chunks:
            return

        collection = self._collection(strategy)
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = []
        for chunk in chunks:
            metadata = dict(chunk.metadata)
            metadata.update({
                "document_id": chunk.document_id,
                "source": chunk.source,
                "page": chunk.page,
            })
            # Chroma metadata accepts scalar values; reject nested objects early.
            if any(not isinstance(v, (str, int, float, bool)) for v in metadata.values()):
                raise TypeError("Chroma metadata values must be strings, numbers, or booleans")
            metadatas.append(metadata)

        collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=metadatas,
        )

        # Remove old chunks for these source documents after a changed re-ingest.
        current_by_document: dict[str, set[str]] = {}
        for chunk in chunks:
            current_by_document.setdefault(chunk.document_id, set()).add(chunk.chunk_id)
        for document_id, current_ids in current_by_document.items():
            previous = collection.get(where={"document_id": document_id}, include=[])
            obsolete = set(previous["ids"]) - current_ids
            if obsolete:
                collection.delete(ids=sorted(obsolete))

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if len(query_vector) != self.dimensions:
            raise ValueError(f"query vector must have {self.dimensions} dimensions")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        collection = self._collection(strategy)
        if collection.count() == 0:
            return []

        result = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count()),
            where=filters or None,
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        for chunk_id, document, metadata, distance in zip(
            result["ids"][0], result["documents"][0],
            result["metadatas"][0], result["distances"][0],
        ):
            hits.append({
                "chunk_id": chunk_id,
                "text": document,
                "score": 1.0 - float(distance),
                "metadata": metadata,
            })
        return hits
