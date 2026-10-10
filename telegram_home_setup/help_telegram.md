# Telegram Setup for Claude Code — Full Beginner Guide

## What You Need Before Starting

- **Claude Code** installed and working (the CLI tool)
- **Telegram** account and app (phone or desktop)
- A bot token from BotFather (Step 1 below)
- **Two terminal windows** open side by side — this is critical

---

## The Two Terminals — Keep These Straight

| | Terminal A | Terminal B |
|---|---|---|
| **Purpose** | Listens for Telegram messages | Your normal Claude Code session |
| **What runs in it** | `claude --channels ...` | Regular `claude` or nothing |
| **Leave it open?** | YES — always running | Use normally |

---

## Step 1 — Get a Bot Token (BotFather)

**Who:** You, in the Telegram app
**Where:** Telegram app -> search `@BotFather`

1. Open Telegram (phone or web.telegram.org)
2. Search for `@BotFather` in the search bar — it has a blue checkmark
3. Start a chat with BotFather
4. Send: `/newbot`
5. BotFather asks for a name — type any name e.g. `My Claude Bot`
6. BotFather asks for a username — must end in `bot` e.g. `myclaudetest_bot`
7. BotFather replies with a token that looks like: `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
8. **Copy that token — you'll need it in the next step**

---

## Step 2 — Configure the Token in Claude Code

**Who:** You
**Where:** Terminal B (your normal Claude Code session)

In Terminal B, run:
```
/telegram:configure <paste-your-token-here>
```

Example:
```
/telegram:configure 7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Claude Code confirms it saved the token. Done.

---

## Step 3 — Start the Telegram Listener

**Who:** You
**Where:** Terminal A (a NEW terminal window — open one now)

Open a brand new terminal window. In it, run:
```bash
claude --channels plugin:telegram@claude-plugins-official
# or 
claude --channels plugin:telegram@claude-plugins-official --settings "{\"disableAllHooks\": true}"
# or 
set CLAUDE_NO_PERSONALITY=1 && claude --channels plugin:telegram@claude-plugins-official
```

**What happens:** This terminal starts up and just sits there waiting. That is correct. It will say something like "Channels connected" or similar. **Do not close this terminal. Do not type anything in it. Leave it running.**

---

## Step 4 — Get the Pairing Code

**Who:** You (in Telegram app) -> Bot replies automatically
**Where:** Telegram app

1. In the Telegram app, search for your bot by its username (e.g. `@myclaudetest_bot`)
2. Open a chat with your bot
3. Send any message — just type `hi` and send

**What happens:** The bot (powered by Terminal A) automatically replies with a pairing code like:
```
Your pairing code is: ABC123
```

**If the bot does NOT reply:** Terminal A is not running — go back to Step 3.

---

## Step 5 — Approve the Pairing Code

**Who:** You
**Where:** Terminal B (your normal Claude session)

Copy the pairing code from Telegram. In Terminal B, run:
```
/telegram:access pair ABC123
```

(Replace `ABC123` with your actual code.)

Claude Code confirms the pairing is approved.

> **Note:** A file is temporarily written to `~/.claude/channels/telegram/approved/` — the channel server reads it, sends you the "you're in" confirmation in Telegram, then deletes it automatically. This is normal.

---

## Step 6 — Lock Down Access (Recommended)

**Who:** You
**Where:** Terminal B

Run:
```
/telegram:access policy allowlist
```

This means **only your Telegram account** can send messages to Claude through the bot. Keeps randos out.

---

## Step 7 — Test It

**Who:** You (in Telegram) -> Claude replies
**Where:** Telegram app, with Terminal A still running

Send a message to your bot from Telegram. Claude should respond.

---

## Quick Checklist When Something Breaks

| Symptom | Fix |
|---|---|
| Bot doesn't reply to `hi` | Terminal A is not running — open it and run the `--channels` command |
| Pairing code command fails | Make sure you're in Terminal B, not Terminal A |
| Bot replies but then stops | Terminal A got closed — reopen it |
| `/mcp` in Terminal A says `CONNECTION_CLOSED` | Server exited at startup. Run it by hand to see why (see Lessons Learned, L3). Most common: `.env` has CRLF line endings (L2) |
| "typing..." shows in Telegram, nothing in Terminal A | Server is fine; Claude Code is not accepting channel events. Run `/status` in Terminal A and read the `Channels:` line (L6) |
| `/status` says `Channels: Configured but not active` | Auth/policy problem: channels need a claude.ai login or direct Console API key. A custom `ANTHROPIC_BASE_URL` (corporate proxy) blocks it (L6) |
| Bot never answers, no `bun.exe` running | Listener session is closed. Restart it; messages sent meanwhile are lost (L8) |
| Log shows `409 Conflict` | A second listener is polling the same token (other machine or stale process). Stop it (L7) |

---

## Revoking and Replacing Your Bot Token

Do this when: your token was leaked or shared accidentally, the bot is behaving strangely, or you want a clean reset.

---

### Who Does What

| | Who | Device |
|---|---|---|
| Revoke old token | You (via BotFather) | Phone or web.telegram.org |
| Get new token | BotFather replies automatically | Phone or web.telegram.org |
| Configure new token in Claude Code | You | Terminal B |
| Restart the listener | You | Terminal A |

---

### Step 1 — Revoke the Old Token (BotFather)

**Who:** You  
**Where:** Telegram app on your phone (or web.telegram.org)

1. Open Telegram and search for `@BotFather`
2. Send: `/mybots`
3. BotFather lists your bots — tap your bot's name
4. Tap **API Token**
5. Tap **Revoke current token**
6. BotFather confirms the old token is now invalid — any session using the old token will stop working immediately

> **Note:** Your bot still exists. Only the token is replaced. Your bot username and chat history are unaffected.

---

### Step 2 — Copy the New Token (BotFather)

**Who:** You  
**Where:** Telegram app (same BotFather chat, immediately after Step 1)

BotFather automatically sends the new token in the same message as the revocation confirmation. It looks like:

```
7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Copy it now — you will need it in the next step.

---

### Step 3 — Stop Terminal A

**Who:** You  
**Where:** Terminal A (the channels listener)

Press `Ctrl+C` in Terminal A to stop the running `--channels` session. The old token is now invalid so it would fail anyway.

---

### Step 4 — Configure the New Token in Claude Code

**Who:** You  
**Where:** Terminal B (your normal Claude Code session)

Run:
```
/telegram:configure <paste-new-token-here>
```

Claude Code confirms the new token is saved.

---

### Step 5 — Restart the Listener

**Who:** You  
**Where:** Terminal A

Run the channels command again:
```bash
claude --channels plugin:telegram@claude-plugins-official
```

Terminal A is now listening with the new token. Test by sending a message from your phone — the bot should reply normally.

---

### Step 6 — Re-pair if Needed

**Who:** You  
**Where:** Phone (Telegram) + Terminal B

If your Telegram account loses access after the token change, re-pair:

1. Send any message to your bot from your phone — it will reply with a new pairing code
2. In Terminal B, run: `/telegram:access pair <new-code>`
3. Done — you are back on the allowlist

---

## Lessons Learned (Work Laptop Debugging, 2026-10-10)

Telegram never delivered a message on a corporate work laptop. Root causes were found in two layers: a fixable file-format bug, then a blocker that is not fixable on that machine.

### L1 — `ls` hides dotfiles: use `ls -a`

The token file is `~/.claude/channels/telegram/.env`. A plain `ls` does not show it, which led to a wrong "token is missing" diagnosis. Always use `ls -a`, or check by path directly.

### L2 — CRLF line endings in `.env` silently break the token

The server reads `.env` with the pattern `/^(\w+)=(.*)$/` after splitting on `\n`. If the line ends with a Windows carriage return, the pattern does not match, the token is never loaded, and the server exits with `TELEGRAM_BOT_TOKEN required`. Claude Code only shows this as `CONNECTION_CLOSED`.

- Cause: a Windows editor, or a paste through a Windows tool, saved the file with CRLF.
- Fix: `sed -i 's/\r$//' ~/.claude/channels/telegram/.env`
- Prevention: on Windows, write the file with the `setup_home.sh` script in `telegram_home_setup/` (it writes LF), not with Notepad.

### L3 — Diagnose a dead server by running it by hand

`CONNECTION_CLOSED` hides the real error. The plugin launches the server with the command below; run it yourself and the error prints:

```bash
cd ~/.claude/plugins/cache/claude-plugins-official/telegram/<version>
timeout 15 bun run --cwd . --shell=bun --silent start < /dev/null
```

Look for lines beginning `telegram channel:`.

### L4 — Check whether the server is alive

- `~/.claude/channels/telegram/bot.pid` holds the poller PID. If the file exists but the PID is not running, it is stale.
- Windows: `tasklist //FI "IMAGENAME eq bun.exe"` (two bun.exe processes = launcher + server). No bun.exe = no listener.
- Running = `bot.pid` present AND bun.exe present.

### L5 — "typing..." in Telegram proves the server got your message

The server sends the typing indicator only after the message passes the allowlist gate, immediately before it hands the message to Claude Code. So if you see "typing..." and nothing in Terminal A, the Telegram side and the token are fine. The failure is inside Claude Code (L6).

### L6 — `/status` is the decisive check: read the `Channels:` line

Run `/status` in Terminal A. Healthy output mentions the channel as active. The failing output was:

```
Channels: Configured but not active (not currently available): plugin:telegram@claude-plugins-official
```

Meaning: Claude Code receives the events and discards them. Per the Claude Code channels docs, channels need Anthropic authentication through claude.ai or a Console API key, and are not available on Bedrock, Vertex or Foundry. Team and Enterprise orgs must also enable them.

On the work laptop `/status` showed `Auth token: none`, `API key: ANTHROPIC_API_KEY`, a custom `ANTHROPIC_BASE_URL` (corporate proxy) and `Organization policy: not fetched with a custom ANTHROPIC_BASE_URL`. The likely (inferred, not documented) cause is that the proxy stops Claude Code from confirming channels are allowed. Treat channels as unavailable on a proxied setup.

### L7 — One poller per bot token

Telegram allows exactly one `getUpdates` consumer per token. A second listener (another machine, or a zombie process) causes `409 Conflict`. The server kills a stale poller on startup using `bot.pid`, but it cannot see a poller on another computer. Using the same bot on two machines means only one may listen at a time. A second bot per machine avoids this.

### L8 — The listener must stay open; messages are not replayed

Channel events only arrive while the `--channels` session is open. Anything sent while it was closed is lost. For always-on use, keep the session in a persistent terminal.

### L9 — Other facts worth remembering

- Bun is required (`bun --version` to check). Install: https://bun.sh
- The `--channels` flag is hidden from `claude --help` but works.
- `dmPolicy: allowlist` silently drops every sender not in `allowFrom`. No error, no reply. Your numeric Telegram user ID (not username) must be listed.
- `/telegram:configure` only writes the `.env`. If the `.env` already exists, running it again changes nothing useful.
- Being in `.mcp.json` is not enough; the plugin must be named in `--channels`.
- Do not `cat` the `.env` or paste the token into a chat. To verify the token without printing it, count a format match: Grep for `^TELEGRAM_BOT_TOKEN=\d+:[A-Za-z0-9_-]+$` with count output.
- Plugin install location: `~/.claude/plugins/cache/claude-plugins-official/telegram/<version>/`
- State directory: `~/.claude/channels/telegram/` (`.env`, `access.json`, `approved/`, `bot.pid`).

### L10 — Home computer setup

Use the `telegram_home_setup/` package. Key rules:

1. Log in with a claude.ai account (`/login`). Do not set `ANTHROPIC_API_KEY` or `ANTHROPIC_BASE_URL`; environment variables override the login and disable channels.
2. Do not copy work-laptop `CLAUDE.md`, `settings.json`, hooks or the `.env` token across.
3. Type the bot token on the home machine yourself. It is never packaged.
4. Same bot as work: stop the work-laptop listener (Terminal A) before starting the home one (L7).
5. After starting, run `/status` and confirm the Channels line is active before testing.
