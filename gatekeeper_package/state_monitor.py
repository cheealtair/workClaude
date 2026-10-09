"""
State Monitor -- Stop hook for Claude Code.

=====================================================================
PRIME DIRECTIVE (shared with gatekeeper.py)
  This hook NEVER runs git -- not directly, not indirectly.
  It spawns no processes. Its only inputs are the JSON on stdin and
  one file, task_state.json. Its only output is JSON on stdout.
=====================================================================

Fires every time Claude finishes a turn and hands control back to the
user. Reads task_state.json and shows the CURRENT state so the user
knows, before typing the next prompt, whether the deck is clear.

This is the "state" half of the gatekeeper, split out from the
UserPromptSubmit hook so the information arrives BEFORE the next
prompt rather than after it.

Output: one JSON object with a systemMessage (shown to the user).
Never blocks. Always exits 0.

To DISABLE : set ENABLED = False below.
"""

import sys
import json
import os
from datetime import datetime

TASK_STATE_FILE = os.path.join(
    os.path.expanduser("~"), ".claude", "hooks", "task_state.json"
)

ENABLED = True

if not ENABLED:
    sys.exit(0)

STALE_HOURS = 24

FORBIDDEN_MODULES = ("subprocess", "pty", "multiprocessing")


def check_prime_directive():
    loaded = [m for m in FORBIDDEN_MODULES if m in sys.modules]
    if loaded:
        return "PRIME DIRECTIVE VIOLATION: process-spawning module(s) loaded: " + ", ".join(loaded)
    return ""


def read_task_state():
    try:
        with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, ""
    except FileNotFoundError:
        return {}, "task_state.json missing"
    except Exception as exc:
        return {}, f"task_state.json unreadable ({type(exc).__name__})"


def age_text(updated_str):
    """
    Return (hours_float or None, human text).
    Age is taken from the file's modification time, which is the true moment
    of the last write. The 'updated' field is written by Claude, which does
    not know the wall clock, so it is only used as a fallback.
    """
    try:
        try:
            updated = datetime.fromtimestamp(os.path.getmtime(TASK_STATE_FILE)).astimezone()
        except OSError:
            updated = datetime.fromisoformat(updated_str)
            if updated.tzinfo is None:
                updated = updated.astimezone()
        secs = (datetime.now().astimezone() - updated).total_seconds()
        hours = secs / 3600
        if secs < 0:
            return hours, "timestamp in the future"
        if secs < 90:
            return hours, "just now"
        if secs < 3600:
            return hours, f"{int(secs // 60)}m ago"
        if hours < 48:
            return hours, f"{int(hours)}h ago"
        return hours, f"{int(hours // 24)}d ago"
    except Exception:
        return None, "no valid timestamp"


def main():
    # Drain stdin so the caller never sees a broken pipe; content unused.
    try:
        sys.stdin.read()
    except Exception:
        pass

    data, problem = read_task_state()
    status  = data.get("status", "")
    task    = data.get("task", "")
    detail  = data.get("detail", "")
    project = data.get("project", "")
    updated = data.get("updated", "")
    # Age comes from file mtime, so it is computed even if 'updated' is empty.
    hours, when = age_text(updated)

    lines = []
    if problem:
        lines.append(f"STATE  [UNKNOWN]  {problem} -- assuming clean")
    elif status == "in_progress":
        tag = f" [{project}]" if project else ""
        head = f"STATE  [DIRTY]  task in progress: '{task}'{tag}  (updated {when})"
        lines.append(head)
        if detail:
            lines.append(f"       {detail}")
        if hours is not None and hours > STALE_HOURS:
            lines.append(
                f"       ! flagged in_progress for {int(hours)}h -- may be stale. "
                "If the task is done, ask Claude to reset task_state.json."
            )
        lines.append("       ! Hold off switching model/effort until this task is complete")
    elif status == "clean":
        lines.append(f"STATE  [CLEAN]  safe to switch model or effort  (updated {when})")
    elif status == "":
        lines.append("STATE  [UNKNOWN]  task_state.json has no status field -- assuming clean")
    else:
        # Same handling as gatekeeper.py: report the breach, assume clean.
        lines.append(
            f"STATE  [UNKNOWN]  status='{status}' -- expected clean or in_progress -- assuming clean"
        )

    violation = check_prime_directive()
    if violation:
        lines.append(f"       !!! {violation}")

    out = {"systemMessage": "\n".join(lines)}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
