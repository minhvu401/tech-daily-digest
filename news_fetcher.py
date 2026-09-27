"""
news_fetcher.py – Thu thập tin tức từ RSS feeds
Lọc bài trong vòng FETCH_HOURS_BACK giờ gần nhất.
"""
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import TypedDict

import feedparser
import requests

import config

logger = logging.getLogger(__name__)


class Article(TypedDict):
    title: str
    url: str
    source: str
    published: str   # ISO string
    summary_raw: str  # Mô tả gốc từ feed (sẽ được AI tóm tắt lại)


def _parse_published(entry) -> datetime:
    """Chuyển đổi time struct từ feedparser sang datetime UTC."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    # Không có ngày → coi như bài hôm nay
    return datetime.now(timezone.utc)


def _clean_html(text: str) -> str:
    """Loại bỏ thẻ HTML và boilerplate text từ RSS feeds."""
    import re
    # Decode HTML entities
    text = text.replace("&#160;", " ").replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # Xóa thẻ HTML
    text = re.sub(r"<[^>]+>", " ", text)
    # Xóa boilerplate text phổ biến từ feed
    boilerplate = [
        r"The post .+ first appeared on .+\.",
        r"Continue reading\.?",
        r"Read more\.?",
        r"Click here to read more\.?",
        r"\[…\]", r"\[\.\.\.\]",
        r"This article first appeared on .+\.",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    # Xóa khoảng trắng thừa
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_topic(topic_key: str) -> list[Article]:
    """
    Fetch tất cả feeds của một chủ đề, trả về danh sách Article
    sắp xếp theo thời gian mới nhất, tối đa MAX_ARTICLES_PER_TOPIC bài.
    """
    topic_cfg = config.RSS_FEEDS[topic_key]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.FETCH_HOURS_BACK)
    articles: list[Article] = []

    for source_name, feed_url in topic_cfg["feeds"]:
        try:
            feed = feedparser.parse(
                feed_url,
                request_headers={"User-Agent": "TechDailyDigest/1.0"},
            )
            if feed.bozo and not feed.entries:
                logger.warning("Feed lỗi (bozo): %s", feed_url)
                continue

            for entry in feed.entries:
                pub_dt = _parse_published(entry)
                if pub_dt < cutoff:
                    continue

                title = getattr(entry, "title", "").strip()
                url   = getattr(entry, "link", "").strip()
                if not title or not url:
                    continue

                # Lấy mô tả gốc (ưu tiên summary > content)
                raw = ""
                if hasattr(entry, "summary"):
                    raw = entry.summary
                elif hasattr(entry, "content"):
                    raw = entry.content[0].get("value", "")
                raw = _clean_html(raw)[:1500]  # Tăng lên 1500 ký tự để Gemini có đủ context

                articles.append(
                    Article(
                        title=title,
                        url=url,
                        source=source_name,
                        published=pub_dt.isoformat(),
                        summary_raw=raw,
                    )
                )

        except Exception as exc:
            logger.warning("Không thể fetch %s (%s): %s", source_name, feed_url, exc)
            continue

    # Sắp xếp mới nhất trước, lấy tối đa MAX
    articles.sort(key=lambda a: a["published"], reverse=True)

    # Dedup theo URL
    seen: set[str] = set()
    unique: list[Article] = []
    for art in articles:
        if art["url"] not in seen:
            seen.add(art["url"])
            unique.append(art)

    return unique[: config.MAX_ARTICLES_PER_TOPIC]


def fetch_all_topics() -> dict[str, list[Article]]:
    """Fetch tất cả chủ đề, trả về dict topic_key → list[Article]."""
    result: dict[str, list[Article]] = {}
    for topic_key in config.RSS_FEEDS:
        logger.info("Đang fetch topic: %s", topic_key)
        result[topic_key] = fetch_topic(topic_key)
        time.sleep(0.5)  # Lịch sự với server
    return result
