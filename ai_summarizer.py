"""
ai_summarizer.py – Tóm tắt bài viết bằng Gemini AI
Dùng google-genai >= 2.3.0, retry với exponential backoff cho lỗi 503.
"""
import logging
import re
import time
from typing import TYPE_CHECKING

from google import genai

import config

if TYPE_CHECKING:
    from news_fetcher import Article

logger = logging.getLogger(__name__)

# Khởi tạo Gemini client một lần duy nhất
_client: genai.Client | None = None

# Fallback models
_MODEL_FALLBACKS = [
    config.GEMINI_MODEL,    # gemini-3.8-flash (primary)
    "gemini-flash-latest",  # alias ổn định
]

_SYSTEM_PROMPT = """
Ban la tro ly tom tat tin tuc cong nghe cho mot developer Viet Nam.
Nhiem vu: Tom tat bai viet ky thuat bang TIENG VIET, day du thong tin nhung gon gang.

Quy tac:
- Viet 4-6 cau, khoang 80-120 tu (du de hieu ma khong can vao doc bai goc)
- Cau 1: Neu van de / tin tuc chinh la gi
- Cau 2-4: Neu cu the cac diem noi bat, tinh nang moi, thay doi quan trong, hoac cac buoc chinh
- Cau 5-6 (neu can): Li do quan trong voi developer, hoac ket luan
- Giu nguyen ten ky thuat tieng Anh (Java, Spring Boot, LLM, RAG, AWS, Docker...)
- KHONG bat dau bang "Bai viet nay..." hay "Theo bai..."
- KHONG dung tu hoa my thua
- Tra ve DUNG so dong tom tat tuong ung voi so bai dau vao, danh so [1], [2]...
""".strip()


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _call_gemini_with_retry(user_prompt: str) -> str | None:
    """
    Gọi Gemini API với exponential backoff retry.
    Xử lý đúng 503 (overload) và 429 (rate limit).
    """
    client = _get_client()
    max_retries = 4
    base_delay  = 3  # giây

    for model in _MODEL_FALLBACKS:
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        temperature=0.5,
                        max_output_tokens=2048,
                    ),
                )
                logger.info("Gemini OK (model=%s, attempt=%d)", model, attempt)
                return response.text or ""

            except Exception as exc:
                err_str = str(exc)
                is_503  = "503" in err_str or "UNAVAILABLE" in err_str
                is_429  = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
                is_404  = "404" in err_str or "NOT_FOUND" in err_str

                if is_404:
                    logger.warning("Model %s khong kha dung (404), thu model tiep theo...", model)
                    break  # Thử model tiếp theo ngay

                if is_429:
                    # Rate limit – parse thời gian retry gợi ý từ API
                    import re as _re
                    m = _re.search(r"retry in (\d+(?:\.\d+)?)s", err_str)
                    wait = min(float(m.group(1)) if m else 60, 65)
                    logger.warning(
                        "Rate limit 429 (model=%s) – quota ngay hom nay da het. "
                        "Dung fallback mo ta goc. (Reset luc 0h)", model
                    )
                    # 429 = hết quota ngày → không retry, chuyển fallback
                    break

                if is_503 and attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1))  # 3, 6, 12, 24s
                    logger.warning(
                        "Gemini 503 (model=%s, lan %d/%d), thu lai sau %ds...",
                        model, attempt, max_retries, delay
                    )
                    time.sleep(delay)
                    continue

                logger.error("Gemini error (model=%s): %s", model, exc)
                break

    return None  # Tất cả thất bại → dùng fallback


def summarize_articles(articles: list["Article"]) -> list[str]:
    """
    Tóm tắt batch tất cả bài. Fallback sang mô tả gốc nếu API thất bại.
    """
    if not articles:
        return []

    lines = []
    for i, art in enumerate(articles, 1):
        lines.append(
            f"[{i}] Title: {art['title']}\n"
            f"    Description: {art['summary_raw'] or '(no description)'}"
        )
    user_prompt = (
        f"Tom tat {len(articles)} bai sau day, moi bai mot doan, "
        f"danh so [1], [2], ... tuong ung:\n\n" + "\n\n".join(lines)
    )

    raw_output = _call_gemini_with_retry(user_prompt)

    if raw_output:
        summaries = _parse_numbered_output(raw_output, len(articles))
        logger.info("Da tom tat %d bai thanh cong.", len(articles))
        return summaries

    # Fallback: dùng mô tả gốc (đã clean), giới hạn 300 ký tự
    logger.warning("Dung fallback mo ta goc cho %d bai.", len(articles))
    return [
        (art["summary_raw"][:300] + "...") if len(art["summary_raw"]) > 300
        else (art["summary_raw"] or art["title"])
        for art in articles
    ]


def _parse_numbered_output(text: str, expected_count: int) -> list[str]:
    """Parse output dạng [1] ... [2] ... thành list string."""
    pattern = re.compile(r"\[(\d+)\]\s*(.+?)(?=\[\d+\]|\Z)", re.DOTALL)
    matches  = pattern.findall(text)

    result: dict[int, str] = {}
    for num_str, content in matches:
        result[int(num_str)] = content.strip().replace("\n", " ")

    return [
        result.get(i, "Tom tat chua kha dung.")
        for i in range(1, expected_count + 1)
    ]


def summarize_all_topics(
    topics_data: dict[str, list["Article"]],
) -> dict[str, list[str]]:
    """Tóm tắt tất cả chủ đề."""
    result: dict[str, list[str]] = {}
    for topic_key, articles in topics_data.items():
        logger.info("Tom tat topic '%s' (%d bai)...", topic_key, len(articles))
        result[topic_key] = summarize_articles(articles)
    return result
