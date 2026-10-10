#!/usr/bin/env bash
# One-time Telegram channel setup for Claude Code (home computer).
# Run in Git Bash (Windows) or any bash (Linux/macOS):  bash setup_home.sh
# The bot token is typed at the prompt. It is never stored in this package.

set -u

STATE_DIR="${TELEGRAM_STATE_DIR:-$HOME/.claude/channels/telegram}"
ENV_FILE="$STATE_DIR/.env"
ACCESS_FILE="$STATE_DIR/access.json"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Telegram channel setup (home) ==="

echo "[1/5] Checking prerequisites"
if ! command -v bun >/dev/null 2>&1; then
  echo "  FAIL: bun not found. Install from https://bun.sh then re-run."
  exit 1
fi
echo "  bun $(bun --version)"
if ! command -v claude >/dev/null 2>&1; then
  echo "  FAIL: claude not found. Install Claude Code first, then re-run."
  exit 1
fi
echo "  claude found"

echo "[2/5] Checking environment (channels need a claude.ai login)"
for v in ANTHROPIC_API_KEY ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_MODEL; do
  if [ -n "${!v:-}" ]; then
    echo "  WARNING: $v is set in this shell. It can override the claude.ai login"
    echo "           and leave channels 'configured but not active'. Unset it:  unset $v"
  fi
done

echo "[3/5] Writing the bot token"
mkdir -p "$STATE_DIR/approved"
if [ -f "$ENV_FILE" ]; then
  printf "  %s already exists. Overwrite? [y/N] " "$ENV_FILE"
  read -r ans
  case "$ans" in y|Y) ;; *) echo "  keeping existing .env"; SKIP_TOKEN=1 ;; esac
fi
if [ "${SKIP_TOKEN:-0}" != "1" ]; then
  printf "  Paste bot token (input hidden): "
  read -r -s TOKEN
  echo
  TOKEN="$(printf '%s' "$TOKEN" | tr -d '\r\n[:space:]')"
  if ! printf '%s' "$TOKEN" | grep -Eq '^[0-9]+:[A-Za-z0-9_-]+$'; then
    echo "  FAIL: that does not look like a BotFather token (digits:letters)."
    exit 1
  fi
  printf 'TELEGRAM_BOT_TOKEN=%s\n' "$TOKEN" > "$ENV_FILE"
  chmod 600 "$ENV_FILE" 2>/dev/null || true
  unset TOKEN
  echo "  .env written with LF line endings"
fi

echo "[4/5] Access list"
if [ -f "$ACCESS_FILE" ]; then
  echo "  $ACCESS_FILE exists, leaving it alone"
else
  printf "  Your numeric Telegram user ID (get it from @userinfobot): "
  read -r TG_ID
  TG_ID="$(printf '%s' "$TG_ID" | tr -d '\r\n[:space:]')"
  if ! printf '%s' "$TG_ID" | grep -Eq '^[0-9]+$'; then
    echo "  FAIL: the user ID must be digits only (not your @username)."
    exit 1
  fi
  sed "s/<YOUR_TELEGRAM_USER_ID>/$TG_ID/" "$HERE/access.json.template" > "$ACCESS_FILE"
  echo "  access.json written with allowlist for ID $TG_ID"
fi

echo "[5/5] Verifying"
bash "$HERE/verify_telegram.sh"

cat <<'EOF'

=== Manual steps still needed (inside Claude Code) ===
 1. Run:  claude        then:  /login   (sign in with your claude.ai account)
 2. Run:  /plugin install telegram@claude-plugins-official
    Choose USER scope. Then:  /reload-plugins   and exit.
 3. Stop the work-laptop listener first if it uses the same bot (one poller per token).
 4. Start the listener:  bash launch_listener.sh
 5. In that session run /status and confirm the Channels line says active.
 6. DM your bot on Telegram. The message should appear in the listener terminal.
EOF
