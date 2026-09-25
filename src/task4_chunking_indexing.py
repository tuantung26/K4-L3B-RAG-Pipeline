"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

# Cache model để tránh load lại nhiều lần
_embedding_model = None


def _get_embedding_model():
    """Lazy-load embedding model theo EMBEDDING_PROVIDER."""
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model

    if EMBEDDING_PROVIDER == "sentence_transformers":
        # pyrefly: ignore [missing-import]
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    elif EMBEDDING_PROVIDER == "openai":
        # pyrefly: ignore [missing-import]
        import openai
        _embedding_model = openai.OpenAI()
    elif EMBEDDING_PROVIDER == "gemini":
        # pyrefly: ignore [missing-import]
        import google.genai as genai
        _embedding_model = genai.Client()
    else:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")

    return _embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed danh sách văn bản, dispatch theo EMBEDDING_PROVIDER trong .env."""
    model = _get_embedding_model()

    if EMBEDDING_PROVIDER == "sentence_transformers":
        return model.encode(texts, batch_size=32, show_progress_bar=False).tolist()

    elif EMBEDDING_PROVIDER == "openai":
        response = model.embeddings.create(
            model=EMBEDDING_MODEL or "text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]

    elif EMBEDDING_PROVIDER == "gemini":
        embeddings = []
        for text in texts:
            result = model.models.embed_content(
                model=EMBEDDING_MODEL or "models/text-embedding-004",
                contents=text,
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings

    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    # pyrefly: ignore [missing-import]
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    for path in STANDARDIZED_DIR.rglob("*.md"):
        doc_type = "legal" if "legal" in path.parts else "news"
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": path.read_text(encoding="utf-8"),
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    # pyrefly: ignore [missing-import]
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        for index, text in enumerate(splitter.split_text(document["content"])):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
