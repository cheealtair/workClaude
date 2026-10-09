"""
Prompt Gatekeeper - Installer
=====================================================================
Installs the gatekeeper.py + state_monitor.py hooks into a Claude Code
setup on any machine (Windows, Mac, Linux).

Usage:
    python install_gatekeeper.py

Run from the gatekeeper_package/ directory. The installer expects
gatekeeper.py and state_monitor.py to be in the same directory.

What it does:
  1. Locates ~/.claude/
  2. Creates ~/.claude/hooks/
  3. Copies gatekeeper.py and state_monitor.py into hooks/
  4. Writes task_state.json (clean) if it does not already exist
  5. Merges hook blocks into settings.json (safe - does not overwrite)
  6. Appends Task State Convention to CLAUDE.md if not already present
  7. py_compile both scripts
  8. Prints smoke test commands

Re-running is safe (idempotent).
=====================================================================
"""

import sys
import os
import json
import shutil
import pathlib
import subprocess
import platform

HERE = pathlib.Path(__file__).parent.resolve()

# -------------------------------------------------------
# CLAUDE.MD SECTION TO INJECT
# -------------------------------------------------------
CLAUDE_MD_SECTION = """
## Task State Convention (Gatekeeper Hooks)

Two global hooks (`gatekeeper.py` on UserPromptSubmit, `state_monitor.py` on Stop) read
`~/.claude/hooks/task_state.json` and nothing else. Keep it accurate
BEFORE ending a turn; the user sees it immediately after.

- **START of a substantial task** (code, TTL, SPARQL, multi-section docs, scripts, build
  phases): write `{"status": "in_progress", "task": "<short name>", "detail": "<optional>",
  "project": "<e.g. MyProject>", "cwd": "<working dir>", "updated": "<ISO local time>"}`.
- **END of a task** (complete, handed off, or paused): write `"status": "clean"` with all
  other fields empty strings.
- Trivial follow-ups (a question, a one-line edit) need no update.

**[check] mode:** if a prompt begins with `[check]`, do NOT execute it or call tools.
Reply with a short assessment (what it involves, size, recommended model and effort,
whether the state allows switching) ending "Switch with /model if needed, then type go."
On "go", execute the checked prompt.

**PRIME DIRECTIVE (all projects):** these hooks, and any hook written for this user, must
never run git or spawn processes (no subprocess, os.system, os.popen, pty,
multiprocessing). After any hook edit run `python -m py_compile` on it.

Rationale, scope, decisions and full source: see prompt_gatekeeper_model_switcher.md
"""

CLAUDE_MD_MARKER = "## Task State Convention (Gatekeeper Hooks)"

# -------------------------------------------------------
# TASK_STATE.JSON INITIAL CONTENT
# -------------------------------------------------------
TASK_STATE_CLEAN = {
    "status": "clean",
    "task": "",
    "detail": "",
    "project": "",
    "cwd": "",
    "updated": "2026-01-01T00:00:00"
}

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def banner(text):
    print()
    print("=" * 60)
    print("  " + text)
    print("=" * 60)

def ok(msg):
    print("  [OK]   " + msg)

def skip(msg):
    print("  [SKIP] " + msg)

def info(msg):
    print("  [INFO] " + msg)

def fail(msg):
    print("  [FAIL] " + msg)

def find_claude_dir():
    return pathlib.Path.home() / ".claude"

def python_path():
    return sys.executable

def posix_path(p):
    """Convert a path to POSIX style for use in settings.json hook commands."""
    p = pathlib.Path(p)
    if platform.system() == "Windows":
        drive = p.drive.rstrip(":").lower()
        rest = str(p.relative_to(p.anchor)).replace("\\", "/")
        return "/" + drive + "/" + rest
    return str(p)

# -------------------------------------------------------
# STEPS
# -------------------------------------------------------

def step_check_sources():
    """Confirm hook source files are present."""
    missing = []
    for name in ("gatekeeper.py", "state_monitor.py"):
        if not (HERE / name).exists():
            missing.append(name)
    if missing:
        fail("Missing source files: " + ", ".join(missing))
        fail("Run the installer from inside gatekeeper_package/")
        sys.exit(1)
    ok("Source files found: gatekeeper.py, state_monitor.py")


def step_create_hooks_dir(hooks_dir):
    hooks_dir.mkdir(parents=True, exist_ok=True)
    ok("Hooks directory ready: " + str(hooks_dir))


def step_copy_scripts(hooks_dir):
    for name in ("gatekeeper.py", "state_monitor.py"):
        src = HERE / name
        dst = hooks_dir / name
        shutil.copy2(src, dst)
        ok("Copied " + name + " -> " + str(dst))


def step_write_task_state(hooks_dir):
    ts = hooks_dir / "task_state.json"
    if ts.exists():
        skip("task_state.json already exists -- not overwritten")
    else:
        ts.write_text(json.dumps(TASK_STATE_CLEAN, indent=2), encoding="utf-8")
        ok("Created task_state.json (clean)")


def step_patch_settings(claude_dir, hooks_dir):
    settings_path = claude_dir / "settings.json"
    if not settings_path.exists():
        info("settings.json not found -- creating minimal one")
        settings = {}
    else:
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception as e:
            fail("Could not parse settings.json: " + str(e))
            fail("Fix settings.json manually and re-run.")
            sys.exit(1)

    py = posix_path(python_path())
    gk = posix_path(hooks_dir / "gatekeeper.py")
    sm = posix_path(hooks_dir / "state_monitor.py")

    gk_command = py + " " + gk
    sm_command = py + " " + sm

    hooks = settings.setdefault("hooks", {})

    # --- UserPromptSubmit ---
    ups_list = hooks.setdefault("UserPromptSubmit", [])
    already_gk = any(
        any(h.get("command", "").endswith("gatekeeper.py") for h in entry.get("hooks", []))
        for entry in ups_list
    )
    if already_gk:
        skip("gatekeeper.py already registered in UserPromptSubmit")
    else:
        ups_list.append({
            "hooks": [
                {
                    "type": "command",
                    "command": gk_command,
                    "statusMessage": "Gatekeeper assessing prompt..."
                }
            ]
        })
        ok("Registered gatekeeper.py in UserPromptSubmit")

    # --- Stop ---
    stop_list = hooks.setdefault("Stop", [])
    already_sm = any(
        any(h.get("command", "").endswith("state_monitor.py") for h in entry.get("hooks", []))
        for entry in stop_list
    )
    if already_sm:
        skip("state_monitor.py already registered in Stop")
    else:
        stop_list.append({
            "hooks": [
                {
                    "type": "command",
                    "command": sm_command,
                    "timeout": 5
                }
            ]
        })
        ok("Registered state_monitor.py in Stop")

    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    ok("settings.json saved")


def step_patch_claude_md(claude_dir):
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.exists():
        claude_md.write_text(CLAUDE_MD_SECTION.lstrip(), encoding="utf-8")
        ok("Created CLAUDE.md with Task State Convention section")
        return

    content = claude_md.read_text(encoding="utf-8")
    if CLAUDE_MD_MARKER in content:
        skip("Task State Convention already present in CLAUDE.md")
    else:
        with claude_md.open("a", encoding="utf-8") as f:
            f.write("\n" + CLAUDE_MD_SECTION)
        ok("Appended Task State Convention to CLAUDE.md")


def step_compile(hooks_dir):
    py = python_path()
    gk = str(hooks_dir / "gatekeeper.py")
    sm = str(hooks_dir / "state_monitor.py")
    result = subprocess.run(
        [py, "-m", "py_compile", gk, sm],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        ok("Both scripts compile cleanly")
    else:
        fail("py_compile failed:")
        print(result.stderr)
        fail("Fix the syntax error before using the hooks.")


def step_smoke_test_hint(hooks_dir):
    py = posix_path(python_path())
    gk = posix_path(hooks_dir / "gatekeeper.py")
    sm = posix_path(hooks_dir / "state_monitor.py")
    print()
    print("  Smoke tests (run in bash / Git Bash):")
    print()
    print('  printf \'{"user_prompt":"review all the ttl files"}\' | ' + py + " " + gk)
    print("  -- expect: JSON with Opus 5.5 recommendation, effort high")
    print()
    print("  printf '{}' | " + py + " " + sm)
    print("  -- expect: JSON with STATE [CLEAN] line")
    print()

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    banner("Prompt Gatekeeper Installer")
    print("  Platform : " + platform.system())
    print("  Python   : " + python_path())

    claude_dir = find_claude_dir()
    hooks_dir  = claude_dir / "hooks"
    print("  Claude   : " + str(claude_dir))
    print("  Hooks    : " + str(hooks_dir))

    banner("Step 1 -- Check source files")
    step_check_sources()

    banner("Step 2 -- Create hooks directory")
    step_create_hooks_dir(hooks_dir)

    banner("Step 3 -- Copy hook scripts")
    step_copy_scripts(hooks_dir)

    banner("Step 4 -- Write task_state.json")
    step_write_task_state(hooks_dir)

    banner("Step 5 -- Patch settings.json")
    step_patch_settings(claude_dir, hooks_dir)

    banner("Step 6 -- Patch CLAUDE.md")
    step_patch_claude_md(claude_dir)

    banner("Step 7 -- Compile scripts")
    step_compile(hooks_dir)

    banner("Step 8 -- Smoke test commands")
    step_smoke_test_hint(hooks_dir)

    banner("Done -- Gatekeeper installed")
    print("  Restart Claude Code (or open a new session) to activate the hooks.")
    print()


if __name__ == "__main__":
    main()
