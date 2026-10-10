# Telegram for Claude Code - Home Computer Setup

Package contents:

| File | Purpose |
|---|---|
| `SETUP_HOME.md` | This checklist |
| `setup_home.sh` | One-time setup: checks prerequisites, writes the token `.env` (LF endings), copies the allowlist |
| `verify_telegram.sh` | Read-only health check (never prints the token) |
| `launch_listener.sh` | Starts the `--channels` listener |
| `access.json.template` | Allowlist for your Telegram user ID |
| `help_telegram.md` | Full guide including Lessons Learned (L1-L10) |

NOT in the package, on purpose: the bot token, work-laptop settings, hooks and CLAUDE.md.

## Before you start

1. Install Claude Code and Bun (`bun --version` must work). Bun: https://bun.sh
2. Have a **claude.ai account** (Pro/Max or similar). Channels do not work with a custom proxy or base URL.
3. Have the bot token ready from BotFather (`/mybots` -> your bot -> API Token). It is the same bot as at work.
4. Know your numeric Telegram user ID (message @userinfobot in Telegram). The setup script asks for it and writes your allowlist.
5. On Windows use Git Bash for the scripts.

## Steps

1. Unzip the package anywhere, e.g. `~/telegram_home_setup/`.
2. In a shell, make sure these are NOT set: `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`.
3. Run `bash setup_home.sh`. Paste the token when asked (input is hidden).
4. Start `claude`, run `/login`, sign in with the claude.ai account.
5. Run `/plugin install telegram@claude-plugins-official`, pick **user** scope, run `/reload-plugins`, then exit.
6. **Stop the work-laptop listener** if it is running. One bot token allows only one listener at a time.
7. Run `bash launch_listener.sh`. Leave that terminal open and do not type in it.
8. In that session run `/status`. The `Channels:` line must say active, not "Configured but not active".
9. DM your bot on Telegram. The message should appear in the listener terminal and Claude should reply.

## If it fails

| Symptom | Check |
|---|---|
| `CONNECTION_CLOSED` in `/mcp` | `bash verify_telegram.sh` - usually CRLF in `.env` (fix: `sed -i 's/\r$//' ~/.claude/channels/telegram/.env`) |
| "typing..." then nothing | `/status` Channels line; env vars from step 2; are you logged in with claude.ai? |
| No reply at all from the bot | Listener terminal closed. Re-run `launch_listener.sh` |
| `409 Conflict` | Another listener is using the token (work laptop?). Stop it |
| Your DMs ignored | Your numeric ID must be in `~/.claude/channels/telegram/access.json` `allowFrom` |

See `help_telegram.md` Lessons Learned for the reasoning behind each item.
