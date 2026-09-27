"""
email_renderer.py – Render HTML email đẹp với dark theme xanh đậm & đen
Responsive, inline CSS, tương thích Gmail/Outlook.
"""
from datetime import datetime
import pytz

import config
from news_fetcher import Article


def _vn_weekday(weekday: int) -> str:
    names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    return names[weekday]


def render_html(
    topics_data: dict[str, list[Article]],
    summaries: dict[str, list[str]],
) -> str:
    """Tạo chuỗi HTML hoàn chỉnh cho email."""

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    date_str = f"{_vn_weekday(now.weekday())}, {now.day:02d}/{now.month:02d}/{now.year}"

    # ──────────────────── Tính tổng số bài ────────────────────
    total_articles = sum(len(arts) for arts in topics_data.values())

    # ──────────────────── Build section cards ─────────────────
    sections_html = ""
    for topic_key, topic_cfg in config.RSS_FEEDS.items():
        articles = topics_data.get(topic_key, [])
        topic_summaries = summaries.get(topic_key, [])
        icon  = topic_cfg["icon"]
        label = topic_cfg["label"]

        if not articles:
            card_html = f"""
            <tr>
              <td style="padding:12px 20px;color:{config.COLOR_TEXT_MUTED};font-style:italic;font-size:14px;">
                Không tìm thấy bài mới trong 48 giờ qua.
              </td>
            </tr>"""
        else:
            cards = []
            for i, art in enumerate(articles):
                summary_text = topic_summaries[i] if i < len(topic_summaries) else art["summary_raw"][:150]
                cards.append(_article_card(art, summary_text))
            card_html = "".join(cards)

        sections_html += f"""
        <!-- SECTION: {label} -->
        <tr>
          <td style="padding:0 0 24px 0;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <!-- Section Header -->
              <tr>
                <td style="
                  background:linear-gradient(135deg,{config.COLOR_HEADER_TOP},{config.COLOR_HEADER_BOT});
                  padding:14px 20px;
                  border-radius:8px 8px 0 0;
                ">
                  <span style="font-size:22px;">{icon}</span>
                  <span style="
                    color:{config.COLOR_TEXT};
                    font-size:16px;
                    font-weight:700;
                    letter-spacing:1px;
                    text-transform:uppercase;
                    vertical-align:middle;
                    margin-left:10px;
                  ">{label}</span>
                </td>
              </tr>
              <!-- Articles -->
              {card_html}
            </table>
          </td>
        </tr>"""

    # ──────────────────── Full HTML ───────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Tech Daily Digest – {date_str}</title>
</head>
<body style="margin:0;padding:0;background-color:#02040A;font-family:'Segoe UI',Roboto,Arial,sans-serif;">

  <!-- WRAPPER -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#02040A;padding:24px 0;">
    <tr>
      <td align="center">

        <!-- CONTAINER (max 640px) -->
        <table width="640" cellpadding="0" cellspacing="0" border="0"
               style="max-width:640px;width:100%;">

          <!-- HEADER -->
          <tr>
            <td style="
              background:linear-gradient(160deg,#00082A 0%,#000E50 50%,#001480 100%);
              padding:36px 30px 28px;
              border-radius:12px 12px 0 0;
              text-align:center;
              border-bottom:3px solid {config.COLOR_ACCENT};
            ">
              <div style="font-size:36px;margin-bottom:6px;">🔷</div>
              <h1 style="
                margin:0;padding:0;
                color:{config.COLOR_TEXT};
                font-size:26px;
                font-weight:800;
                letter-spacing:2px;
                text-transform:uppercase;
              ">Tech Daily Digest</h1>
              <p style="
                margin:10px 0 0;
                color:{config.COLOR_ACCENT};
                font-size:14px;
                letter-spacing:1px;
              ">{date_str} &nbsp;|&nbsp; {total_articles} bài mới nhất</p>
            </td>
          </tr>

          <!-- INTRO BAR -->
          <tr>
            <td style="
              background:{config.COLOR_SECTION};
              padding:12px 24px;
              border-left:4px solid {config.COLOR_ACCENT};
            ">
              <p style="margin:0;color:{config.COLOR_TEXT_MUTED};font-size:13px;line-height:1.5;">
                ☀️ Chào buổi sáng! Dưới đây là tổng hợp tin tức
                <strong style="color:{config.COLOR_TEXT};">Java BE · AI · Solution Architecture</strong>
                được chọn lọc và tóm tắt bởi Gemini AI.
              </p>
            </td>
          </tr>

          <!-- CONTENT -->
          <tr>
            <td style="background:{config.COLOR_BG};padding:24px 20px 8px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {sections_html}
              </table>
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="
              background:#02040A;
              padding:20px 24px;
              border-top:1px solid {config.COLOR_BORDER};
              border-radius:0 0 12px 12px;
              text-align:center;
            ">
              <p style="margin:0 0 6px;color:{config.COLOR_TEXT_MUTED};font-size:12px;">
                🤖 Tổng hợp tự động bởi <strong style="color:{config.COLOR_ACCENT};">Tech Daily Digest</strong>
                &nbsp;|&nbsp; Powered by <strong style="color:{config.COLOR_ACCENT};">Gemini AI</strong>
              </p>
              <p style="margin:0;color:#1E2A4A;font-size:11px;">
                Gửi lúc 7:00 AM GMT+7 mỗi ngày &nbsp;•&nbsp; Java · AI · Architecture
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""
    return html


def _article_card(art: Article, summary: str) -> str:
    """Render một thẻ bài viết."""
    title = art["title"]
    url   = art["url"]
    src   = art["source"]

    # Format ngày
    try:
        from datetime import datetime, timezone
        pub_dt = datetime.fromisoformat(art["published"])
        pub_dt = pub_dt.astimezone(pytz.timezone(config.TIMEZONE))
        pub_str = pub_dt.strftime("%d/%m %H:%M")
    except Exception:
        pub_str = ""

    return f"""
              <tr>
                <td style="
                  background:{config.COLOR_CARD};
                  border-left:3px solid {config.COLOR_ACCENT};
                  border-bottom:1px solid {config.COLOR_BORDER};
                  padding:16px 20px;
                ">
                  <!-- Meta row -->
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                        <span style="
                          background:{config.COLOR_HEADER_TOP};
                          color:{config.COLOR_ACCENT};
                          font-size:10px;
                          font-weight:700;
                          padding:2px 8px;
                          border-radius:10px;
                          letter-spacing:0.5px;
                          text-transform:uppercase;
                        ">{src}</span>
                        {f'<span style="color:{config.COLOR_TEXT_MUTED};font-size:11px;margin-left:8px;">{pub_str}</span>' if pub_str else ''}
                      </td>
                    </tr>
                  </table>
                  <!-- Title -->
                  <h3 style="
                    margin:10px 0 6px;
                    color:{config.COLOR_TEXT};
                    font-size:15px;
                    font-weight:700;
                    line-height:1.4;
                  ">{title}</h3>
                  <!-- Summary -->
                  <p style="
                    margin:0 0 12px;
                    color:{config.COLOR_TEXT_MUTED};
                    font-size:13px;
                    line-height:1.6;
                  ">{summary}</p>
                  <!-- CTA Button -->
                  <a href="{url}"
                     style="
                       display:inline-block;
                       background:{config.COLOR_BTN};
                       color:#FFFFFF;
                       font-size:12px;
                       font-weight:600;
                       padding:7px 16px;
                       border-radius:6px;
                       text-decoration:none;
                       letter-spacing:0.5px;
                     ">Đọc chi tiết &rarr;</a>
                </td>
              </tr>"""


def render_plain_text(
    topics_data: dict[str, list[Article]],
    summaries: dict[str, list[str]],
) -> str:
    """Render plain-text fallback cho email clients không hỗ trợ HTML."""
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    lines = [
        "=" * 60,
        f"  TECH DAILY DIGEST – {now.strftime('%d/%m/%Y')}",
        "=" * 60,
        "",
    ]
    for topic_key, topic_cfg in config.RSS_FEEDS.items():
        articles  = topics_data.get(topic_key, [])
        topic_sums = summaries.get(topic_key, [])
        lines.append(f"{topic_cfg['icon']} {topic_cfg['label'].upper()}")
        lines.append("-" * 40)
        if not articles:
            lines.append("  Không có bài mới.")
        for i, art in enumerate(articles):
            sm = topic_sums[i] if i < len(topic_sums) else ""
            lines.append(f"  {i+1}. {art['title']}")
            if sm:
                lines.append(f"     {sm}")
            lines.append(f"     🔗 {art['url']}")
            lines.append("")
        lines.append("")
    lines.append("=" * 60)
    lines.append("Powered by Gemini AI | Tech Daily Digest")
    return "\n".join(lines)
