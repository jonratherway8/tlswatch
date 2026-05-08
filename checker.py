import os
import random
import shutil
import smtplib
import ssl
import subprocess
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ── Jitter ───────────────────────────────────────────────────────────────────
jitter = random.randint(0, 180)
print(f"Sleeping {jitter}s for jitter...")
time.sleep(jitter)

# ── Config ────────────────────────────────────────────────────────────────────
TLS_EMAIL    = os.environ["TLS_EMAIL"]
TLS_PASSWORD = os.environ["TLS_PASSWORD"]
TLS_ORDER_ID = os.environ["TLS_ORDER_ID"]

BASE_URL  = "https://visas-fr.tlscontact.com"
LOGIN_URL = f"{BASE_URL}/en-us/login"
APPT_URL  = f"{BASE_URL}/workflow/appointment-booking/gbLON2fr/{TLS_ORDER_ID}"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
GMAIL_ADDRESS      = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL       = os.environ.get("NOTIFY_EMAIL", "")

PROFILE_DIR = Path.home() / ".tlswatch-profile"
CDP_PORT    = 9222

UK_TZ = timezone(timedelta(hours=1))  # BST; change to timedelta(0) in winter

NO_SLOT_TEXT = "we currently don't have any appointment slots available"

BLOCK_INDICATORS = [
    "just a moment",
    "access denied",
    "403",
    "429",
    "attention required",
    "ddos-guard",
    "enable javascript and cookies",
]

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


# ── Notifications ─────────────────────────────────────────────────────────────

def uk_now() -> str:
    return datetime.now(UK_TZ).strftime("%d %b %Y %H:%M:%S %Z")


def send_telegram(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured — skipping.")
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        resp.raise_for_status()
        print("Telegram sent.")
    except Exception as exc:
        print(f"Telegram failed: {exc}")


def send_email(subject: str, body: str) -> None:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD or not NOTIFY_EMAIL:
        print("Email not configured — skipping.")
        return
    try:
        msg = (
            f"From: {GMAIL_ADDRESS}\r\n"
            f"To: {NOTIFY_EMAIL}\r\n"
            f"Subject: {subject}\r\n"
            f"Content-Type: text/plain; charset=utf-8\r\n"
            f"\r\n"
            f"{body}"
        )
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.sendmail(GMAIL_ADDRESS, NOTIFY_EMAIL, msg.encode("utf-8"))
        print("Email sent.")
    except Exception as exc:
        print(f"Email failed: {exc}")


def notify_slot_found() -> None:
    now = uk_now()
    send_telegram(
        "🇫🇷 <b>APPOINTMENT SLOT AVAILABLE</b>\n\n"
        "A France visa appointment slot has appeared at TLScontact London.\n\n"
        f"👉 Book now: {APPT_URL}\n\n"
        f"⏰ Detected at: {now}\n\n"
        "Slots disappear fast — open the link immediately!"
    )
    send_email(
        "🇫🇷 TLS SLOT AVAILABLE — Book now",
        (
            "APPOINTMENT SLOT AVAILABLE\n\n"
            "A France visa appointment slot has appeared at TLScontact London.\n\n"
            f"Book now: {APPT_URL}\n\n"
            f"Detected at: {now}\n\n"
            "Slots disappear fast — open the link immediately!"
        ),
    )


def notify_blocked() -> None:
    send_telegram(
        "⚠️ <b>TLSWatch blocked</b>\n\n"
        "TLScontact appears to have blocked this check (CAPTCHA or access denied).\n"
        "Monitoring will resume on the next scheduled run (~12 minutes).\n\n"
        f"⏰ {uk_now()}"
    )


def notify_error(err: str) -> None:
    send_telegram(
        f"🔴 <b>TLSWatch error</b>\n\n"
        f"<pre>{err[:800]}</pre>\n\n"
        f"⏰ {uk_now()}"
    )


# ── Browser helpers ───────────────────────────────────────────────────────────

def human_delay(lo: float = 1.0, hi: float = 3.0) -> None:
    time.sleep(random.uniform(lo, hi))


def is_blocked(page) -> bool:
    title = page.title().lower()
    url   = page.url.lower()
    return any(ind in title or ind in url for ind in BLOCK_INDICATORS)


def page_text(page) -> str:
    try:
        return page.inner_text("body").lower()
    except Exception:
        return page.content().lower()


def find_chrome():
    for path in CHROME_PATHS:
        if Path(path).exists():
            return path
    for name in ("google-chrome", "chromium-browser", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return None


def cdp_ready(port: int, timeout: int = 2) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


# ── Login ─────────────────────────────────────────────────────────────────────

def try_login(page) -> bool:
    print(f"Navigating to login: {LOGIN_URL}")
    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    except PlaywrightTimeout:
        print("Login page timeout.")
        return False

    # Wait up to 60s for any Cloudflare challenge on the login page
    deadline = time.time() + 60
    while is_blocked(page) and time.time() < deadline:
        print(f"Waiting for CF challenge on login... Title={page.title()!r}")
        time.sleep(3)

    if is_blocked(page):
        print(f"Blocked on login page after 60s. Title={page.title()!r}")
        return False

    human_delay(1, 2)

    # If already redirected away from login, session is still alive
    if not any(kw in page.url.lower() for kw in ["login", "signin", "/auth"]):
        print(f"Already authenticated. URL={page.url}")
        return True

    # ── Email ──
    email_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[id="email"]',
        'input[placeholder*="mail" i]',
        'input[autocomplete="email"]',
        'input[autocomplete="username"]',
    ]
    email_el = None
    for sel in email_selectors:
        try:
            email_el = page.wait_for_selector(sel, timeout=5000)
            if email_el:
                print(f"Email field: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not email_el:
        print(f"Email field not found. URL={page.url!r}")
        return False

    try:
        email_el.click()
        human_delay(0.3, 0.8)
        email_el.type(TLS_EMAIL, delay=random.randint(50, 120))
    except Exception as exc:
        print(f"Email fill failed: {exc}")
        return False

    human_delay(0.5, 1.2)

    # ── Password ──
    password_selectors = [
        'input[type="password"]',
        'input[name="password"]',
        'input[id="password"]',
        'input[placeholder*="password" i]',
        'input[autocomplete="current-password"]',
    ]
    password_el = None
    for sel in password_selectors:
        try:
            password_el = page.wait_for_selector(sel, timeout=5000)
            if password_el:
                print(f"Password field: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not password_el:
        print(f"Password field not found. URL={page.url!r}")
        return False

    try:
        password_el.click()
        human_delay(0.3, 0.8)
        password_el.type(TLS_PASSWORD, delay=random.randint(50, 120))
    except Exception as exc:
        print(f"Password fill failed: {exc}")
        return False

    human_delay(0.5, 1.5)

    # ── Submit ──
    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Sign in")',
        'button:has-text("Log in")',
        'button:has-text("Login")',
        'button:has-text("Continue")',
        'button:has-text("Se connecter")',
    ]
    submitted = False
    for sel in submit_selectors:
        try:
            btn = page.query_selector(sel)
            if btn:
                print(f"Submit: {sel}")
                btn.click()
                submitted = True
                break
        except Exception:
            continue

    if not submitted:
        try:
            password_el.press("Enter")
            submitted = True
            print("Submit via Enter.")
        except Exception as exc:
            print(f"Submit fallback failed: {exc}")
            return False

    human_delay(2, 4)
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except PlaywrightTimeout:
        pass

    # i2-auth.visas-fr.tlscontact.com (Keycloak) has its own CF protection —
    # wait for it to auto-solve before checking the outcome.
    deadline = time.time() + 60
    while is_blocked(page) and time.time() < deadline:
        print(f"Waiting for CF challenge after submit... Title={page.title()!r}")
        time.sleep(3)

    # Give the OAuth redirect chain (auth-callback → dashboard) time to settle.
    human_delay(3, 5)
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
    except PlaywrightTimeout:
        pass

    final_url = page.url.lower()
    print(f"Post-submit URL: {page.url}")

    # Success: landed back on the main domain (not the auth server).
    if "visas-fr.tlscontact.com" in final_url and "i2-auth" not in final_url:
        if not any(kw in final_url for kw in ["login", "signin", "connexion"]):
            print(f"Login OK. URL: {page.url}")
            return True

    print(f"Login failed. URL={page.url!r}")
    return False


# ── Slot detection ────────────────────────────────────────────────────────────

def detect_slots(page) -> str:
    print(f"Navigating to appointment page: {APPT_URL}")
    try:
        page.goto(APPT_URL, wait_until="domcontentloaded", timeout=30000)
        human_delay(3, 5)
    except PlaywrightTimeout:
        print("Appointment page timeout.")
        return "blocked"

    if is_blocked(page):
        return "blocked"

    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeout:
        pass

    if is_blocked(page):
        return "blocked"

    # If redirected to login, session expired
    if any(kw in page.url.lower() for kw in ["login", "signin", "/auth"]):
        print("Redirected to login — session expired.")
        return "session_expired"

    body = page_text(page)
    print(f"Page text snippet: {body[:200]!r}")

    if NO_SLOT_TEXT in body:
        return "no_slots"

    secondary = [
        "no slots are currently available",
        "no appointment",
        "aucun créneau",
        "no available",
        "currently unavailable",
    ]
    if any(p in body for p in secondary):
        return "no_slots"

    if "appointment-booking" in page.url or "book your appointment" in body:
        print("On appointment page, no 'no slots' text → slots available!")
        return "slots"

    print(f"Ambiguous. URL={page.url!r} title={page.title()!r}")
    print(f"Body: {body[:400]!r}")
    return "no_slots"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> int:
    print(f"Profile: {PROFILE_DIR}")
    print(f"Appointment URL: {APPT_URL}")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    chrome_bin = find_chrome()
    chrome_proc = None

    # Launch real Chrome via subprocess — no automation flags, no webdriver flag,
    # undetectable to Cloudflare. Profile preserves cf_clearance between runs.
    if not cdp_ready(CDP_PORT, timeout=2):
        if not chrome_bin:
            print("Google Chrome not found. Install it at https://www.google.com/chrome/")
            return 1
        print(f"Launching Chrome: {chrome_bin}")
        chrome_proc = subprocess.Popen([
            chrome_bin,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
        ])
        if not cdp_ready(CDP_PORT, timeout=20):
            print("Chrome failed to start within 20s.")
            chrome_proc.terminate()
            return 1
    else:
        print(f"Reusing Chrome already running on port {CDP_PORT}.")

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

            if browser.contexts:
                ctx = browser.contexts[0]
                page = ctx.new_page()
            else:
                ctx = browser.new_context(
                    locale="en-GB",
                    extra_http_headers={"Accept-Language": "en-GB,en;q=0.9"},
                )
                page = ctx.new_page()

            # Landing probe
            try:
                page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
            except PlaywrightTimeout:
                print("Site unreachable.")
                notify_blocked()
                page.close()
                return 0

            # Wait up to 60s for Cloudflare challenge to auto-solve
            deadline = time.time() + 60
            while is_blocked(page) and time.time() < deadline:
                print(f"Waiting for CF challenge... Title={page.title()!r}")
                time.sleep(3)

            if is_blocked(page):
                print(f"Blocked on landing after 60s. Title={page.title()!r}")
                notify_blocked()
                page.close()
                return 0

            # Login (skipped if session cookie still valid)
            try:
                login_ok = try_login(page)
            except Exception as exc:
                print(f"Login exception: {exc}")
                login_ok = False

            if not login_ok or is_blocked(page):
                notify_blocked()
                page.close()
                return 0

            # Detect slots
            try:
                result = detect_slots(page)
            except Exception as exc:
                print(f"Detection exception: {exc}")
                result = "blocked"

            # Session expired mid-run → re-login once
            if result == "session_expired":
                print("Session expired — re-logging in.")
                try:
                    login_ok = try_login(page)
                    result = detect_slots(page) if login_ok else "blocked"
                except Exception as exc:
                    print(f"Re-login failed: {exc}")
                    result = "blocked"

            page.close()

        ts = uk_now()
        if result == "slots":
            print(f"SLOTS FOUND at {ts}!")
            notify_slot_found()
        elif result == "no_slots":
            print(f"No slots at {ts}.")
        else:
            print(f"Blocked at {ts}.")
            notify_blocked()

        return 0

    except Exception:
        tb = traceback.format_exc()
        print(f"Unhandled error:\n{tb}")
        notify_error(tb)
        return 1

    finally:
        if chrome_proc:
            print("Terminating Chrome.")
            chrome_proc.terminate()
            try:
                chrome_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                chrome_proc.kill()


if __name__ == "__main__":
    sys.exit(run())
