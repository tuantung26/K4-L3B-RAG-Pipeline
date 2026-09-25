"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []

# Cache index để không build lại mỗi lần gọi
_bm25_index: BM25Okapi | None = None
_bm25_corpus: list[dict] = []


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def _load_corpus_from_vectorstore() -> list[dict]:
    """Lấy toàn bộ chunks từ ChromaDB để build BM25 corpus."""
    from .task4_chunking_indexing import get_collection

    collection = get_collection()
    total = collection.count()
    if total == 0:
        return []
    response = collection.get(
        limit=total,
        include=["documents", "metadatas"],
    )
    corpus = []
    for item_id, content, metadata in zip(
        response["ids"],
        response["documents"],
        response["metadatas"],
    ):
        corpus.append({
            "id": item_id,
            "content": content,
            "metadata": metadata,
        })
    return corpus


def _get_bm25() -> tuple[BM25Okapi, list[dict]]:
    """Lazy-load BM25 index và corpus từ ChromaDB.

    Nếu module-level CORPUS được set (e.g. qua monkeypatch trong test),
    luôn build lại index từ CORPUS đó để tránh dùng cache stale.
    """
    global _bm25_index, _bm25_corpus

    # Nếu CORPUS được inject từ ngoài (test hoặc caller), ưu tiên dùng nó
    if CORPUS:
        if CORPUS is not _bm25_corpus:
            # CORPUS thay đổi → build lại index
            _bm25_corpus = CORPUS
            _bm25_index = build_bm25_index(_bm25_corpus)
        return _bm25_index, _bm25_corpus

    # Không có CORPUS inject → lazy-load từ ChromaDB
    if _bm25_index is None:
        _bm25_corpus = _load_corpus_from_vectorstore()
        _bm25_index = build_bm25_index(_bm25_corpus)

    return _bm25_index, _bm25_corpus


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    bm25, corpus = _get_bm25()
    if not corpus:
        return []

    scores = bm25.get_scores(query.lower().split())
    indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for index in indices:
        if scores[index] <= 0:
            continue
        item = corpus[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
