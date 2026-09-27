# Tech Daily Digest 🔷

> Hệ thống tự động thu thập & gửi email tin tức công nghệ mỗi sáng 7h (GMT+7)

**Chủ đề:** Java Backend · Artificial Intelligence · Solution Architecture  
**Powered by:** Gemini AI + RSS Feeds

---

## Cài đặt

### Bước 1 – Cài Python dependencies

```bash
pip install -r requirements.txt
```

### Bước 2 – Cấu hình secrets

File `.env` đã được tạo sẵn với thông tin của bạn.  
Nếu cần thay đổi, mở `.env` và sửa:

```env
GEMINI_API_KEY=your_key_here
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
RECIPIENT_EMAIL=your_email@gmail.com
SEND_HOUR=7
SEND_MINUTE=0
```

> **Lưu ý Gmail App Password:**  
> Đây KHÔNG phải mật khẩu Gmail thường.  
> Vào: Google Account → Security → 2-Step Verification → App passwords → Tạo mới

---

## Sử dụng

### Gửi email thử ngay lập tức
```bash
python main.py --test
```

### Xem preview giao diện email (không gửi)
```bash
python main.py --preview
```
Sau đó mở file `preview.html` bằng trình duyệt.

### Khởi động scheduler (chạy tự động mỗi ngày 7h sáng)
```bash
python main.py
```

---

## Chạy nền (Windows)

Để hệ thống chạy nền ngay cả khi đóng terminal:

```bat
:: Tạo file run_background.bat
start /min pythonw main.py
```

Hoặc dùng **Windows Task Scheduler**:
1. Mở Task Scheduler → Create Basic Task
2. Trigger: Daily, 7:00 AM
3. Action: Start a program → `python.exe`
4. Arguments: `"d:\Dev\Automation Information\main.py" --test`

---

## Cấu trúc project

```
Automation Information/
├── main.py              # Entry point chính
├── config.py            # Cấu hình & RSS feeds
├── news_fetcher.py      # Thu thập tin tức từ RSS
├── ai_summarizer.py     # Tóm tắt với Gemini AI
├── email_renderer.py    # Render HTML email
├── email_sender.py      # Gửi qua Gmail SMTP
├── requirements.txt     # Dependencies
├── .env                 # Secrets (KHÔNG commit)
├── .env.example         # Template
├── .gitignore
├── logs/
│   └── email_history.log
└── README.md
```

---

## Nguồn tin RSS

| Chủ đề | Nguồn |
|---|---|
| ☕ Java Backend | Baeldung, InfoQ Java, JetBrains Blog, Spring Blog, DZone, Dev.to |
| 🤖 AI/ML | Google AI Blog, The Verge AI, VentureBeat, Hacker News, MIT Tech Review |
| 🏗️ Architecture | The New Stack, AWS Blog, InfoQ Arch, Netflix Tech Blog, Martin Fowler |

---

## Troubleshooting

| Lỗi | Giải pháp |
|---|---|
| `SMTPAuthenticationError` | Kiểm tra GMAIL_APP_PASSWORD (phải là App Password, không phải mật khẩu thường) |
| `GEMINI_API_KEY invalid` | Tạo key mới tại aistudio.google.com/apikey |
| Không có bài nào | Tăng `FETCH_HOURS_BACK` trong `config.py` lên 72 |
| Email vào Spam | Thêm sender vào Contacts Gmail |
