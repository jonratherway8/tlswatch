# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Automated TLScontact London appointment monitor for French Schengen visa applications. Runs on a self-hosted GitHub Actions runner (the user's Mac), checks for available slots every 12–15 minutes, and sends a Telegram push notification when one appears.

## Running the checker

```bash
# Install dependencies (no browser download needed — uses system Chrome)
pip3 install -r requirements.txt

# Run locally (requires env vars set)
TLS_EMAIL=... TLS_PASSWORD=... TLS_ORDER_ID=... TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 checker.py
```

## Architecture

**Single-file script** (`checker.py`) triggered by GitHub Actions on a cron schedule.

### Cloudflare bypass approach

TLScontact (`visas-fr.tlscontact.com`) is protected by Cloudflare Turnstile. The only reliable bypass on a residential Mac is launching real Chrome as a subprocess — this produces a `navigator.webdriver = undefined` browser that Turnstile treats as a real user. Playwright then attaches via CDP (`connect_over_cdp`) purely as a remote control layer.

Key constraints:
- **Must use `subprocess.Popen`** to launch Chrome, not `playwright.launch()` — Playwright's launch injects `--enable-automation` which Cloudflare detects even with mitigation flags
- **Persistent profile** at `~/.tlswatch-profile` stores `cf_clearance` and TLS session cookies between runs (~24h TTL), so only the first run after expiry requires the Turnstile challenge to auto-solve
- The auth server `i2-auth.visas-fr.tlscontact.com` (Keycloak/OpenID Connect) is a separate domain with its own Cloudflare challenge — the script waits up to 60s for it after form submit

### Login flow

`visas-fr.tlscontact.com/en-us/login` → redirects to `i2-auth.visas-fr.tlscontact.com` (Keycloak) → form submit → OAuth redirect chain back to `visas-fr.tlscontact.com/en-us/auth-callback` → dashboard. Login success is detected by landing on `visas-fr.tlscontact.com` with `i2-auth` absent from the URL.

### Slot detection

Looks for the exact string `"we currently don't have any appointment slots available"` in the body of `APPT_URL`. Absence of this string on the appointment page = slot found.

### Credentials and secrets

All sensitive values are GitHub Secrets, passed as env vars in `check.yml`. `TLS_ORDER_ID` is the numeric ID at the end of the appointment booking URL.

## Self-hosted runner requirement

The workflow runs on `runs-on: self-hosted` (the user's Mac). GitHub-hosted runners are datacenter IPs which Cloudflare blocks. The runner is installed as a macOS launch agent so it can display GUI windows (needed for Turnstile auto-solve on first run after `cf_clearance` expires).

No browser install step in CI — system Chrome at `/Applications/Google Chrome.app` is used directly.
