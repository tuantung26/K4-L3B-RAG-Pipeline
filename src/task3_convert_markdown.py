"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.
"""

from pathlib import Path
import json

from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOCX từ landing/legal sang standardized/legal."""

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"

    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()

    for path in legal_dir.iterdir():
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:

            output_file = output_dir / f"{path.stem}.md"

            # Không tạo lại nếu file đã tồn tại
            if output_file.exists():
                print(f"Skipped: {output_file}")
                continue

            result = converter.convert(str(path))

            if not result.text_content.strip():
                print(f"Skipped empty file: {path}")
                continue

            output_file.write_text(
                result.text_content,
                encoding="utf-8"
            )

            print(f"Converted: {path.name} -> {output_file.name}")


def convert_news_articles() -> None:
    """Convert JSON từ landing/news sang standardized/news."""

    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"

    output_dir.mkdir(parents=True, exist_ok=True)

    for path in news_dir.glob("*.json"):

        output_file = output_dir / f"{path.stem}.md"

        # Không tạo lại nếu file đã tồn tại
        if output_file.exists():
            print(f"Skipped: {output_file}")
            continue

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n"
            "---\n\n"
        )

        content = data.get("content_markdown", "").strip()

        if not content:
            print(f"Skipped empty file: {path}")
            continue

        output_file.write_text(
            header + content,
            encoding="utf-8"
        )

        print(f"Converted: {path.name} -> {output_file.name}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    convert_legal_docs()
    convert_news_articles()

    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()