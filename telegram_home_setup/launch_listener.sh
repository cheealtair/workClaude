#!/usr/bin/env bash
# Start the Telegram listener. Leave this terminal open and do not type in it.

for v in ANTHROPIC_API_KEY ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN; do
  if [ -n "${!v:-}" ]; then
    echo "WARNING: $v is set. It can override the claude.ai login and disable channels."
    echo "Unset it first (unset $v) and re-run. Continuing in 5 seconds, Ctrl+C to abort."
    sleep 5
  fi
done

bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/verify_telegram.sh" || {
  echo "Fix the problems above before launching."
  exit 1
}

echo "Starting listener. Once up, run /status and check the Channels line."
exec claude --channels plugin:telegram@claude-plugins-official
