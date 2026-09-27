"""
config.py – Cấu hình tập trung cho Tech Daily Digest
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Credentials
# ──────────────────────────────────────────────
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "")
GMAIL_USER        = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL   = os.getenv("RECIPIENT_EMAIL", "minhvuhoang4104@gmail.com")

# ──────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────
TIMEZONE    = "Asia/Ho_Chi_Minh"
SEND_HOUR   = int(os.getenv("SEND_HOUR", "7"))
SEND_MINUTE = int(os.getenv("SEND_MINUTE", "0"))

# ──────────────────────────────────────────────
# Giới hạn bài mỗi chủ đề
# ──────────────────────────────────────────────
MAX_ARTICLES_PER_TOPIC = 5
FETCH_HOURS_BACK       = 48   # Lấy bài trong 48h (tăng để luôn có đủ tin)

# ──────────────────────────────────────────────
# Gemini Model
# ──────────────────────────────────────────────
GEMINI_MODEL = "gemini-3.8-flash"

# ──────────────────────────────────────────────
# Email Theme Colors – Deep Navy Dark
# ──────────────────────────────────────────────
COLOR_BG         = "#05080F"   # Gần đen tuyệt đối
COLOR_HEADER_TOP = "#000B2E"   # Navy cực đậm
COLOR_HEADER_BOT = "#001166"   # Navy đậm
COLOR_SECTION    = "#080D1F"   # Section nền rất đậm
COLOR_CARD       = "#0A0E1C"   # Card nền đậm
COLOR_BORDER     = "#0A1A6E"   # Border navy đậm
COLOR_TEXT       = "#FFFFFF"   # Trắng
COLOR_TEXT_MUTED = "#A8B8D8"   # Xám xanh nhạt
COLOR_ACCENT     = "#3B7FFF"   # Xanh sáng accent
COLOR_BTN        = "#0033CC"   # Nút xanh navy đậm

# ──────────────────────────────────────────────
# RSS Feeds theo chủ đề
# ──────────────────────────────────────────────
RSS_FEEDS = {
    "java": {
        "icon": "☕",
        "label": "Java Backend",
        "feeds": [
            ("Baeldung",          "https://feeds.feedburner.com/Baeldung"),
            ("InfoQ Java",        "https://www.infoq.com/java/rss/"),
            ("JetBrains Blog",    "https://blog.jetbrains.com/feed/"),
            ("Spring Blog",       "https://spring.io/blog.atom"),
            ("DZone Java",        "https://feeds.dzone.com/java"),
            ("Dev.to Java",       "https://dev.to/feed/tag/java"),
        ],
    },
    "ai": {
        "icon": "🤖",
        "label": "Artificial Intelligence",
        "feeds": [
            ("Google AI Blog",    "https://blog.research.google/feeds/posts/default"),
            ("The Verge AI",      "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
            ("VentureBeat AI",    "https://venturebeat.com/category/ai/feed/"),
            ("Hacker News AI",    "https://hnrss.org/newest?q=AI+LLM&count=20"),
            ("MIT Tech Review AI","https://www.technologyreview.com/topic/artificial-intelligence/feed"),
            ("Dev.to AI",         "https://dev.to/feed/tag/ai"),
        ],
    },
    "architecture": {
        "icon": "🏗️",
        "label": "Solution Architecture",
        "feeds": [
            ("The New Stack",     "https://thenewstack.io/feed/"),
            ("AWS Blog",          "https://aws.amazon.com/blogs/architecture/feed/"),
            ("InfoQ Architecture","https://www.infoq.com/architecture-design/rss/"),
            ("Netflix Tech Blog", "https://netflixtechblog.com/feed"),
            ("Martin Fowler",     "https://martinfowler.com/feed.atom"),
            ("Dev.to DevOps",     "https://dev.to/feed/tag/devops"),
        ],
    },
}
