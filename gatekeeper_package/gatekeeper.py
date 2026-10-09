"""
Gatekeeper -- UserPromptSubmit hook for Claude Code.

=====================================================================
PRIME DIRECTIVE
  This hook NEVER runs git -- not directly, not indirectly.
  It spawns no processes of any kind: no subprocess, no os.system,
  no os.popen, no shelling out. Its only inputs are the JSON on stdin
  and one file, task_state.json. Its only output is JSON on stdout.
  A runtime self-check (check_prime_directive) confirms that no
  process-spawning module has been imported, and reports a violation
  in the user-visible message if it ever finds one.
=====================================================================

Fires on every prompt submission. Assesses clean state from
task_state.json and recommends a model and effort level based on the
prompt text.

To ENABLE  : set ENABLED = True below.
To DISABLE : set ENABLED = False below.

When disabled the script exits silently as soon as it is imported past
the switch -- no output, no context injection.

Output channels (per Claude Code hook docs):
  - systemMessage         -> shown to the USER in the terminal
  - additionalContext     -> injected into CLAUDE's context
  stderr is NOT shown to the user on exit 0, so it is not used here.

Model cost reference (as recorded Sep 2026, unverified -- check the
current price list before relying on the figures):
  Fable 5.1  : most expensive tier  -- long-horizon agentic tasks only
  Opus 5.5   : $4  / $20 per MTok   -- complex reasoning, coding, TTL work
  Sonnet 5   : $2  / $10 per MTok   -- edits, explanations, medium tasks
  Haiku 4.5  : $1  / $5  per MTok   -- quick confirmations, one-liners

Note on the Sonnet label: settings.json maps the "sonnet" alias
(ANTHROPIC_DEFAULT_SONNET_MODEL) to claude-sonnet-4-6@default. The
recommendation below says "Sonnet 5". If /model Sonnet 5 does not
resolve through the proxy, either update that env var or change
DEFAULT_MODEL_LABEL / the Sonnet rule label here.
"""

import sys
import json
import os
import re
from datetime import datetime

TASK_STATE_FILE = os.path.join(
    os.path.expanduser("~"), ".claude", "hooks", "task_state.json"
)

# -------------------------------------------------------
# MASTER SWITCH -- flip to False to deactivate
# -------------------------------------------------------
ENABLED = True
# -------------------------------------------------------

if not ENABLED:
    sys.exit(0)


# -------------------------------------------------------
# MODEL SELECTION RULES
# Evaluated top-to-bottom; first match wins.
# Keywords match on WORD BOUNDARIES: "ttl" matches "ttl" and
# "ttl-file" but not "settle"; "no" does not match "know".
# Fable is intentionally last and has a very high bar --
# it is the most expensive tier and is only justified for
# truly long-horizon, multi-step autonomous tasks.
# -------------------------------------------------------

MODEL_RULES = [
    (
        "Opus 5.5", "claude-opus-5-5",
        "complex reasoning, TTL/SPARQL authoring, ontology work, deep reviews",
        [
            "ttl", "turtle", "sparql", "owl", "ontology", "rdf",
            "implement", "build the", "write the", "generate",
            "create a script", "review all", "self-review", "full review",
            "architecture", "master plan", "masterplan",
            "phase p1", "phase p2", "phase p3",
            "validate", "anzo", "graphmart",
        ],
    ),
    (
        "Sonnet 5", "claude-sonnet-5",
        "edits, explanations, updates, medium-complexity tasks",
        [
            "explain", "summarise", "summarize", "update", "edit",
            "add a line", "what is", "how does", "can you check",
            "what does", "describe", "clarify", "in short",
            "quick", "brief",
        ],
    ),
    (
        "Haiku 4.5", "claude-haiku-4-5-20251001",
        "one-liners, confirmations, trivial follow-ups",
        [
            "yes", "no", "ok", "okay", "thanks", "great",
            "go ahead", "proceed", "continue", "sounds good",
            "make it so", "done",
        ],
    ),
    (
        "Fable 5.1", "claude-fable-5-1",
        "long-horizon multi-step autonomous tasks only -- most expensive tier",
        [
            "full build", "end to end", "end-to-end",
            "all phases", "entire p1", "entire build",
            "autonomous", "multi-step workflow",
            "run the whole", "build and validate and upload",
            "run everything", "do the whole",
        ],
    ),
]

DEFAULT_MODEL_LABEL = "Sonnet 5"
DEFAULT_MODEL_ID    = "claude-sonnet-5"
DEFAULT_MODEL_PURPOSE = "edits, explanations, updates, medium-complexity tasks"

# Haiku is only recommended for genuinely short prompts. A long prompt
# that happens to contain "ok" or "yes" is not a confirmation.
HAIKU_MAX_WORDS = 8

EFFORT_HIGH_KEYWORDS = [
    "review all", "self-review", "full review", "check everything",
    "audit", "validate all", "integrity check", "deep review",
]
EFFORT_LOW_KEYWORDS = [
    "quick", "briefly", "one line", "just check", "in short",
]

FABLE_WARNING = (
    "NOTE: Fable 5.1 is the most expensive tier. "
    "Only use it if this is truly a long-horizon autonomous task "
    "that Opus at high effort cannot handle."
)

STALE_HOURS = 24  # warn if in_progress for longer than this

# -------------------------------------------------------
# CHECK MODE
# If the prompt begins with [check], Claude is instructed to ASSESS the
# request and stop, without executing it or calling tools. The current
# model does the assessing, so it uses real understanding and the full
# conversation context, not keywords. The prompt stays in the
# conversation, so after an optional /model switch the user types "go".
# -------------------------------------------------------
CHECK_PREFIX_RE = re.compile(r"^\s*\[\s*check\s*\]\s*", re.IGNORECASE)

CHECK_MODE_INSTRUCTION = (
    "CHECK MODE. The user prefixed this prompt with [check]. Do NOT execute the "
    "request, do NOT call any tools, do NOT start the task, and do NOT write "
    "task_state.json. Instead reply with a short assessment, under 120 words: "
    "(1) one line restating what the request would involve; "
    "(2) size and depth: trivial / medium / complex / long-horizon; "
    "(3) recommended model (Haiku 4.5, Sonnet 5, Opus 5.5 or Fable 5.1) and effort "
    "(low / medium / high), with a one-sentence reason; "
    "(4) whether the current task state allows switching. "
    "End with exactly: 'Switch with /model if needed, then type go.' "
    "The keyword heuristic guessed {label}; override it if your reading differs."
)

FORBIDDEN_MODULES = ("subprocess", "pty", "multiprocessing")


# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def check_prime_directive():
    """
    Return a violation string if any process-spawning module is loaded,
    else an empty string. This hook must never shell out.
    """
    loaded = [m for m in FORBIDDEN_MODULES if m in sys.modules]
    if loaded:
        return (
            "PRIME DIRECTIVE VIOLATION: process-spawning module(s) loaded: "
            + ", ".join(loaded)
        )
    return ""


def read_task_state():
    """
    Sole clean-state signal.
    Returns (status, task, detail, project, cwd, updated) from task_state.json.
    Falls back to ("unknown", "", "", "", "", "") if file missing or unreadable.
    Status is "missing" if the file parses but has no status field.
    """
    try:
        with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (
            data.get("status", "missing"),
            data.get("task", ""),
            data.get("detail", ""),
            data.get("project", ""),
            data.get("cwd", ""),
            data.get("updated", ""),
        )
    except Exception:
        return ("unknown", "", "", "", "", "")


def state_age_hours(updated_str):
    """
    Return hours since the last write of task_state.json, or None.
    Primary source is the file's mtime. The 'updated' field is only a
    fallback if the file cannot be stat'ed; naive values are treated as
    LOCAL time, because that is how the convention writes them.
    """
    try:
        try:
            # File mtime is the true time of the last write. Claude does not
            # know the wall clock, so the 'updated' field is only a fallback.
            updated = datetime.fromtimestamp(os.path.getmtime(TASK_STATE_FILE)).astimezone()
        except OSError:
            updated = datetime.fromisoformat(updated_str)
            if updated.tzinfo is None:
                updated = updated.astimezone()
        delta = datetime.now().astimezone() - updated
        return delta.total_seconds() / 3600
    except Exception:
        return None


def assess_clean_state():
    """
    Returns (is_clean, reason, is_stale, age_hours, project, task_cwd).
    """
    task_status, task_name, task_detail, project, task_cwd, updated = read_task_state()
    # Age comes from file mtime, so it is computed even if 'updated' is empty.
    age_hours = state_age_hours(updated)
    is_stale = (
        task_status == "in_progress"
        and age_hours is not None
        and age_hours > STALE_HOURS
    )
    project_tag = f" [{project}]" if project else ""

    if task_status == "in_progress":
        reason = f"task in progress: '{task_name}'{project_tag}"
        if task_detail:
            reason += f" -- {task_detail}"
        return False, reason, is_stale, age_hours, project, task_cwd

    if task_status == "clean":
        return True, "task_state.json: clean", False, None, project, task_cwd

    if task_status == "unknown":
        return True, "task_state.json missing or unreadable -- assuming clean", False, None, "", ""

    if task_status == "missing":
        return True, "task_state.json has no status field -- assuming clean", False, None, project, task_cwd

    # Any other value is a convention breach (typo or unknown state).
    # Same handling as state_monitor.py: report it, assume clean.
    return (
        True,
        f"task_state.json status='{task_status}' is not clean/in_progress -- assuming clean",
        False, None, project, task_cwd,
    )


def kw_match(kw, prompt_lower):
    """Word-boundary match: keyword must not be embedded in a longer token."""
    pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
    return re.search(pattern, prompt_lower) is not None


def recommend_model(prompt_lower):
    word_count = len(prompt_lower.split())
    for label, model_id, purpose, keywords in MODEL_RULES:
        if label.startswith("Haiku") and word_count > HAIKU_MAX_WORDS:
            continue
        for kw in keywords:
            if kw_match(kw, prompt_lower):
                return label, model_id, kw, purpose
    return DEFAULT_MODEL_LABEL, DEFAULT_MODEL_ID, "default", DEFAULT_MODEL_PURPOSE


def recommend_effort(prompt_lower):
    if any(kw_match(kw, prompt_lower) for kw in EFFORT_HIGH_KEYWORDS):
        return "high"
    if any(kw_match(kw, prompt_lower) for kw in EFFORT_LOW_KEYWORDS):
        return "low"
    return None


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    # Current docs name the field "user_prompt"; older builds used "prompt".
    prompt = data.get("user_prompt") or data.get("prompt", "")
    check_mode = CHECK_PREFIX_RE.match(prompt) is not None
    if check_mode:
        prompt = CHECK_PREFIX_RE.sub("", prompt, count=1)
    pl     = prompt.lower()

    violation = check_prime_directive()
    # project and cwd are informational only (kept in the file for the user).
    is_clean, state_reason, is_stale, age_hours, _project, _task_cwd = assess_clean_state()
    model_label, _, trigger, purpose = recommend_model(pl)
    effort   = recommend_effort(pl)
    is_fable = "Fable" in model_label

    state_tag = "[CLEAN]" if is_clean else "[DIRTY]"

    # ---- user-visible message (systemMessage) ----
    # Model recommendation only. The STATE is shown by state_monitor.py
    # (Stop hook) at the end of each turn, before the user types.
    lines = [
        "GATEKEEPER" + ("  -- CHECK MODE: assessment only, nothing will be executed" if check_mode else ""),
        f"  Model  : /model {model_label}  (trigger: '{trigger}')",
        f"  Use for: {purpose}",
    ]
    if effort:
        lines.append(f"  Effort : consider /effort {effort}")
    if not is_clean:
        lines.append(f"  ! {state_tag} task in progress -- hold off switching model/effort")
    if is_fable:
        lines.append(f"  ! {FABLE_WARNING}")
    if violation:
        lines.append(f"  !!! {violation}")
    system_message = "\n".join(lines)

    # ---- context injected for Claude (additionalContext) ----
    stale_note = ""
    if is_stale and age_hours is not None:
        stale_note = f" WARNING: state has been in_progress for {int(age_hours)}h -- may be stale."

    if is_clean and state_reason == "task_state.json: clean":
        state_text = "clean -- safe to switch model or effort"
    elif is_clean:
        state_text = "clean (" + state_reason + ") -- safe to switch model or effort"
    else:
        state_text = (
            "DIRTY (" + state_reason + ") -- hold off switching model or effort "
            "until current task is complete"
        )

    injected = (
        f"[Gatekeeper] State: {state_text}.{stale_note} "
        f"Suggested model: {model_label} (matched keyword '{trigger}'; {purpose})."
    )
    if effort:
        injected += f" Suggested effort: {effort}."
    if is_fable:
        injected += f" {FABLE_WARNING}"
    if violation:
        injected += f" {violation}"

    # ---- Check mode: assess only, no execution, no state writes ----
    if check_mode:
        injected += " " + CHECK_MODE_INSTRUCTION.format(label=model_label)

    # ---- Option D: state maintenance instruction for Claude ----
    # Claude keeps task_state.json honest at the END of its turn, because
    # a Stop hook then displays it to the user before the next prompt.
    # Skipped in check mode: nothing is started or finished.
    if check_mode:
        pass
    elif is_clean:
        injected += (
            " [Option D] Before ending this turn: if you START substantial work "
            "(code, TTL, SPARQL, multi-section docs, a build phase), write "
            "task_state.json with status in_progress. Do NOT write it for "
            "trivial Q&A."
        )
    else:
        injected += (
            " [Option D] Before ending this turn: if the in-progress task is now "
            "COMPLETE or handed off to the user, write task_state.json with status "
            "clean. If it is still mid-flight, leave it. If you have moved on to a "
            "different substantial task, overwrite it with the new task."
        )

    out = {
        "systemMessage": system_message,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": injected,
        },
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
