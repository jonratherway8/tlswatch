# TLSWatch Setup Guide

**No coding required. Follow each step in order. If something looks different on your screen, look for something with a similar name — the GitHub interface changes occasionally but the structure stays the same.**

---

## What you'll need before you start

- A computer with internet access and a web browser
- Your TLScontact account email and password
- The Telegram app installed on your iPhone
- A personal Gmail account *(optional — only needed for backup email alerts)*

This will take about 30–45 minutes to set up. Once done, it runs automatically 24/7.

---

## Part 1: Create a GitHub Account

GitHub is a free website where you can store and run code automatically. Think of it like Dropbox, but for code.

**Step 1.** Open your web browser and go to **https://github.com**

**Step 2.** Click the **"Sign up"** button in the top-right corner.

**Step 3.** Enter your email address, create a password, and choose a username. Click **"Continue"** after each field.

**Step 4.** Complete the verification puzzle (usually clicking images). Then click **"Create account"**.

**Step 5.** Check your email for a confirmation code from GitHub. Enter it on the page. You now have a GitHub account.

---

## Part 2: Create the Repository

A repository is like a folder on GitHub where your files will live.

**Step 6.** Once logged in to GitHub, look for the **"+"** icon in the top-right corner of the page. Click it, then click **"New repository"**.

**Step 7.** Fill in the form:
- **Repository name:** `tlswatch`
- **Description:** (optional) `TLScontact appointment slot monitor`
- **Visibility:** Select **Public** — this is important! Public repos get more free run time.
- Leave everything else unchecked.

**Step 8.** Click the green **"Create repository"** button at the bottom.

You'll see a mostly empty page. That's normal — we're about to add files.

---

## Part 3: Upload the Files

You need to upload 4 files and 1 file inside a special folder structure.

### Upload the main files first

**Step 9.** On your repository page, click **"Add file"** → **"Upload files"**.

**Step 10.** Drag and drop (or click "choose your files" to browse to) these 4 files:
- `checker.py`
- `requirements.txt`
- `README.md`
- `SETUP_GUIDE.md`

**Step 11.** At the bottom of the page, leave the commit message as-is and click **"Commit changes"**.

### Upload the workflow file (this goes inside a special folder)

The workflow file must be placed at `.github/workflows/check.yml`. GitHub won't let you drag a file into a non-existent folder, so we create it with a trick.

**Step 12.** Click **"Add file"** → **"Create new file"**.

**Step 13.** In the file name box at the top, type exactly: `.github/workflows/check.yml`
(As you type the `/` characters, GitHub automatically creates the folders. You'll see `.github/` and `workflows/` appear as folder breadcrumbs.)

**Step 14.** Open the `check.yml` file you downloaded on your computer in a text editor (on Mac: right-click → Open With → TextEdit; on Windows: right-click → Open With → Notepad).

**Step 15.** Select all the text (Ctrl+A on Windows, Cmd+A on Mac), copy it, then paste it into the big text area on the GitHub page.

**Step 16.** Click the green **"Commit changes"** button. In the popup, click **"Commit changes"** again.

Your repository now has all the files it needs.

---

## Part 4: Create a Telegram Bot

Telegram lets the monitor send you instant notifications to your iPhone.

**Step 17.** Open Telegram on your iPhone. In the search bar at the top, search for **BotFather**.

**Step 18.** Tap the result that shows a blue tick (official bot). Tap **Start** or **"/"** to begin chatting.

**Step 19.** Send the following message to BotFather (type it or copy-paste):
```
/newbot
```

**Step 20.** BotFather will ask for a name. Type any name you like, for example:
```
TLS Slot Watcher
```

**Step 21.** BotFather will ask for a username. It must end in `bot`, for example:
```
tlsslotwatch_bot
```
(If that username is taken, try adding numbers, like `tlsslotwatch2024_bot`.)

**Step 22.** BotFather will reply with a message containing your **bot token**. It looks like:
```
1234567890:ABCdefGHIjklMNOpqrSTUVwxyz-abc1234567
```
Copy this token and save it somewhere safe — you'll need it in Part 6.

**Step 23.** Now start a chat with your new bot. Search for your bot's username in Telegram (the one you chose in Step 21) and tap **Start**.

**Step 24.** Send any message to your bot, for example:
```
hello
```
(This is needed so the bot knows your chat ID.)

### Get your Telegram Chat ID

**Step 25.** In your phone or computer browser, open this URL (replace `YOUR_TOKEN` with the token from Step 22):
```
https://api.telegram.org/botYOUR_TOKEN/getUpdates
```
For example, if your token is `1234567890:ABCdef...`, the URL would be:
```
https://api.telegram.org/bot1234567890:ABCdef.../getUpdates
```

**Step 26.** The page will show some text. Look for `"chat":{"id":` followed by a number. That number is your **chat ID**. It might look like `987654321`. Copy it.

If you see `{"ok":true,"result":[]}` (empty result), go back to Telegram, send another message to your bot, then refresh the page.

---

## Part 5: Create a Gmail App Password *(optional — skip if you only want Telegram alerts)*

Email is a backup notification. **Telegram alone is sufficient** — if you prefer not to set up email, skip this entire part and go straight to Part 6. Leave the three email secrets (`GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `NOTIFY_EMAIL`) blank when you reach Part 6.

> **"The setting you are looking for is not available for your account"?**
> This means your Google account is a work, school, or organisation account (Google Workspace) — App Passwords are disabled by the admin. You have two options: skip email entirely (recommended), or create a free personal Gmail account at https://gmail.com and use that instead.

For security, Gmail requires a special "App Password" for automated scripts — not your real Gmail password.

**Step 27.** Go to **https://myaccount.google.com** and log in with a **personal** Gmail account (not a work or school one).

**Step 28.** Click on **"Security"** in the left sidebar.

**Step 29.** Look for **"2-Step Verification"** and make sure it is turned on. (If it says "Off", click it and follow the steps to turn it on — you'll need to verify your phone number.)

**Step 30.** Once 2-Step Verification is on, go back to the Security page and search for **"App passwords"** in the search bar at the top of the page. Click it.

**Step 31.** At the bottom of the App passwords page, in the text box that says "App name", type:
```
TLSWatch
```
Then click **"Create"**.

**Step 32.** Google will show you a 16-character password in a yellow box, like:
```
abcd efgh ijkl mnop
```
Copy all 16 characters (with or without the spaces — both work). This is your **Gmail App Password**. Save it somewhere safe.

---

## Part 6: Add All Secrets to GitHub

Secrets are like a locked safe inside your repository. The monitor reads them when it runs, but they're never visible to anyone.

**Step 33.** Go back to your `tlswatch` repository on GitHub.

**Step 34.** Click the **"Settings"** tab (near the top of the page, to the right of "Insights").

**Step 35.** In the left sidebar, click **"Secrets and variables"**, then click **"Actions"**.

**Step 36.** Click the green **"New repository secret"** button.

You need to add **7 secrets**, one at a time. For each one:
- Click **"New repository secret"**
- Type the exact secret name (copy it from the table below)
- Paste the value
- Click **"Add secret"**

| Secret name | What to paste as the value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The bot token from Step 22 (looks like `1234567890:ABCdef...`) |
| `TELEGRAM_CHAT_ID` | The chat ID number from Step 26 (looks like `987654321`) |
| `GMAIL_ADDRESS` | *(optional)* Your personal Gmail address (e.g. `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | *(optional)* The 16-character App Password from Step 32 (no spaces needed) |
| `TLS_EMAIL` | Your TLScontact account email address |
| `TLS_PASSWORD` | Your TLScontact account password |
| `TLS_ORDER_ID` | Your TLScontact order/application ID — see note below |
| `NOTIFY_EMAIL` | *(optional)* Email address to receive alerts (can be same as `GMAIL_ADDRESS`) |

After adding all 8, you should see 8 secrets listed on the page.

**Finding your TLS_ORDER_ID:**
When you log in to TLScontact and navigate to the appointment booking page, look at the URL in your browser's address bar. It will look something like:
```
https://visas-fr.tlscontact.com/workflow/appointment-booking/gbLON2fr/26382519
```
The number at the very end of the URL (e.g. `26382519`) is your order ID. Copy just that number.

---

## Part 7: Enable the Workflow

GitHub Actions workflows need to be enabled before they run automatically.

**Step 37.** Click the **"Actions"** tab near the top of your repository page.

**Step 38.** If you see a yellow banner saying "Workflows aren't being run on this forked repository" or a similar message asking to enable workflows, click the green button to enable them.

**Step 39.** In the left sidebar, you should see **"TLS Appointment Checker"** listed. Click it.

---

## Part 8: Do a Manual Test Run

Before the automatic schedule kicks in, test that everything works.

**Step 40.** On the "TLS Appointment Checker" page in Actions, click **"Run workflow"** on the right side of the page.

**Step 41.** A small dropdown will appear. Click the green **"Run workflow"** button inside it.

**Step 42.** The page will refresh. You'll see a new run appear with a spinning yellow circle (running) or a green tick (done) or a red X (failed).

**Step 43.** Click on the run to see details. Click on **"check"** to see the logs.

**What you should see if everything is working:**
- The script will say "Sleeping Xs for jitter..." (a random delay is normal)
- It will try to log in to TLScontact
- If TLScontact is currently blocking automated access (common), it will say "Blocked on landing" and send you a Telegram message saying "TLSWatch blocked"
- If it gets through, it will report whether slots are available

A "blocked" result on the first run is normal and expected — the monitoring still works and will retry every 12 minutes automatically.

**If the run shows a red X and fails completely:**
- Click the run to see the error message
- The most common issue is a secret being entered incorrectly — go back to Settings → Secrets and double-check all 7 secrets

---

## Part 9: Understand the Schedule

The monitor runs automatically at these times:

- **Weekdays:** every 12 minutes, between 6am and 10pm UK time
- **Weekends:** every 15 minutes, between 8am and 6pm UK time

### Summer time (BST) adjustment

GitHub's scheduler runs in UTC (international standard time). In winter, UK time = UTC, so no adjustment is needed. In summer (when clocks go forward in late March), UK time = UTC + 1 hour, which means the schedule will run 1 hour later than intended if you don't adjust it.

**To adjust for British Summer Time (BST):**

**Step 44.** In your repository, click on `.github` → `workflows` → `check.yml`.

**Step 45.** Click the pencil icon (Edit) in the top right of the file.

**Step 46.** Find these two lines:
```
- cron: '*/12 6-22 * * 1-5'
- cron: '*/15 8-18 * * 0,6'
```

Change them to:
```
- cron: '*/12 5-21 * * 1-5'
- cron: '*/15 7-17 * * 0,6'
```
(The hour numbers shift down by 1 to account for BST.)

**Step 47.** Click **"Commit changes"** and then **"Commit changes"** again in the popup.

Reverse this change in late October when clocks go back.

---

## Part 10: How to Know It's Working

After the first manual test, the monitor will run automatically. You don't need to do anything.

**Signs it's working normally:**
- You receive occasional Telegram messages saying "TLSWatch blocked" — this means it's running but TLScontact is blocking automated access (normal behaviour for this site)
- You can click the **Actions** tab on your repository at any time to see recent runs
- Green ticks = ran without crashing. The absence of a "SLOT AVAILABLE" message means no slots were found

**When a slot is found:**
- You'll receive an instant Telegram notification on your iPhone
- You'll also receive a backup email
- Open the link in the notification immediately — slots disappear within minutes

---

## Part 11: Make the Monitor More Reliable — Run on Your Mac *(optional but recommended)*

By default, checks run on GitHub's cloud servers. Those servers use well-known IP addresses that TLScontact's security system (Cloudflare) often blocks, causing the "TLSWatch blocked" Telegram message. This does not mean the monitor is broken — it retries automatically — but it does reduce how often a check successfully reaches the appointment page.

**The fix:** tell GitHub to run the checks on your Mac instead. Your Mac has a home internet connection with a normal residential IP address that Cloudflare does not flag. This is called a **self-hosted runner**. It is a small background app that sits quietly on your Mac and picks up jobs from GitHub whenever a check is scheduled.

**Requirement:** your Mac must be on (not shut down) for checks to run. Sleep/screen-off is fine — the runner wakes automatically when a job arrives.

---

### Step A: Register your Mac as a runner

**Step 48.** Go to your `tlswatch` repository on GitHub.

**Step 49.** Click **"Settings"** → in the left sidebar scroll down to **"Actions"** → click **"Runners"**.

**Step 50.** Click the green **"New self-hosted runner"** button.

**Step 51.** Under "Runner image", select **macOS**. Under "Architecture", select:
- **ARM64** if your Mac has an M1, M2, M3, or M4 chip (most Macs bought after 2020)
- **X64** if your Mac has an Intel chip (most Macs bought before 2020)

If you're unsure: click the Apple menu (top-left) → "About This Mac". If it says "Apple M..." it's ARM64. If it says "Intel" it's X64.

**Step 52.** GitHub will show you three groups of Terminal commands. Leave this page open — you'll need those commands in the next steps.

---

### Step B: Install the runner on your Mac

**Step 53.** Open the **Terminal** app on your Mac. You can find it by pressing Cmd+Space and typing "Terminal", then pressing Enter.

**Step 54.** Copy and run the commands from **"Download"** section on the GitHub page one at a time. They will look something like:
```
mkdir actions-runner && cd actions-runner
curl -o actions-runner-osx-arm64-2.x.x.tar.gz -L https://github.com/...
tar xzf ./actions-runner-osx-arm64-2.x.x.tar.gz
```
Paste each line into Terminal and press Enter. Wait for each to finish before pasting the next.

**Step 55.** Now run the command from the **"Configure"** section. It looks like:
```
./config.sh --url https://github.com/YOUR-USERNAME/tlswatch --token XXXXXXXXXX
```
(The token is unique to you and already filled in on the GitHub page — just copy it.)

**Step 56.** Terminal will ask you a few questions:
- **Enter the name of the runner group:** just press Enter (accepts default)
- **Enter the name for this runner:** type something like `my-mac` and press Enter
- **Enter any additional labels:** just press Enter
- **Enter name of work folder:** just press Enter

**Step 57.** Now install the runner as a background service so it starts automatically when you log in. Run these two commands:
```
./svc.sh install
./svc.sh start
```

The runner is now running in the background. You can close Terminal.

---

### Step C: Update the workflow file to use your Mac

You need to make one small edit to `check.yml` so GitHub sends jobs to your Mac instead of its own servers.

**Step 58.** In your GitHub repository, click on `.github` → `workflows` → `check.yml`.

**Step 59.** Click the pencil (Edit) icon in the top right.

**Step 60.** Find this line:
```
    runs-on: ubuntu-22.04
```

Change it to:
```
    runs-on: self-hosted
```

**Step 61.** Click **"Commit changes"**, then **"Commit changes"** again in the popup.

---

### Step D: Verify it's working

**Step 62.** Go to the **Actions** tab in your repository and click **"Run workflow"** → **"Run workflow"** to trigger a manual test.

**Step 63.** Click on the running job. You should see it say **"Running on: my-mac"** (or whatever name you chose in Step 56) instead of "ubuntu-22.04". This confirms the job is running on your Mac.

The checks should now get through Cloudflare much more reliably. You will see far fewer "TLSWatch blocked" Telegram messages.

---

### If you want to stop or uninstall the runner later

Open Terminal and run:
```
cd actions-runner
./svc.sh stop
./svc.sh uninstall
```

---

## Frequently Asked Questions

**Q: Will this actually work given Cloudflare blocks it?**
With the default setup (GitHub's servers), checks are frequently blocked because those servers use known datacenter IP addresses. You will receive "TLSWatch blocked" Telegram messages often — this is normal and the monitor retries automatically. For significantly better reliability, follow Part 11 to run the checks on your own Mac instead. Your home internet connection is not flagged by Cloudflare, so almost every check will get through.

**Q: How do I turn off the monitor?**
Go to the Actions tab, click "TLS Appointment Checker", then click the "..." menu near the top right and choose "Disable workflow". Re-enable it the same way.

**Q: I got the slot notification — what do I do?**
Click the link in the Telegram message immediately. It takes you to the TLScontact booking page. You will still need to log in and complete the booking manually.

**Q: Gmail App Passwords says "The setting you are looking for is not available for your account."**
Your account is a work, school, or organisation Google account — App Passwords are disabled by the admin. Skip email entirely: just don't add the three email secrets (`GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `NOTIFY_EMAIL`). Telegram notifications will still work perfectly.

**Q: My Gmail App Password doesn't work.**
Make sure you are using a personal Gmail account (not a work/school one), and that 2-Step Verification is enabled (Step 29). Also make sure you didn't include spaces when pasting the App Password.

**Q: The Actions run is failing with a Python error.**
Check that all 8 secrets are entered correctly (Settings → Secrets and variables → Actions). The secret names must be spelled exactly as shown in the table in Step 36.

**Q: The runner says "offline" or jobs are queued but not running.**
Your Mac may be asleep or shut down, or the runner service may have stopped. Open Terminal and run `cd actions-runner && ./svc.sh start` to restart it. To check the runner status on GitHub: Settings → Actions → Runners — it should show a green dot next to your runner name.

**Q: Can I run the monitor on my Mac without it being a self-hosted runner?**
Yes — but it requires leaving Terminal open and running `python3 checker.py` manually each time, which is not practical. The self-hosted runner approach from Part 11 is the right way to do this automatically.
