# TLSWatch

Automated TLScontact London appointment slot monitor for French Schengen visa applications.

Runs every 10–15 minutes via GitHub Actions (free). Sends instant Telegram push notification + backup email when a slot appears. Zero cost, zero maintenance after setup.

**→ See [SETUP_GUIDE.md](SETUP_GUIDE.md) for full step-by-step setup instructions (no coding required).**

---

## How it works

- GitHub Actions runs `checker.py` on a schedule (weekdays every 12 min, weekends every 15 min)
- Playwright launches a headless browser with bot-detection mitigations, logs into TLScontact, and checks for available appointment slots
- If a slot is found: sends a Telegram message and email with a direct booking link
- If blocked by Cloudflare: sends a Telegram warning and waits for the next run
- All credentials are stored as GitHub Secrets — never in code

## Secrets required

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `GMAIL_ADDRESS` | Gmail address for sending alerts |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your real password) |
| `TLS_EMAIL` | TLScontact account email |
| `TLS_PASSWORD` | TLScontact account password |
| `TLS_ORDER_ID` | Order ID from the appointment booking URL (the number at the end) |
| `NOTIFY_EMAIL` | Email address to receive alerts |
