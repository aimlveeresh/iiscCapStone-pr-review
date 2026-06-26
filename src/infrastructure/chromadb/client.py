"""ChromaDB client: embedded (default) or HTTP (optional)."""

from __future__ import annotations

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_client = None
_collection = None


def _init_client():
    global _client, _collection
    if _client is not None:
        return

    settings = get_settings()
    chromadb = settings.chromadb
    mode = chromadb.mode.lower()

    try:
        if mode == "http":
            import chromadb

            _client = chromadb.HttpClient(
                host=chromadb.host,
                port=chromadb.port,
            )
        else:  # embedded (default)
            import chromadb

            _client = chromadb.PersistentClient(
                path=chromadb.persist_dir,
            )
        _collection = _client.get_or_create_collection(
            name=chromadb.collection,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("chromadb_initialized", mode=mode)
    except Exception as exc:
        logger.error("chromadb_init_failed", error=str(exc), mode=mode)
        _client = None
        _collection = None


def get_collection():
    """Get the ChromaDB collection (lazy init)."""
    _init_client()
    return _collection


def query_knowledge(query: str, top_k: int = 5) -> list[str]:
    """Query the knowledge base for documents matching the query."""
    collection = get_collection()
    if collection is None:
        logger.debug("chromadb_not_available")
        return []

    try:
        # embeddings will be auto-generated if embed_function is configured.
        results = collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        return docs
    except Exception as exc:
        logger.debug("chromadb_query_failed", error=str(exc))
        return []


def upsert_documents(documents: list[str], metadatas: list[dict] | None = None) -> None:
    """Upsert documents into the knowledge base."""
    collection = get_collection()
    if collection is None:
        logger.warning("chromadb_not_available_for_upsert")
        return

    try:
        ids = [str(i) for i in range(len(documents))]
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas or [{"source": "owasp"} for _ in documents],
        )
        logger.info("chromadb_upserted", count=len(documents))
    except Exception as exc:
        logger.error("chromadb_upsert_failed", error=str(exc))
