"""Read-only adapter to the RAG Lead's Week 8 baseline."""

import os
from functools import lru_cache
from typing import Any, Literal, TypedDict


class ContextResult(TypedDict):
    chunks: list[dict[str, Any]]


@lru_cache(maxsize=1)
def _get_retriever():
    # Keep model loading and Qdrant access out of server startup and other tools.
    from src.rag.baseline import BaselineRetriever, DEFAULT_DATA

    return BaselineRetriever(
        data_path=os.environ.get("RAG_DATA_PATH", DEFAULT_DATA),
        url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
    )


def retrieve_context(
    query: str, mode: Literal["folk", "rap"] | None = None, limit: int = 5,
) -> ContextResult:
    """Retrieve ranked corpus chunks with provenance and cosine scores.

    Requires an already ingested Week 8 BGE-M3 collection in Qdrant. Does not
    ingest or write data. Omit mode for unfiltered retrieval; limit is 1-20.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Provide a nonempty query.")
    if mode not in (None, "folk", "rap"):
        raise ValueError("Mode must be folk, rap or None.")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("Limit must be an integer from 1 to 20.")
    hits = _get_retriever().retrieve(query, mode=mode, limit=limit)
    return {"chunks": hits}
