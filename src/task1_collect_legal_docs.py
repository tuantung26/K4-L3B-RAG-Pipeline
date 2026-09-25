"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    import requests

    sources = {
        "55-vbhn-vpqh.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/3/55-vbhn-vpqh.pdf",
        "49-vbhn-vpqh.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/3/49-vbhn-vpqh.pdf",
        "65-vbhn-bxd.signed.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/8/65-vbhn-bxd.signed.pdf",
    }

    for filename, url in sources.items():
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        file_path = DATA_DIR / filename
        file_path.write_bytes(response.content)

        print(f"Downloaded: {filename}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
