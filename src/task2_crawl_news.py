"""
Task 2 — Crawl bài viết/thông báo.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://baochinhphu.vn/phat-dong-cuoc-thi-tim-hieu-phap-luat-ve-trat-tu-an-toan-giao-thong-duong-bo-nam-2026-10226092316262017.htm",
    "https://cms.baochinhphu.vn/sua-doi-bo-sung-mot-so-quy-dinh-ve-trat-tu-an-toan-giao-thong-duong-bo-102260629181414298.htm",
    "https://baochinhphu.vn/nhung-luu-y-khi-trang-bi-ghe-an-toan-cho-tre-em-102260615165901115.htm",
    "https://baochinhphu.vn/quy-dinh-ve-thiet-bi-giam-sat-tren-phuong-tien-giao-thong-duong-bo-102260818170314883.htm",
    "https://baochinhphu.vn/bao-dam-trat-tu-an-toan-giao-thong-dip-nghi-le-02-9-va-thang-cao-diem-hoc-sinh-den-truong-102260819095527811.htm",
]


async def crawl_article(url: str) -> dict:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

        return {
            "url": url,
            "title": result.metadata.get("title", "Unknown"),
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": result.markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)

            output = DATA_DIR / f"article_{index:02d}.json"

            output.write_text(
                json.dumps(
                    article,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8",
            )

            print(f"Saved: {output}")

        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())