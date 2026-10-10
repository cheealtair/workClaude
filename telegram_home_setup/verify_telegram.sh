#!/usr/bin/env bash
# Read-only health check for the Telegram channel. Never prints the token.

STATE_DIR="${TELEGRAM_STATE_DIR:-$HOME/.claude/channels/telegram}"
ENV_FILE="$STATE_DIR/.env"
ok=1

echo "State dir contents (ls -a):"
ls -a "$STATE_DIR" 2>/dev/null || { echo "  MISSING: $STATE_DIR"; ok=0; }

if [ -f "$ENV_FILE" ]; then
  if grep -q $'\r' "$ENV_FILE"; then
    echo "FAIL .env contains CR (CRLF) line endings - fix: sed -i 's/\\r\$//' \"$ENV_FILE\""
    ok=0
  else
    echo "ok   .env has no CR characters"
  fi
  if grep -Eq '^TELEGRAM_BOT_TOKEN=[0-9]+:[A-Za-z0-9_-]+$' "$ENV_FILE"; then
    echo "ok   .env token line has the expected format"
  else
    echo "FAIL .env missing a valid TELEGRAM_BOT_TOKEN=digits:letters line"
    ok=0
  fi
else
  echo "FAIL no .env at $ENV_FILE"
  ok=0
fi

if [ -f "$STATE_DIR/access.json" ]; then
  echo "ok   access.json present"
else
  echo "FAIL no access.json"
  ok=0
fi

for v in ANTHROPIC_API_KEY ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN; do
  [ -n "${!v:-}" ] && echo "warn $v is set in this shell (can disable channels)"
done

if [ -f "$STATE_DIR/bot.pid" ]; then
  pid="$(tr -d '\r\n' < "$STATE_DIR/bot.pid")"
  if command -v tasklist >/dev/null 2>&1; then
    if tasklist //FI "PID eq $pid" 2>/dev/null | grep -q "$pid"; then
      echo "ok   listener running (pid $pid)"
    else
      echo "info bot.pid is stale (pid $pid not running) - listener is not up"
    fi
  elif kill -0 "$pid" 2>/dev/null; then
    echo "ok   listener running (pid $pid)"
  else
    echo "info bot.pid is stale (pid $pid not running) - listener is not up"
  fi
else
  echo "info no bot.pid - listener is not running"
fi

[ "$ok" = "1" ] && echo "RESULT: config looks good" || { echo "RESULT: problems found"; exit 1; }
