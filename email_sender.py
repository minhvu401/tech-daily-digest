"""
email_sender.py – Gửi email qua Gmail SMTP với TLS
Có retry logic 3 lần, gửi cả HTML + plain-text fallback.
"""
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import pytz

import config

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
MAX_RETRIES = 3
RETRY_DELAY = 5  # giây


def send_email(html_body: str, plain_body: str, subject: str | None = None) -> bool:
    """
    Gửi email với nội dung HTML + plain-text fallback.
    Thử lại tối đa MAX_RETRIES lần nếu lỗi.
    Trả về True nếu gửi thành công.
    """
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    if subject is None:
        subject = f"🔷 Tech Daily Digest – {now.strftime('%d/%m/%Y')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Tech Daily Digest <{config.GMAIL_USER}>"
    msg["To"]      = config.RECIPIENT_EMAIL

    # Plain text trước (fallback)
    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    # HTML sau (ưu tiên hiển thị)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Đang gửi email (lần %d/%d)...", attempt, MAX_RETRIES)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
                server.sendmail(
                    config.GMAIL_USER,
                    config.RECIPIENT_EMAIL,
                    msg.as_bytes(),
                )
            logger.info("✅ Đã gửi email thành công đến %s", config.RECIPIENT_EMAIL)
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error("❌ Lỗi xác thực Gmail. Kiểm tra GMAIL_APP_PASSWORD: %s", e)
            return False  # Không retry lỗi auth
        except Exception as exc:
            logger.warning("⚠️  Lần %d thất bại: %s", attempt, exc)
            if attempt < MAX_RETRIES:
                logger.info("Thử lại sau %d giây...", RETRY_DELAY)
                time.sleep(RETRY_DELAY)

    logger.error("❌ Gửi email thất bại sau %d lần thử.", MAX_RETRIES)
    return False
