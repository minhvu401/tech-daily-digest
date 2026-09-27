"""
main.py – Entry point cho Tech Daily Digest

Usage:
  python main.py            # Khởi động scheduler (chạy nền mỗi ngày 7h sáng)
  python main.py --test     # Gửi email thử ngay lập tức
  python main.py --preview  # In HTML ra file preview.html, KHÔNG gửi email
"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import pytz

# ── Fix Unicode encoding trên Windows ──
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Đảm bảo thư mục logs tồn tại ──
Path("logs").mkdir(exist_ok=True)

# ── Cấu hình logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/email_history.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


def run_digest() -> bool:
    """Pipeline chính: fetch → summarize → render → send."""
    logger.info("══════════════════════════════════════")
    logger.info("  Tech Daily Digest – Bắt đầu xử lý  ")
    logger.info("══════════════════════════════════════")

    # 1. Thu thập tin tức
    logger.info("📡 [1/4] Đang thu thập RSS feeds...")
    from news_fetcher import fetch_all_topics
    topics_data = fetch_all_topics()

    total = sum(len(v) for v in topics_data.values())
    logger.info("   ✔ Thu thập được %d bài tổng cộng", total)
    for k, v in topics_data.items():
        logger.info("   • %s: %d bài", k, len(v))

    if total == 0:
        logger.warning("⚠️  Không tìm thấy bài nào! Kiểm tra kết nối mạng.")

    # 2. Tóm tắt với Gemini AI
    logger.info("🤖 [2/4] Đang tóm tắt bằng Gemini AI...")
    from ai_summarizer import summarize_all_topics
    summaries = summarize_all_topics(topics_data)
    logger.info("   ✔ Tóm tắt hoàn tất")

    # 3. Render email
    logger.info("🎨 [3/4] Đang render HTML email...")
    from email_renderer import render_html, render_plain_text
    html_body  = render_html(topics_data, summaries)
    plain_body = render_plain_text(topics_data, summaries)
    logger.info("   ✔ Render hoàn tất (%d chars HTML)", len(html_body))

    # 4. Gửi email
    logger.info("📧 [4/4] Đang gửi email...")
    from email_sender import send_email
    success = send_email(html_body, plain_body)

    if success:
        logger.info("🎉 Pipeline hoàn tất thành công!")
    else:
        logger.error("❌ Pipeline thất bại ở bước gửi email.")

    return success


def preview_digest() -> None:
    """Render và lưu HTML ra file, không gửi email."""
    logger.info("🔍 Preview mode – Đang tạo preview.html...")

    from news_fetcher import fetch_all_topics
    from ai_summarizer import summarize_all_topics
    from email_renderer import render_html, render_plain_text

    topics_data = fetch_all_topics()
    summaries   = summarize_all_topics(topics_data)
    html_body   = render_html(topics_data, summaries)
    plain_body  = render_plain_text(topics_data, summaries)

    out_path = Path("preview.html")
    out_path.write_text(html_body, encoding="utf-8")

    print(f"\n✅ Đã tạo: {out_path.absolute()}")
    print("   Mở file bằng trình duyệt để xem giao diện email.\n")
    print("─" * 50)
    print("PLAIN TEXT PREVIEW:")
    print("─" * 50)
    print(plain_body)


def start_scheduler() -> None:
    """Khởi động APScheduler, chạy run_digest() mỗi ngày lúc SEND_HOUR:SEND_MINUTE."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    import config

    scheduler = BlockingScheduler(timezone=config.TIMEZONE)
    scheduler.add_job(
        run_digest,
        trigger="cron",
        hour=config.SEND_HOUR,
        minute=config.SEND_MINUTE,
        id="daily_digest",
        name="Tech Daily Digest",
        misfire_grace_time=600,  # Cho phép trễ 10 phút
    )

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    logger.info("═══════════════════════════════════════════════")
    logger.info("  🗓️  Scheduler đã khởi động!")
    logger.info("  ⏰  Gửi email lúc %02d:%02d mỗi ngày (GMT+7)", config.SEND_HOUR, config.SEND_MINUTE)
    logger.info("  📧  Đến: %s", config.RECIPIENT_EMAIL)
    logger.info("  🕐  Thời gian hiện tại: %s", now.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("  ⌛  Nhấn Ctrl+C để dừng.")
    logger.info("═══════════════════════════════════════════════")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler đã dừng.")


def validate_config() -> bool:
    """Kiểm tra cấu hình trước khi chạy."""
    import config
    errors = []
    if not config.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY chưa được đặt trong .env")
    if not config.GMAIL_USER:
        errors.append("GMAIL_USER chưa được đặt trong .env")
    if not config.GMAIL_APP_PASSWORD:
        errors.append("GMAIL_APP_PASSWORD chưa được đặt trong .env")
    if errors:
        for err in errors:
            logger.error("❌ Config error: %s", err)
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tech Daily Digest – Automation Email Tin Tức Công Nghệ"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Gửi email thử ngay lập tức (không cần đợi 7h sáng)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Render HTML ra file preview.html, KHÔNG gửi email",
    )
    args = parser.parse_args()

    if not validate_config():
        logger.error("Vui lòng kiểm tra file .env")
        sys.exit(1)

    if args.preview:
        preview_digest()
    elif args.test:
        logger.info("🧪 Chế độ TEST – Gửi email ngay bây giờ...")
        ok = run_digest()
        sys.exit(0 if ok else 1)
    else:
        start_scheduler()
