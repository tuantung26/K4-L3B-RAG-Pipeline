"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# File cache mapping source path -> pageindex document ID
_CACHE_FILE = Path(__file__).parent.parent / "chroma_db" / "pageindex_cache.json"


def _load_cache() -> dict[str, str]:
    """Đọc cache document IDs từ disk."""
    if _CACHE_FILE.exists():
        return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    """Lưu cache document IDs xuống disk."""
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY chưa được cấu hình trong .env")

    import pageindex

    client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
    cache = _load_cache()
    updated = False

    for path in STANDARDIZED_DIR.rglob("*.md"):
        key = path.relative_to(STANDARDIZED_DIR).as_posix()
        if key in cache:
            continue  # đã upload, bỏ qua

        content = path.read_text(encoding="utf-8")
        response = client.documents.create(
            title=path.stem,
            content=content,
            content_type="text/markdown",
        )
        cache[key] = response.id
        updated = True
        print(f"Uploaded: {key} -> {response.id}")

    if updated:
        _save_cache(cache)
    else:
        print("Tất cả tài liệu đã được upload trước đó.")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY chưa được cấu hình trong .env")

    import pageindex

    cache = _load_cache()
    if not cache:
        raise RuntimeError("Chưa upload tài liệu. Hãy chạy upload_documents() trước.")

    client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
    document_ids = list(cache.values())

    response = client.search(
        query=query,
        document_ids=document_ids,
        top_k=top_k,
    )

    results = []
    for rank, node in enumerate(response.results[:top_k], 1):
        # Nếu API không trả score, gán score giảm dần theo rank
        score = getattr(node, "score", None)
        if score is None:
            score = 1.0 / rank

        # Tìm lại source key từ cache để điền metadata
        source_key = next(
            (k for k, v in cache.items() if v == getattr(node, "document_id", "")),
            "unknown",
        )

        results.append({
            "id": f"pageindex::{getattr(node, 'id', rank)}",
            "content": getattr(node, "text", getattr(node, "content", "")),
            "score": float(score),
            "metadata": {
                "source": Path(source_key).name if source_key != "unknown" else "unknown",
                "title": Path(source_key).stem if source_key != "unknown" else "unknown",
                "doc_type": "legal" if "legal" in source_key else "news",
                "url": None,
                "chunk_index": rank - 1,
            },
            "retrieval_method": "pageindex",
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


if __name__ == "__main__":
    upload_documents()
