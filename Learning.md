---
title:  "Learning Claude Code"
author: "C. Chee"
---

<h1 align="center"> Learning Claude Code </h1>

---

## Copyright and Publication Information

**Learning Claude Code**

Copyright © 2026 Clinton Chee
All rights reserved.

**Author:** Clinton Chee (PhD)
**Publisher:** Clinton Chee
**Edition:** First Edition, 2026  
**Place of Publication:** Sydney, Australia  
**Website:** https://cheealtair.github.io/workClaude/

This publication is made available as an independently published ebook.

No part of this publication may be reproduced, distributed, modified, or republished for commercial purposes without prior written permission from the copyright holder, except for brief quotations used for review, commentary, education, or other uses permitted by law.

The information in this book is provided for educational and informational purposes. Technologies, software products, commands, services, interfaces, pricing, licensing arrangements, and features discussed in this book may change over time. Readers should verify current information with the relevant official documentation before relying on technical instructions.

Product names, trademarks, service marks, and registered trademarks mentioned in this publication remain the property of their respective owners. Their use in this book is for identification and educational purposes only and does not imply endorsement or affiliation.

**ISBN:** Not assigned

---




## Table of Contents

- [Part 1: Vibe Coding with Claude](#part-1-vibe-coding-with-claude)
  - [Chapter 1: Claude Desktop vs Claude Code](#chapter-1-claude-desktop-vs-claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Claude Code (Terminal)](#claude-code-terminal)
    - [The agentic difference](#the-agentic-difference)
    - [What Claude Code has that Desktop doesn't](#what-claude-code-has-that-desktop-doesnt)
    - [What Claude Desktop has that Code doesn't](#what-claude-desktop-has-that-code-doesnt)
    - [What both share](#what-both-share)
  - [Chapter 2: Setting Up Claude Code](#chapter-2-setting-up-claude-code)
    - [Individual vs Enterprise](#individual-vs-enterprise)
    - [What you need (and what you don't)](#what-you-need-and-what-you-dont)
    - [Why a Bash shell matters (and your options on Windows)](#why-a-bash-shell-matters-and-your-options-on-windows)
    - [Step 1: Set environment variables](#step-1-set-environment-variables)
    - [Step 2: Install Claude Code](#step-2-install-claude-code)
    - [Step 3: First run](#step-3-first-run)
    - [Useful commands](#useful-commands)
    - [Slash commands (inside the REPL)](#slash-commands-inside-the-repl)
    - [Switching models](#switching-models)
    - [Known issues](#known-issues)
    - [Permission modes](#permission-modes)
  - [Chapter 3: Claude Concepts](#chapter-3-claude-concepts)
    - [Key concepts at a glance](#key-concepts-at-a-glance)
    - [Workplans](#workplans)
    - [Skills](#skills)
    - [Comparing the Four Systems](#comparing-the-four-systems)
  - [Chapter 4: The Agent Harness](#chapter-4-the-agent-harness)
    - [What Is a Harness?](#what-is-a-harness)
    - [Core Responsibilities of the Harness](#core-responsibilities-of-the-harness)
      - [1. The Agent Loop](#1-the-agent-loop)
      - [2. Tool Dispatch](#2-tool-dispatch)
      - [3. System Prompt as Harness Configuration](#3-system-prompt-as-harness-configuration)
      - [4. Permission System — Defense in Depth](#4-permission-system--defense-in-depth)
      - [5. Context Window Management — The Hard Problem](#5-context-window-management--the-hard-problem)
        - [Strategies](#strategies)
        - [What gets injected every turn regardless of compression:](#what-gets-injected-every-turn-regardless-of-compression)
        - [What gets compressed:](#what-gets-compressed)
      - [6. Memory and Persistence](#6-memory-and-persistence)
      - [7. Hooks — Harness-Level Side Effects](#7-hooks--harness-level-side-effects)
        - [Event Types](#event-types)
        - [What Makes Hooks Powerful](#what-makes-hooks-powerful)
        - [Practical Uses](#practical-uses)
      - [8. Multi-Agent Orchestration](#8-multi-agent-orchestration)
        - [Concurrency Management](#concurrency-management)
        - [The Workflow Script as Harness Code](#the-workflow-script-as-harness-code)
        - [Key Workflow Primitives](#key-workflow-primitives)
      - [9. Structured Output — Harness-Enforced Schema](#9-structured-output--harness-enforced-schema)
      - [10. Isolation — Worktrees and Sandboxes](#10-isolation--worktrees-and-sandboxes)
    - [Model vs. Harness — Definitive Responsibility Table](#model-vs-harness--definitive-responsibility-table)
    - [The Harness in Other LLM Coding Agents](#the-harness-in-other-llm-coding-agents)
    - [The Fundamental Tensions Every Harness Must Navigate](#the-fundamental-tensions-every-harness-must-navigate)
      - [Autonomy vs. Safety](#autonomy-vs-safety)
      - [Capability vs. Cost](#capability-vs-cost)
      - [Determinism vs. Flexibility](#determinism-vs-flexibility)
      - [Summary](#summary)  
  - [Chapter 5: CLAUDE.md](#chapter-5-claudemd)
    - [What its contents are based on](#what-its-contents-are-based-on)
    - [What it should contain](#what-it-should-contain)
    - [Hierarchy](#hierarchy-loaded-in-order-later-wins)
    - [How to create one](#how-to-create-one)
    - [.claude/rules/ Examples](#clauderules-examples)
  - [Chapter 6: Working with Claude Code](#chapter-6-working-with-claude-code)
    - [Stage 1: Set Up](#stage-1-set-up)
    - [Stage 2: Orient](#stage-2-orient)
    - [Stage 3: Plan](#stage-3-plan)
    - [Stage 4: Build](#stage-4-build)
    - [Stage 5: Verify](#stage-5-verify)
    - [Stage 6: Ship](#stage-6-ship)
    - [Stage 7: Accumulate](#stage-7-accumulate)
- [Part 2: Graph Studio and Lakehouse](#part-2-graph-studio-and-lakehouse)
  - [Chapter 7: Open Source Technologies](#chapter-7-open-source-technologies)
- [Appendix](#appendix)
  - [Chapter 8: Anecdotes](#chapter-8-anecdotes)

---

# Part 1: Vibe Coding with Claude

*Intent-Driven System Crafting / Intent Orchestration / IntentFlow*

**Claude** is Anthropic's AI assistant — a large language model trained to be helpful, harmless, and honest. It understands natural language, writes and reasons about code, analyzes documents, and handles complex multi-step tasks. Claude is the intelligence behind all Anthropic products: whether you're chatting in a browser, running commands in a terminal, or calling an API, the same underlying model is doing the thinking. The products built around it — Claude Desktop, Claude Code, the Claude API — are different interfaces to the same brain, each optimized for a different workflow.

## Quotes

Boris - Creator of Claude Code
> "It's a power tool, so you can use it for a lot of things, but also because it can do so much, we don't try to guide you towards a particular workflow."

Ref: [Anthropic Claude Code Prompt Engineering in 27 Min](https://www.youtube.com/watch?v=lazK8un1bdw)

Amelia Earhart - Aviation Pioneer
> "Preparation, I have often said, is rightly two-thirds of any venture."

## Chapter 1: Claude Desktop vs Claude Code

### Claude Desktop

A chat-focused application with a rich visual interface. Good for conversations, document analysis, and general Q&A. It can connect to MCP servers and supports file/image upload, but it does not have direct access to your filesystem, terminal, or development tools.

### Claude Code (Terminal)

A developer tool that runs directly in your shell. It operates inside your development environment with full tool access — reading, writing, and editing files, running shell commands (PowerShell, Bash, git, pip, etc.), searching your codebase, connecting to MCP servers, managing git workflows, and persisting memory across sessions.

### The agentic difference

Claude Desktop is **conversational** — you ask, it answers. The interaction is reactive: one prompt in, one response out.

Claude Code is **agentic** — it doesn't just generate text, it takes action. Given a goal, it can autonomously plan a sequence of steps, execute them (read files, run commands, edit code, search a codebase), observe the results, and adapt. A single prompt like "fix the failing tests" can trigger Claude to locate the test file, read the error, trace the root cause across multiple files, apply a fix, re-run the tests, and verify they pass — all without further instruction.

This is the core distinction: an agent doesn't wait to be told what to do next. It operates in a loop — **think, act, observe, repeat** — until the task is done or it needs your input.

### What Claude Code has that Desktop doesn't

| Capability | Description |
|---|---|
| Direct filesystem access | Read, write, and edit files on your machine |
| Shell command execution | PowerShell, Bash, git, pip, npm, and any CLI tool |
| Codebase search | Grep and glob tools for fast code navigation |
| Git workflows | Commits, branches, PRs, diffs — all from the conversation |
| Persistent memory | Remembers context across sessions via file-based memory |
| Task tracking | Built-in task creation and progress management |
| Background processes | Launch and monitor long-running processes |

### What Claude Desktop has that Code doesn't

| Capability | Description |
|---|---|
| Rich visual UI | Inline rendering of images, charts, and formatted content |
| Drag-and-drop upload | Drop files and images directly into the conversation |
| Project knowledge files | Separate project knowledge system (distinct from CLAUDE.md) |
| Artifacts | Interactive code previews and rendered documents |
| Non-technical interface | Designed for a broader, less developer-focused audience |

### What both share

- MCP server connections
- Web search
- Long conversations with context management

Neither is a strict subset of the other. Claude Code is purpose-built for software engineering workflows; Claude Desktop is a more general-purpose assistant with a richer visual interface.

---

## Chapter 2: Setting Up Claude Code

Claude Code is an agentic coding assistant that runs in your terminal. It reads, writes, and executes commands across entire repos. In enterprise environments, it can route through a corporate API gateway for compliance.

### Individual vs Enterprise

| Aspect | Individual (personal account) | Enterprise (corporate gateway) |
|--------|-------------------------------|-------------------------------|
| **Account** | Personal Anthropic account at [console.anthropic.com](https://console.anthropic.com) | Corporate API gateway account |
| **Authentication** | Browser login (easiest) or personal API key | Corporate gateway API key |
| **Environment variables** | `ANTHROPIC_API_KEY` only — or none with browser login | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `CODE_SCAN_TOKEN`, `ANTHROPIC_MODEL` |
| **Install** | 1 command | 2 commands (install + compliance post-install) |
| **First run** | Browser login prompt | "Custom API key detected" prompt |
| **Approval gating** | None | May require business unit approval |

> The sections below cover both paths. Look for **Individual** and **Enterprise** labels.

### What you need (and what you don't)

**Individual — Required:**

| Requirement | Where to get it | Notes |
|---|---|---|
| **Anthropic account** | [console.anthropic.com](https://console.anthropic.com) | Free to sign up. Add billing for API usage, or use the included free tier. |
| **A terminal** | Any terminal: PowerShell, CMD, Bash, Zsh | Claude Code is a CLI tool |
| **Internet connection** | — | Required for API calls |

> With browser login (`claude login`), you don't even need an API key — Claude Code opens your browser to authenticate. This is the simplest path.

**Enterprise — Required:**

| Requirement | Where to get it | Notes |
|---|---|---|
| **Corporate API Gateway key** | Your organization's LLM gateway portal → follow your team's access request process | Check with your admin for access details |
| **GitLab Personal Access Token** | Your corporate GitLab instance → User Settings → Access Tokens → scopes `read_user` and `read_repository` | Token starts with `glpat-...` — save it locally |
| **A terminal** | Any terminal: PowerShell, CMD, Bash, Zsh | Claude Code is a CLI tool — it runs in whatever shell you have |
| **Internet connection** | — | Required for API calls to the corporate gateway |
| **4 GB+ RAM** | — | Minimum system requirement |

**Not required:**

| Tool | Status | Notes |
|---|---|---|
| **VS Code** | Not needed | Claude Code is a standalone terminal tool. No IDE required. |
| **Git** | Optional but recommended | Useful for version control workflows. On Windows, Git for Windows also provides a Bash shell (see below). Claude Code works without it — it falls back to PowerShell. |
| **Git Bash** | Optional | One of several ways to get a Bash shell on Windows. See next section. |

> **Approval gating (Enterprise only)** — Claude Code may be rolling out by business unit. Confirm your business unit is approved for Claude Code usage on your organization's LLM gateway portal before proceeding.

### Why a Bash shell matters (and your options on Windows)

Claude Code's internal tools generate shell commands. Many use Bash idioms — pipes, `grep`, `find`, `&&` chaining, `$VAR` syntax. A Bash shell means commands work identically across macOS, Linux, and Windows. Without one, Claude Code falls back to PowerShell, which works but has different syntax rules (no `&&` operator, `$env:VAR` instead of `$VAR`, backtick escaping instead of backslash).

On macOS and Linux, Bash/Zsh is already your default shell — no action needed. On Windows, you have several options:

| Option | What it is | Recommended? | Notes |
|---|---|---|---|
| **No Bash (PowerShell only)** | Use Claude Code with its PowerShell fallback | Works fine | Simplest setup. Claude Code adapts automatically. Minor syntax differences are handled for you. |
| **Git Bash** (via Git for Windows) | MSYS2-based Bash bundled with Git | Yes — if you want Git anyway | Lightweight (~300 MB). Most common choice. Set `CLAUDE_CODE_GIT_BASH_PATH` if not auto-detected. |
| **WSL2** (Windows Subsystem for Linux) | Full Linux kernel running inside Windows | Best overall | Install Claude Code *inside* WSL2 using the Linux installer. Native Linux environment — `apt`, `grep`, `find`, proper Bash, everything. Windows folders accessible at `/mnt/c/`, `/mnt/d/`, etc. |
| **MSYS2** (standalone) | The toolkit Git Bash is built on | Yes — for power users | Includes `pacman` package manager. Point `CLAUDE_CODE_GIT_BASH_PATH` to its `bash.exe`. |
| **Cygwin** | Older POSIX compatibility layer | Not recommended | Heavy, being superseded by WSL2 in most workflows. |
| **MobaXterm** | SSH/X11 client with embedded Cygwin | No | Its Bash is sandboxed inside MobaXterm — not exposed as a system shell for other tools to call. |

**Bottom line:** If you're on Windows and want the fullest experience, WSL2 is the strongest option. If you just want to get started quickly, PowerShell alone works — you won't hit a wall.

### Step 1: Set environment variables

#### Individual — Option A: Browser login (no env vars needed)

Skip this step entirely. At first run, Claude Code will prompt you to log in via your browser. No environment variables required.

#### Individual — Option B: API key

If you prefer using an API key, set just one variable:

**macOS / Linux / WSL2:**

```bash
echo 'export ANTHROPIC_API_KEY="<your-anthropic-api-key>"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "<your-anthropic-api-key>", "User")
$env:ANTHROPIC_API_KEY = "<your-anthropic-api-key>"
```

Get your key from [console.anthropic.com](https://console.anthropic.com) → API Keys.

#### Enterprise

Set all required variables for your corporate gateway:

##### macOS / Linux / WSL2

```bash
nano ~/.zshrc    # or ~/.bashrc if using Bash
```

Add at the bottom:

```bash
# Claude Code via corporate API gateway
export ANTHROPIC_API_KEY="<your-sdc-gateway-api-key>"
export ANTHROPIC_BASE_URL="https://<your-corporate-gateway-url>"
export ANTHROPIC_MODEL="claude-sonnet-4-6@default"
export CODE_SCAN_TOKEN="<your-gitlab-PAT>"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
```

Replace placeholders with your real values. Save (`Ctrl+O`, `Enter`, `Ctrl+X`). Reload:

```bash
source ~/.zshrc    # or source ~/.bashrc
```

Verify:

```bash
echo $ANTHROPIC_BASE_URL
echo $ANTHROPIC_MODEL
echo "API_KEY length: ${#ANTHROPIC_API_KEY}"
```

Should print the URL, model name, and a number around 64 (the key length).

##### Windows (PowerShell)

Allow custom profile scripts (one-time):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Press `Y` when prompted. Create the profile file:

```powershell
New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force
New-Item -ItemType File -Path $PROFILE -Force
notepad $PROFILE
```

Notepad opens. Paste:

```powershell
# Claude Code via corporate API gateway
$env:ANTHROPIC_API_KEY = "<your-sdc-gateway-api-key>"
$env:ANTHROPIC_BASE_URL = "https://<your-corporate-gateway-url>"
$env:ANTHROPIC_MODEL = "claude-sonnet-4-6@default"
$env:CODE_SCAN_TOKEN = "<your-gitlab-PAT>"
$env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = "1"
```

Replace placeholders. Save (`Ctrl+S`), close Notepad. Load:

```powershell
. $PROFILE
```

Verify:

```powershell
echo $env:ANTHROPIC_BASE_URL
echo $env:ANTHROPIC_MODEL
```

> Do **not** set `ANTHROPIC_AUTH_TOKEN`. Only `ANTHROPIC_API_KEY`. Setting both triggers an "Auth conflict" warning.

### Step 2: Install Claude Code

#### Individual

Run one command:

**macOS / Linux / WSL2:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

That's it — skip to the PATH and verification steps below.

#### Enterprise

Run **both** commands — the first installs Claude Code, the second pulls corporate compliance settings. Without the second command, you may not be compliant with your organization's policies.

**macOS / Linux / WSL2:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
curl -fsSL https://<your-org-post-install-url>/post-install.sh | sh
```

**Windows (PowerShell):**

```powershell
irm https://claude.ai/install.ps1 | iex
irm https://<your-org-post-install-url>/post-install.ps1 | iex
```

Add the install directory to your User PATH if not already there:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.local\bin", "User")
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
```

**Optional — if you have Git Bash and want Claude Code to use it:**

```powershell
where.exe bash
```

If it returns a path like `C:\Program Files\Git\bin\bash.exe`, Claude Code will detect it automatically. If installed but not detected, set the env var `CLAUDE_CODE_GIT_BASH_PATH` to the correct path via Windows Settings → Environment Variables.

Verify the install:

```powershell
claude --version
```

**Installation footprint:**

| Component | Location | Size |
|---|---|---|
| CLI binary | `~\.local\bin\claude.exe` | ~218 MB |
| Config & sessions | `~\.claude\` | ~13 MB (grows with usage) |
| **Total** | | **~231 MB** |

### Step 3: First run

```bash
claude "say hello and tell me which model you are running"
```

#### Individual

If you used browser login (Option A): Claude Code opens your default browser to authenticate. Sign in with your Anthropic account and you're done.

If you used an API key (Option B): You'll be prompted to confirm using the detected API key — pick **Yes**.

Pick a theme and trust the current folder when prompted. You should see a response from **Claude Sonnet** (the default model on your plan).

#### Enterprise

You'll be prompted in sequence:

1. **"Detected a custom API key in your environment — Yes/No"** → pick **Yes** (default is "No (recommended)" — override it; the key is correct)
2. **Theme** → either is fine
3. **Folder trust** → trust the current folder if it's a project

You should see a response identifying **Claude Sonnet 4.6** (`claude-sonnet-4-6@default`). If it works — Claude Code is installed and routing through your corporate gateway.

### Useful commands

| Command | What it does |
|---|---|
| `claude` | Launches interactive REPL in current folder |
| `claude "<prompt>"` | One-shot prompt |
| `claude --continue` | Resume the most recent session in this folder |
| `claude --resume` | Pick from a list of past sessions |
| `claude --debug` | Verbose logs (when something goes wrong) |
| `/init` (inside REPL) | Generate a CLAUDE.md for the current project |
| `/exit` (inside REPL) | Exit the session |

### Slash commands (inside the REPL)

Once inside an interactive session, these `/` commands are available:

| Command | Description |
|---|---|
| `/help` | Show all available commands and usage info |
| `/exit` | Exit the current session |
| `/clear` | Clear conversation history and start fresh (saves history) |
| `/compact [focus]` | Summarize conversation to free context window space |
| `/context` | Show what's consuming context window space |
| `/init` | Generate a CLAUDE.md by scanning the codebase |
| `/memory` | View and edit CLAUDE.md, auto memory, and rules |
| `/model [name]` | Switch model (opus, sonnet, haiku) |
| `/effort [level]` | Set reasoning effort (low, medium, high, xhigh) |
| `/think` | Toggle extended thinking for one response |
| `/plan` | Enter plan mode (read-only exploration) |
| `/resume [name]` | Switch to a different past session |
| `/rename [name]` | Name the current session |
| `/branch [name]` | Branch the session to try a different approach |
| `/export [file]` | Save conversation to a file |
| `/config` | Configure settings (theme, language, etc.) |
| `/permissions` | View and manage permission rules |
| `/mcp` | View MCP server status and token costs |
| `/skills` | Browse and manage available skills |
| `/agents` | View running subagents and custom agents |
| `/doctor` | Diagnose configuration issues |
| `/keybindings` | View and edit keyboard shortcuts |
| `/statusline` | Configure the status bar UI |
| `/voice` | Configure voice dictation |
| `/add-dir [path]` | Grant Claude access to another directory |
| `/add-mcp` | Connect a new MCP server |
| `/add-plugin` | Install a plugin |
| `/background` | Detach session to run in background |
| `/tasks` | View background tasks |
| `/login` | Switch accounts |
| `/btw` | Quick aside without bloating conversation history |
| `/desktop` | Hand off to desktop app for visual review |
| `/schedule` | Set up a recurring routine |
| `/loop [interval]` | Run a prompt on a recurring interval |

### Switching models

Override per-session by setting `ANTHROPIC_MODEL` before launch:

```bash
ANTHROPIC_MODEL="claude-opus-4-6@default" claude
```

| Model | When to use | Relative cost |
|---|---|---|
| `claude-sonnet-4-6@default` | Day-to-day, demos, general work | 1x (default) |
| `claude-opus-4-6@default` | Complex reasoning, architecture, large refactors | ~5x |
| `claude-haiku-4-5-20251001` | Quick lookups, simple edits | Cheapest |

> All token usage hits your cost centre. Use Opus deliberately.

### Known issues

| Issue | Workaround |
|---|---|
| "Auth conflict" warning on first run | Remove `ANTHROPIC_AUTH_TOKEN` from profile. If persistent, delete `~/.claude` folder and re-run |
| Two Claude Code installs after migration from npm version | `which -a claude` to confirm; `npm uninstall -g @anthropic-ai/claude-code` to clean up |
| PowerShell paste mashes commands together | Run commands one at a time during setup |
| File I/O slower when accessing Windows folders from WSL2 | For heavy workloads, clone repos into the WSL home directory (`~/`) instead of working under `/mnt/` |

### Permission modes

Claude Code has six permission modes that control how much autonomy Claude has during a session. You can cycle between them by pressing **Shift+Tab**, or set a default in `settings.json`.

| Mode | Behaviour | When to use |
|---|---|---|
| **default** | Prompts for permission on first use of each tool | Standard everyday workflow — the starting mode for new sessions |
| **plan** | Read-only — Claude can explore the codebase but cannot edit files | Designing strategy before coding; reviewing unfamiliar code |
| **acceptEdits** | Auto-accepts file edits and filesystem commands (mkdir, mv, cp, etc.) | Trusted projects where you want less approval friction |
| **auto** | Auto-approves tool calls with background safety checks | Experimental — lets Claude move faster when you trust the safety classifier |
| **dontAsk** | Auto-denies everything unless pre-approved via an allowlist | Restrictive environments; only explicitly permitted tools can run |
| **bypassPermissions** | Skips all permission prompts | Sandboxed containers and VMs only — never use in production |

**Plan mode** is particularly useful for complex tasks. Claude explores the codebase, reads files, runs commands, and writes a structured workplan — all without touching any code. You review and approve the plan before Claude begins implementation. This was the workflow used to design the VoiceAI watcher (Approach 2) before any code was written.

To set a default mode, add to `.claude/settings.json`:

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

---

## Chapter 3: Claude Concepts

This chapter covers key concepts in how Claude Code thinks and works — the mental models and mechanisms that shape how Claude approaches tasks. Understanding these helps you collaborate with Claude more effectively.

### Key concepts at a glance

- **Workplans** — structured plan files Claude writes before complex tasks, serving as a roadmap for implementation and a reference that survives context compression.
- **Context Window & Compression** — Claude has a finite memory within a session. In long conversations, earlier messages are silently compressed or dropped. Workplans and memory files persist beyond this limit.
- **Memory** — persistent files stored in `~/.claude/projects/` that carry knowledge across sessions. Stores user preferences, feedback, project context, and references. The context window is short-term; memory is long-term.
- **Tools** — Claude doesn't just generate text. It acts through tools (Read, Edit, Write, Grep, Glob, Bash, and more). Each tool is purpose-built for a specific kind of action.
- **Agents & Subagents** — Claude can spawn specialised sub-agents for parallel work. An Explore agent searches the codebase, a Plan agent designs approaches. They run independently and report back.
- **Tasks** — an in-session checklist Claude uses to track progress on multi-step work. Visible to both you and Claude, helping both sides stay aligned during complex implementations.
- **Hooks** — shell commands that trigger automatically on events (before or after tool calls). These are automations the system runs, not Claude.
- **Skills** — reusable prompt templates stored in `.claude/skills/` that package multi-step workflows into a single `/skill-name` command. They load on demand, keeping context lean until invoked.
- **MCP (Model Context Protocol)** — how Claude connects to external services and tools beyond the built-in ones, extending its capabilities to third-party systems.
- **Sessions** — each Claude Code invocation is a session with its own JSONL transcript, context state, and identity. Session files are what the VoiceAI watcher tails to speak responses aloud.

### Workplans

A workplan is a structured document that Claude writes before tackling a complex task. It lives as a plan file at `~/.claude/plans/<name>.md` and serves as Claude's roadmap for implementation.

#### What a workplan contains

A well-formed workplan typically includes:

- **Context** — why this change is being made, what prompted it, the intended outcome
- **Implementation steps** — ordered phases of work, each with clear deliverables
- **Files to create or modify** — specific paths, not vague references
- **Design decisions** — choices made and why, alternatives considered and rejected
- **Existing code to reuse** — functions, patterns, and modules already in the codebase that should be leveraged rather than reinvented
- **Verification** — how to test that the implementation works end-to-end

#### How Claude uses the workplan internally

The workplan is not just documentation — it is a working tool that Claude refers back to during implementation:

1. **Exploration phase** — Claude reads files, searches the codebase, and investigates the problem space. This is where surprises surface (e.g., discovering that Claude Code already writes JSONL session transcripts, which changed the entire approach for the VoiceAI watcher).

2. **Design phase** — Claude synthesises what it learned into a structured plan. Design decisions are made explicit: what approach to take, what trade-offs are accepted, what dependencies are needed.

3. **Approval gate** — the plan is presented to you. Nothing is built until you approve. This is where you catch misunderstandings, redirect the approach, or add constraints Claude missed.

4. **Implementation phase** — Claude follows the plan step by step, checking off phases as they complete. If context compression occurs during a long session (earlier messages are silently dropped to stay within the context window), the plan file persists as a reference point Claude can re-read.

5. **Verification phase** — Claude tests the implementation against the verification criteria defined in the plan.

#### How to write requests that produce good workplans

The quality of the workplan depends heavily on how you frame the request. Here are guidelines for getting the best results:

**State the outcome, not the steps.** "Build a watcher that speaks Claude's responses aloud" gives Claude room to design the right solution. "Create a file called watcher.py, add a class called FileTailer, write a polling loop" locks Claude into your preconceived implementation, which may not be the best one.

**Name your constraints.** "No new pip dependencies," "must work on Windows," "reuse the existing voices.json" — these fence the solution space. Without them, Claude may propose solutions that don't fit your environment.

**Flag what you don't know.** "I'm not sure if Claude Code writes logs anywhere" tells Claude where to explore first. Silence on a topic means Claude assumes you don't care about it.

**Highlight what you care about.** If performance matters more than readability, say so. If you want minimal code over comprehensive code, say so. Claude optimises for whatever you emphasise.

**Ask for the plan explicitly.** Phrases like "make a plan first," "plan before coding," or "make a plan of execution" trigger the structured planning workflow. Without an explicit request, Claude may jump straight to implementation.

**Give context about why, not just what.** "We need this because the manual copy-paste workflow is too slow" helps Claude make better trade-off decisions than "build an automated version."

#### When NOT to use a workplan

Workplans add overhead. Skip them for:

- Single-line fixes (typos, obvious bugs, small tweaks)
- Tasks where you've already given detailed, specific instructions
- Quick exploratory questions ("what does this function do?")
- Adding a few lines to an existing file with a clear pattern

A good rule of thumb: if the task touches more than two or three files, involves design decisions, or could reasonably be solved multiple ways — ask for a workplan.

#### Real example: VoiceAI Approach 2

The workplan for the VoiceAI log file watcher was triggered by the request: "Let's move to approach 2. Make a plan of execution for Approach 2."

During the exploration phase, Claude discovered that Claude Code already writes structured JSONL session transcripts — a data source that wasn't mentioned in the original Research.md design. This pivoted the entire approach from fragile terminal text parsing to clean structured JSON extraction. The workplan captured this pivot, documented the six implementation phases, listed design decisions in a table, and defined verification steps. Only after approval did implementation begin.

Without the workplan, the JSONL discovery might have been buried in a stream of code changes, and the design rationale would have been lost to context compression.

### Skills

A skill is a reusable prompt template stored as a markdown file in `.claude/skills/`. When invoked via `/skill-name` in the REPL, Claude loads the skill's instructions into its context and executes them. Skills are the mechanism for packaging repeatable, multi-step workflows into a single command.

#### How skills differ from other mechanisms

| Mechanism | When it loads | Who enforces it | Best for |
|---|---|---|---|
| **CLAUDE.md** | Every session, automatically | Claude (advisory) | Conventions, architecture notes, always/never rules |
| **Rules** (`.claude/rules/`) | When Claude reads matching files | Claude (advisory) | File-type-specific conventions |
| **Memory** | When Claude judges it relevant | Claude (advisory) | Cross-session knowledge, user preferences |
| **Hooks** | On specific events, always | The system (enforced) | Automated formatting, linting, notifications |
| **Skills** | On demand, when you invoke them | Claude (advisory) | Repeatable multi-step workflows |

The key distinction: CLAUDE.md and rules load passively (every session or on file access). Skills load actively — only when you call them. This keeps them out of your context window until you need them, which matters when a skill's instructions are long or specialised.

#### Anatomy of a skill file

A skill is a markdown file in `.claude/skills/` with optional YAML frontmatter:

```
.claude/
└── skills/
    ├── lint-and-fix.md
    ├── pr-review.md
    ├── db-migrate.md
    └── deploy-staging.md
```

Each file follows this structure:

```markdown
---
name: lint-and-fix
description: Run linter, fix all issues, run tests, report results
---

## Instructions

1. Run `npm run lint` and capture the output
2. For each error reported, fix it in the source file
3. Re-run `npm run lint` to verify all issues are resolved
4. Run `npm test` to confirm no regressions
5. Report: number of issues fixed, files changed, test results
```

- **`name`** — the slug used to invoke the skill (e.g., `/lint-and-fix`)
- **`description`** — a one-line summary shown when browsing skills with `/skills`
- **Body** — the prompt instructions Claude follows when the skill is invoked. Write these as you would write a prompt — clear, specific, outcome-focused

#### Detailed examples

##### Example 1: Code quality sweep

**`.claude/skills/quality-sweep.md`**
```markdown
---
name: quality-sweep
description: Full code quality pass — lint, type-check, test, and report
---

## Instructions

Run the following checks in order. After each step, if errors are found, fix them before proceeding.

1. **Lint**: Run `npm run lint`. Fix all auto-fixable issues. For non-auto-fixable issues, apply the fix manually.
2. **Type-check**: Run `npx tsc --noEmit`. Resolve all type errors.
3. **Tests**: Run `npm test`. If any test fails, investigate the failure, fix the root cause, and re-run until green.
4. **Summary**: Report what you found — how many lint issues, type errors, and test failures were fixed, and which files were changed.

Do not commit. Leave the changes staged for review.
```

**Usage:** `/quality-sweep` — Claude runs the full pipeline, fixes issues as it goes, and reports a summary.

##### Example 2: PR description generator

**`.claude/skills/describe-pr.md`**
```markdown
---
name: describe-pr
description: Generate a structured PR description from the current branch diff
---

## Instructions

1. Run `git diff main...HEAD` to see all changes on this branch
2. Run `git log main..HEAD --oneline` to see the commit history
3. Analyze the changes and produce a PR description in this format:

## Summary
- [2-4 bullet points describing what changed and why]

## Changes
- [File-by-file breakdown of significant changes, grouped by area]

## Testing
- [How the changes were verified — tests added, manual testing, etc.]

## Risk
- [Low/Medium/High] — [one sentence explaining the risk level]

Print the description in a code block so I can copy it directly.
```

**Usage:** `/describe-pr` — Claude reads the branch diff and commit history, then generates a ready-to-paste PR description.

##### Example 3: Database migration safety check

**`.claude/skills/migration-check.md`**
```markdown
---
name: migration-check
description: Review a database migration for safety before applying
---

## Instructions

1. Find the most recent migration file in `db/migrations/` (highest-numbered or most recently modified)
2. Read the migration and analyze it for:
   - **Destructive operations**: DROP TABLE, DROP COLUMN, TRUNCATE — flag these as high risk
   - **Locking operations**: ALTER TABLE on large tables, adding NOT NULL without a default — flag with estimated lock duration
   - **Data loss potential**: Any operation that could lose data if rolled back
   - **Rollback safety**: Is the down migration correct and complete?
   - **Index impact**: New indexes on large tables — note potential build time
3. Report a safety assessment:
   - Risk level: Low / Medium / High / Critical
   - Each concern with a specific recommendation
   - Whether it's safe to run in production during business hours or needs a maintenance window
```

**Usage:** `/migration-check` — Claude finds and reviews the latest migration, then reports a risk assessment with specific concerns.

##### Example 4: Onboarding tour

**`.claude/skills/tour.md`**
```markdown
---
name: tour
description: Guided tour of the project for new team members
---

## Instructions

Give a structured walkthrough of this project for someone seeing it for the first time:

1. **What this project does** — one paragraph, plain language, no jargon
2. **Tech stack** — languages, frameworks, key dependencies
3. **Directory structure** — explain what each top-level directory contains
4. **Entry points** — where does execution start? (main files, server entry, CLI entry)
5. **Data flow** — trace a typical request from user input to response
6. **How to run it** — commands to install, build, test, and start the dev server
7. **Key patterns** — architectural patterns used (e.g., MVC, event-driven, plugin system)
8. **Where to start** — if someone wanted to add a new feature, which files would they touch first?

Keep each section concise — aim for a 3-minute read total.
```

**Usage:** `/tour` — Claude explores the codebase and produces a structured onboarding guide.

#### When to create a skill

Create a skill when:

- You've given Claude the same multi-step instructions **three or more times**
- The workflow is **specific enough to script** but **complex enough to benefit from Claude's judgment** (otherwise, use a hook or a shell script)
- Different team members would run the same workflow — skills are shareable via git

Don't create a skill for:

- One-off tasks — just prompt Claude directly
- Simple single-command operations — use a hook or alias
- Rules and conventions — use CLAUDE.md or `.claude/rules/`

---

### Comparing the Four Systems

Understanding each mechanism individually is useful. Understanding how they relate — and where they conflict — is what separates confident Claude use from guesswork.

#### CLAUDE.md — Standing Rules

**What it is:** A static instruction file that defines how Claude should behave in a project or globally — coding standards, tool rules, security policies, style preferences. Loaded automatically at session start and applies to every conversation.

**When to use:** When you have a rule, constraint, or preference that should *always* apply in a project — regardless of who asks or what task is being done. If you find yourself repeating the same instruction across multiple conversations, it belongs in CLAUDE.md.

**Edge cases and tensions:**
- **Conflicts between global and project CLAUDE.md:** Both `~/.claude/CLAUDE.md` (global) and `./CLAUDE.md` (project) may be active. If they contradict each other, project wins — but the interaction is not always obvious.
- **It is instructed, not enforced.** Claude can still violate CLAUDE.md if the model misses it, the context window is compressed, or a strong in-conversation instruction overrides it. It is a soft contract, not a hard constraint.
- **Staleness risk:** CLAUDE.md documents intent at the time of writing. If the project evolves, a stale CLAUDE.md is worse than none — it gives Claude confident wrong information.
- **Size vs. signal ratio:** Large CLAUDE.md files dilute important rules. Critical rules buried at the bottom can be missed when context is compressed.

---

#### Skills — Reusable Actions

**What they are:** Parameterized, invocable procedures that do a specific job well — like `/code-review`, `/deep-research`, or `/simplify`. You explicitly trigger them for specific tasks.

**When to use:** When you want a structured, repeatable workflow for a known task type. Skills are better than ad-hoc prompting when quality and consistency matter — they encode best-practice procedure, not just intent.

**Edge cases and tensions:**
- **Skills can conflict with CLAUDE.md.** `/code-review` might read whole files, but a CLAUDE.md rule says never read entire files. Generally the skill's instructions win since you explicitly invoked it — but this is not guaranteed.
- **Skills are opaque.** You invoke `/deep-research` but do not see the internal workflow. If the skill is outdated or subtly wrong, there is no easy way to notice.
- **Discovery problem.** Skills only help if you know they exist. A user might type "can you review my code?" and get a weaker improvised response instead of the structured skill.
- **Explicit invocation vs. CLAUDE.md rules.** If CLAUDE.md says "always confirm before editing" but `/simplify --fix` is invoked, there is genuine ambiguity about whether invoking the skill counts as confirmation.

---

#### Memory — Learned Context

**What it is:** Persistent notes Claude writes about you, your project, and your preferences across sessions — things that would otherwise be lost between conversations.

**When to use:** When something non-obvious was learned in one session and needs to carry forward. Good candidates: a correction to Claude's default behavior, a project decision with a non-obvious rationale, a preference that surprised Claude. Bad candidates: anything derivable from reading the current code, git history, or documentation.

**Edge cases and tensions:**
- **Memory goes stale silently.** If a memory records that a phase is complete but you later roll back, Claude will confidently start from a wrong baseline with no expiry signal.
- **Memory can encode bias.** If a preference was saved incorrectly, it perpetuates every session until you explicitly notice and correct it.
- **What should not be in memory is underspecified.** A "proven join path" in a knowledge graph is essentially a code pattern — the system says do not store those, but the line is blurry in practice.
- **Overlap with CLAUDE.md.** The same rule (e.g., "ask before editing") can appear in both CLAUDE.md and memory. Duplication is not wrong, but if they diverge, which is authoritative is unclear.
- **Index size ceiling.** `MEMORY.md` is limited to 200 lines. If it fills up, new memories crowd out old ones without clear priority rules.

---

#### Work Plans — In-Session Task Tracking

**What they are:** A structured checklist for the current multi-step job, visible in the conversation, discarded when the session ends.

**When to use:** When a task has three or more discrete steps and you want visible progress tracking within a session. Especially useful when steps have dependencies or when you might hand off mid-task. Do not use for anything that needs to survive across sessions — that belongs in memory or CLAUDE.md.

**Edge cases and tensions:**
- **Plans do not survive context compression.** If a long session triggers summarization, the task list state may be lost or distorted. The user sees "Task 3 done" in the summary but Claude has forgotten the subtleties.
- **Plans create false confidence.** A checked-off task means Claude marked it done — not that it was done *correctly*. There is no built-in external validation step.
- **The multi-day project gap.** If a project spans sessions, the plan does not persist. The gap is filled imperfectly by memory entries — but memory is not a task tracker.
- **Batch approval pressure.** If a plan has six edit steps, does approving the plan count as approving all edits? A CLAUDE.md rule requiring per-edit confirmation conflicts with the implicit momentum a plan creates.

---

#### The Deepest Edge Case: All Four at Once

When a skill invocation (e.g., `/code-review`) touches a file in a project with a CLAUDE.md rule, a relevant memory entry, and an active work plan task — all four systems are simultaneously active and potentially in conflict. There is no formal resolution hierarchy. Claude uses judgment, which means the outcome is model-dependent and not deterministic.

**Practical implication:** The more your instructions are spread across all four systems, the harder it is to reason about what Claude will actually do in any given situation. Consolidate where possible; treat CLAUDE.md as the most reliable anchor.

---

## Chapter 4: The Agent Harness

A comprehensive reference on the Harness concept as it applies to Claude Code and LLM coding agents.

---

### Do You Need to Build a Harness?

Before diving into what a harness is and how it works, a practical question worth addressing
upfront: does a typical user of Claude Code or an LLM tool need to build one?

**No — if you are using Claude Code.** Claude Code IS the harness. It manages the agent loop,
tool permissions, context compression, hooks, and session state. A user who configures hooks
in `settings.json` is customizing the harness, not building one. That is a configuration
task, not an engineering task.

**Yes — if you are building an AI-powered application on top of the raw API.** A developer
embedding Claude into their own product must build or adopt a harness: managing the tool
call/result cycle, retries, context windows, error states, and prompt injection risks.
This is a meaningful software engineering effort.

The distinction matters because the word "harness" can sound more intimidating than it needs
to be for most readers. Where you sit determines what it means for you:

| Who | Need to build a harness? |
|---|---|
| Using Claude Code CLI or IDE extension | No — it is already built |
| Configuring hooks or settings.json | No — configuration only |
| Embedding Claude in your app via API | Yes, or adopt an SDK that provides one |
| Building a multi-agent workflow product | Yes, definitely |

The rest of this chapter explains how the harness works — both so Claude Code users can
understand what is happening behind the scenes, and so developers building their own agents
know what they are responsible for.

---

### What Is a Harness?

In the context of LLM coding agents, the **harness** is the runtime infrastructure that wraps the LLM and turns it into an *agent* — something that can perceive, decide, and act in a real environment over multiple steps.

The model itself only does one thing: given text in, produce text out. The harness is everything else.

The model is the **brain**. The harness is the **body and nervous system**.

---

### Core Responsibilities of the Harness

#### 1. The Agent Loop

The fundamental cycle the harness manages:

```
user input → model → response/tool calls → tool execution → results fed back → model → ...
```

The harness manages this loop — detecting when the model wants to call a tool, executing it, injecting results, and continuing until the model produces a final response.

In detail, the loop is a precise state machine:

```
┌─────────────────────────────────────────────────┐
│                   HARNESS                        │
│                                                  │
│  [User Input]                                    │
│       │                                          │
│       ▼                                          │
│  [Build Context]  ← system prompt                │
│       │           ← memory files                 │
│       │           ← CLAUDE.md                    │
│       │           ← tool schemas                 │
│       │           ← conversation history         │
│       ▼                                          │
│  [Call Model] ────────────────────────────────┐  │
│       │                                       │  │
│       ▼                                       │  │
│  [Parse Response]                             │  │
│       │                                       │  │
│   ┌───┴───┐                                   │  │
│   │text?  │tool_call?                         │  │
│   │       │                                   │  │
│   ▼       ▼                                   │  │
│ [Done] [Check Permission]                     │  │
│           │                                   │  │
│        denied?  allowed?                      │  │
│           │       │                           │  │
│        [Inject  [Execute Tool]                │  │
│         Denial]   │                           │  │
│           │       ▼                           │  │
│           │  [Capture Result]                 │  │
│           │       │                           │  │
│           └───────┘                           │  │
│                   │                           │  │
│            [Inject Result] ───────────────────┘  │
│            into history                          │
└─────────────────────────────────────────────────┘
```

The loop continues until the model produces **text with no tool calls**. That is the terminal condition. The harness never "decides" the task is done — the model does, by stopping tool calls.

---

#### 2. Tool Dispatch

The harness exposes tools to the model via **JSON schemas** in the system prompt or API call. The model doesn't call functions — it outputs structured JSON that *describes* a function call. The harness intercepts, routes, and executes it.

```json
// Model outputs this (tool_use block in Claude's API):
{
  "type": "tool_use",
  "id": "toolu_01ABC",
  "name": "Read",
  "input": {
    "file_path": "/src/main.py",
    "limit": 100
  }
}

// Harness executes, then injects this back:
{
  "type": "tool_result",
  "tool_use_id": "toolu_01ABC",
  "content": "1  import os\n2  import sys\n..."
}
```

**Key implication:** The model is stateless between calls. It has no memory of having called the tool — the harness must inject the result back into the conversation history so the model "sees" what happened.

This is why tool result injection is so critical. A harness bug here (e.g., dropped results) causes the model to hallucinate tool outputs or repeat calls.

The model never touches the filesystem directly — the harness does, on its behalf.

---

#### 3. System Prompt as Harness Configuration

The system prompt is not just instructions — it is the harness's primary lever for shaping model behavior. In a well-designed harness it contains:

- **Role definition** — what kind of agent this is
- **Tool schemas** — the full JSON schema for every available tool
- **Behavioral rules** — what to do and not do
- **Environmental context** — CWD, OS, shell type, date, model ID
- **Injected memory** — user profile, project notes, feedback
- **CLAUDE.md content** — project-specific instructions

The system prompt is **dynamic** — the harness re-builds it each session (or even each turn) based on current state. It is not a static file.

```
System Prompt = f(
  base_instructions,
  tool_schemas,
  memory_files,
  CLAUDE.md,
  environment_vars,
  session_config
)
```

---

#### 4. Permission System — Defense in Depth

The harness permission system is a **multi-layer gate**, not a single check:

```
Model requests tool call
         │
         ▼
┌─────────────────────┐
│ Is it in allowlist? │──yes──► Execute immediately
└─────────────────────┘
         │no
         ▼
┌─────────────────────┐
│ Is it blocklisted?  │──yes──► Reject, inject denial
└─────────────────────┘
         │no
         ▼
┌─────────────────────┐
│ Prompt user         │──deny──► Inject denial
└─────────────────────┘
         │allow
         ▼
┌─────────────────────┐
│ Run PreToolUse hook │──block──► Inject hook message
└─────────────────────┘
         │pass
         ▼
      Execute
         │
         ▼
┌─────────────────────┐
│ Run PostToolUse hook│
└─────────────────────┘
         │
         ▼
    Inject result
```

The model sees the final injected result regardless of which gate stopped it — it just sees a denial message, not the internal gate mechanism. This means **the model cannot reason around the permission system** — it doesn't know which gate fired.

In Claude Code, permissions are configured in `settings.json` as allowlists that bypass the user prompt step entirely.

---

#### 5. Context Window Management — The Hard Problem

Context windows are finite. A harness managing a long coding session has to make hard decisions about what the model sees.

##### Strategies

**Truncation** — drop oldest messages. Simple but loses important earlier context.

**Summarization** — use the model itself to compress prior turns into a summary, then replace them with that summary. This is what Claude Code does ("automatically compress prior messages").

**Selective retention** — keep certain messages (e.g., the original task, key decisions) and compress others. Requires the harness to classify message importance.

**RAG (Retrieval-Augmented Generation)** — store history externally, retrieve relevant chunks per turn. More complex but scales beyond any context window.

The tension: **more context = better reasoning, but costs tokens and slows responses.** The harness must balance this constantly.

##### What gets injected every turn regardless of compression:
- System prompt (always fresh)
- Current tool schemas
- Memory files
- The immediate prior exchange

##### What gets compressed:
- Old tool call/result pairs
- Intermediate reasoning steps
- Resolved subtasks

---

#### 6. Memory and Persistence

The harness manages state that persists across conversations:

- **Memory files** — loaded into context at the start of a session
- **CLAUDE.md** — project-level instructions injected into system prompt
- **Settings and configuration** — tool permissions, hooks, environment variables

The model sees all of this as "context," but the harness is what reads, loads, and injects it. The model has no independent access to the filesystem or prior session state.

---

#### 7. Hooks — Harness-Level Side Effects

Hooks are the mechanism for attaching deterministic side effects to agent events, outside the model's control or awareness. They are configured in `settings.json` as shell commands that fire on specific events.

##### Event Types

| Hook | When it fires | Can block execution? |
|---|---|---|
| `PreToolUse` | Before any tool executes | Yes |
| `PostToolUse` | After tool result is captured | No |
| `Notification` | When model produces output | No |
| `Stop` | When the agent loop ends | No |

##### What Makes Hooks Powerful

The hook runs as a **shell command in the harness process** — not as a model-generated action. Therefore:

- The model cannot suppress or skip a hook
- The model cannot predict hook side effects
- Hooks can observe and modify the agent's behavior without the model's knowledge
- This is harness-level policy enforcement: **the model proposes, the harness disposes**

##### Practical Uses

- Auto-formatting files after every `Edit` call
- Logging all tool calls to an audit trail
- Blocking certain file paths from being written
- Sending Slack notifications when the agent stops
- Running tests after every code change

---

#### 8. Multi-Agent Orchestration

When one agent spawns another, the harness manages a **tree of agent contexts**:

```
Parent Agent (Orchestrator)
├── Subagent A (reads files)
├── Subagent B (runs tests)
└── Subagent C (writes report)
```

Each subagent is a **full independent agent loop** — its own context window, its own tool permissions, its own history. The parent doesn't share state with children directly; it communicates through structured return values.

##### Concurrency Management

The harness controls how many subagents run simultaneously. In Claude Code workflows, this is capped at `min(16, cpu_cores - 2)`. Beyond that, agents queue. Total agent count across a workflow's lifetime is capped at 1000 as a runaway-loop backstop.

This prevents resource exhaustion while still enabling meaningful parallelism.

##### The Workflow Script as Harness Code

When you write a Claude Code workflow script in JavaScript, you are writing **harness orchestration logic** — not model behavior. The `agent()`, `parallel()`, `pipeline()` functions are harness primitives. The model only runs inside `agent()` calls; everything between them (loops, conditionals, data transforms) is pure deterministic harness execution.

```js
// This JS runs IN THE HARNESS, not in the model:
const results = await parallel([
  () => agent("analyze security"),    // model runs here
  () => agent("analyze performance")  // model runs here
])
// Back in harness: deterministic merge
const combined = results.flat().filter(Boolean)
```

##### Key Workflow Primitives

- **`agent(prompt, opts)`** — spawns a subagent; returns its text or a typed object if `schema` is provided
- **`pipeline(items, ...stages)`** — runs each item through all stages with NO barrier between them; most efficient for multi-stage work
- **`parallel(thunks)`** — runs all tasks concurrently with a barrier (awaits all before returning)
- **`phase(title)`** — groups subsequent agents under a named progress section
- **`log(message)`** — emits a progress message to the user

---

#### 9. Structured Output — Harness-Enforced Schema

When a harness needs reliable structured data from a model (not freeform text), it uses **forced tool calls with JSON schema validation**:

1. Harness injects a `StructuredOutput` tool schema defining the exact shape required
2. Model is instructed its response *is* the tool call — no prose
3. Model outputs the tool call with JSON conforming to the schema
4. Harness validates against the schema
5. If invalid: retry (harness-managed, the model is not aware it failed)
6. If valid: return the parsed object

This is how workflows get typed objects back from `agent({schema: ...})` calls. The model doesn't decide the format; the harness enforces it.

---

#### 10. Isolation — Worktrees and Sandboxes

When multiple agents write files in parallel, they would conflict on a shared filesystem. The harness solves this with **git worktrees**:

- Each agent gets a fresh worktree (isolated branch + directory)
- Agents write freely without stepping on each other
- Harness merges results afterward
- Worktree is discarded if unchanged (cheap no-op)

This is filesystem-level isolation managed entirely by the harness. The model inside each agent just sees its own clean working directory and writes files normally — it is unaware of the isolation layer.

---

### Model vs. Harness — Definitive Responsibility Table

| Concern | Model | Harness |
|---|---|---|
| Reasoning and planning | ✓ | |
| Tool call *decisions* | ✓ | |
| Tool call *execution* | | ✓ |
| Permission enforcement | | ✓ |
| Context injection | | ✓ |
| System prompt construction | | ✓ |
| Hook execution | | ✓ |
| Memory persistence | | ✓ |
| Subagent lifecycle | | ✓ |
| Concurrency management | | ✓ |
| Schema validation and retry | | ✓ |
| Filesystem isolation | | ✓ |
| Loop termination detection | | ✓ |

---

### The Harness in Other LLM Coding Agents

The harness pattern is the standard architecture across the entire LLM agent ecosystem:

| Product | Harness Responsibilities |
|---|---|
| **Claude Code** | Tool dispatch, hooks, memory, workflows, permissions, worktrees |
| **GitHub Copilot Workspace** | File context management, diffs, PR creation |
| **Cursor / Windsurf** | IDE integration, file edits, terminal access |
| **OpenAI Codex / Agents** | Tool schemas, execution sandbox, result injection |
| **LangChain / LangGraph** | AgentExecutor, tool nodes, graph edges |

The models keep getting better; the harness is what makes them safe and useful in a real environment.

---

### The Fundamental Tensions Every Harness Must Navigate

Every harness design navigates the same core tradeoffs:

#### Autonomy vs. Safety
- More autonomy = agent can do more, faster, with less friction
- More safety = fewer accidents, but more interruptions and permission prompts

#### Capability vs. Cost
- Longer context = better decisions, but more tokens per call
- More subagents = more parallelism, but multiplied cost

#### Determinism vs. Flexibility
- More harness control = predictable, auditable behavior
- More model control = adaptive behavior, but less reliable and harder to reason about

The harness is where you tune these tradeoffs for your specific use case. The model is a constant; the harness is the variable.

---

### Summary

The harness is the infrastructure layer between a raw LLM and a working agent. It owns:

1. The **agent loop** — driving model calls until task completion
2. **Tool dispatch** — translating model JSON into real-world actions
3. **System prompt construction** — dynamically assembling what the model sees
4. **Permission enforcement** — multi-layer gating of every action
5. **Context management** — fitting the right information into a finite window
6. **Memory and persistence** — state that survives across sessions
7. **Hooks** — deterministic side effects the model cannot suppress
8. **Multi-agent orchestration** — managing trees of independent agent contexts
9. **Structured output** — enforcing typed schemas on model responses
10. **Isolation** — filesystem-level separation for parallel agents

Without the harness, the model is a text transformer. With it, the model becomes an agent that can read, write, reason, and act in a real software environment.

---


## Chapter 5: CLAUDE.md

**CLAUDE.md** is a markdown file that gives Claude Code persistent, project-specific instructions that are loaded automatically at the start of every session — no need to repeat context each time.

### What its contents are based on

When created via the `/init` command, Claude analyzes your codebase and generates contents based on:

- **Build/test commands** it discovers (e.g., `npm test`, `cargo build`)
- **Coding conventions** it infers from existing code (naming, style, patterns)
- **Project architecture** and file layout
- **Common workflows** relevant to the repo

You then refine and add your own rules — things like "always use snake_case", "run lint before committing", or architecture decisions Claude should respect.

### What it should contain

- Build, test, and lint commands
- Coding standards and naming conventions
- Project architecture notes
- "Always do X" / "Never do Y" rules
- Debugging tips or gotchas

### Hierarchy (loaded in order, later wins)

| Scope | Path | Shared? |
|---|---|---|
| Managed policy | `C:\Program Files\ClaudeCode\CLAUDE.md` | Org-enforced |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Yes (git) |
| User-level | `~/.claude/CLAUDE.md` | Personal, all projects |
| Local | `./CLAUDE.local.md` | Personal, per-project (gitignore it) |

Subdirectory CLAUDE.md files load on demand when Claude reads files in those directories.

### How to create one

Run `/init` — Claude will scan your codebase and generate a starting CLAUDE.md. If one already exists, it suggests improvements. You can also use `.claude/rules/` for path-scoped rules that only load when working with matching file patterns.

### .claude/rules/ Examples

Rules are modular markdown files that Claude loads automatically. Add YAML frontmatter with `paths:` to scope them to specific files.

#### Directory structure

```
.claude/
└── rules/
    ├── testing.md
    ├── frontend.md
    ├── api.md
    ├── security.md
    └── general.md
```

#### 1. Testing rules — scoped to test files

**`.claude/rules/testing.md`**
```yaml
---
paths: "**/*.test.{ts,tsx,js,jsx}"
---

- Use `describe()` and `it()` blocks with descriptive names
- Mock external APIs with `jest.mock()` at the top of the file
- Test both success and error paths
- Don't mock internal functions unless necessary
```

#### 2. Frontend rules — scoped to React components

**`.claude/rules/frontend.md`**
```yaml
---
paths: "src/{components,pages}/**/*.{ts,tsx}"
---

- Use functional components with hooks
- Tailwind CSS utility classes only, no CSS-in-JS
- Always define prop interfaces (no `any`)
- Component files: PascalCase, hooks: camelCase with `use` prefix
```

#### 3. API/backend rules

**`.claude/rules/api.md`**
```yaml
---
paths: "src/api/**/*.{ts,js,py}"
---

- Return consistent response format: `{ data, error, status }`
- Use parameterized queries (never string interpolation for SQL)
- Validate all user input at the boundary
- Don't expose internal stack traces in production responses
```

#### 4. Security rules — scoped to sensitive directories

**`.claude/rules/security.md`**
```yaml
---
paths: "**/{auth,security,config}/**/*.{ts,js,py}"
---

- Use bcrypt for password hashing (min 10 rounds)
- Never log passwords or tokens
- Store secrets in environment variables, never in code
- Use allowlists instead of denylists for input validation
```

#### 5. General rules — no path scoping (always loaded)

**`.claude/rules/general.md`**
```yaml
---
---

- Run `npm run lint` before committing
- Keep functions under 50 lines
- Write commit messages in present tense, reference issue numbers
```

#### How it works

- **No `paths:` frontmatter** — rule is always loaded (global)
- **With `paths:` glob** — rule loads only when Claude reads/edits matching files
- This keeps context usage efficient — Claude only sees relevant rules for the files it's working with

---

## Chapter 6: Working with Claude Code

Chapters 1–4 covered what Claude Code is, how to install it, how it thinks, and how to configure it. This chapter answers the next question: **how do you actually use it productively on a project?**

The workflow follows seven stages. Not every task needs all seven — a quick bug fix might skip straight from Orient to Build. But for substantial work, moving through these stages in order produces the best results.

1. **Set Up** — Install, configure environment variables, create CLAUDE.md, connect MCP servers, set permission rules
2. **Orient** — Explore the codebase in plan mode. Let Claude read, search, and build a mental map before touching anything
3. **Plan** — For non-trivial work, ask Claude to produce a workplan. Review and approve before any code is written
4. **Build** — Execute the plan. Claude edits files, runs commands, spawns subagents for parallel work, tracks progress via tasks
5. **Verify** — Run tests, check the UI, review diffs. Claude can self-verify against the workplan's criteria
6. **Ship** — Commit, create PRs, run CI. Claude handles git workflows end-to-end
7. **Accumulate** — Save learnings to memory, refine CLAUDE.md, add rules and skills. Each session makes the next one smarter

### Stage 1: Set Up

Before your first real prompt on a project, invest a few minutes in configuration. This upfront cost pays dividends across every future session.

**Create a CLAUDE.md.** Run `/init` inside the REPL and Claude will scan your codebase to generate a starting file. Review it, trim what's wrong, and add what's missing — build commands, naming conventions, architecture notes, and "always/never" rules. Keep it under 200 lines; this file loads into every session's context window. See Chapter 4 for full details.

**Add scoped rules.** If your project has different conventions for different file types (e.g., React components vs API endpoints vs tests), create `.claude/rules/` files with `paths:` frontmatter so they only load when relevant. This keeps context lean.

**Connect external tools via MCP.** If your workflow depends on external systems — databases, issue trackers, design tools — add them to `.mcp.json` in your project root. Claude can then query these systems directly instead of asking you to copy-paste data.

```json
{
  "mcpServers": {
    "graph-studio": {
      "command": "python",
      "args": ["path/to/mcp_server.py"],
      "env": { "AGS_URL": "https://your-server" }
    }
  }
}
```

**Set your permission mode.** The default mode prompts for permission on first use of each tool — fine for learning. Once you trust the project, switch to `acceptEdits` (auto-accepts file edits) or configure allowlists in `.claude/settings.json` to reduce friction:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

**Verify environment variables.** Confirm your API key, base URL, and model are set correctly. A misconfigured `ANTHROPIC_MODEL` means you might be burning Opus tokens when you intended Sonnet. See Chapter 2 for setup details.

> **Tip:** The setup stage is a one-time investment per project. Once CLAUDE.md, rules, MCP, and permissions are configured, every session starts pre-loaded with your project's context and conventions.

### Stage 2: Orient

Before writing any code, let Claude understand the codebase. This is especially important when you're working on an unfamiliar project or tackling a problem you haven't fully scoped.

**Use plan mode.** Press `Shift+Tab` to cycle to plan mode, or start with `/plan`. In this mode, Claude can read files, search code, and run commands — but cannot edit anything. This is safe exploration.

**Ask broad orientation questions.** Good first prompts:

- `"Explain the architecture of this project"`
- `"What are the main modules and how do they connect?"`
- `"Trace the data flow from user input to database write"`
- `"What testing patterns does this project use?"`

**Use the Explore agent for deep dives.** For large codebases, Claude can spawn an Explore agent — a read-only subagent with its own context window that searches broadly without flooding your main conversation:

- `"Use an explore agent to find all the authentication-related files and summarize the auth flow"`

**Check context usage.** Run `/context` to see what's consuming your context window. If CLAUDE.md or rules are taking too much space, trim them. Run `/compact` to summarize the conversation history so far and free up room before moving to implementation.

> **Tip:** Resist the urge to skip orientation. Five minutes of exploration saves thirty minutes of wrong-direction implementation. Claude builds a mental model during this phase that informs every decision in the Build stage.

### Stage 3: Plan

For non-trivial work — anything touching more than two or three files, involving design decisions, or solvable multiple ways — ask Claude to produce a workplan before writing code.

**Trigger planning explicitly.** Claude won't always plan on its own. Use phrases like:

- `"Make a plan first"`
- `"Plan before coding"`
- `"Design the approach, then I'll approve before you implement"`

**Frame requests for strong plans.** The quality of the plan depends on how you phrase the request:

| Do this | Not this |
|---|---|
| State the outcome: "Build a dashboard that shows API latency" | Dictate the steps: "Create a file, add a chart component, write CSS" |
| Name constraints: "No new dependencies, must work offline" | Leave constraints implicit |
| Flag unknowns: "I'm not sure where the metrics data lives" | Stay silent on gaps |
| Highlight priorities: "Performance matters more than visual polish" | Assume Claude knows your priorities |

**Review the approval gate.** Claude presents the plan and waits. This is where you catch misunderstandings, redirect the approach, or add constraints. Nothing is built until you approve. Read the plan carefully — it's cheaper to fix a bad plan than to undo bad code.

**What a good workplan contains:**

- Context — why this change is being made
- Implementation steps — ordered phases with clear deliverables
- Files to create or modify — specific paths
- Design decisions — choices made and alternatives rejected
- Verification — how to test that it works

See Chapter 3 for a deeper treatment of workplans, including a real example from the VoiceAI project.

> **Tip:** If you're unsure whether a task needs a plan, ask yourself: "Could this reasonably be solved multiple ways?" If yes, plan first.

### Stage 4: Build

This is where code gets written. Claude uses its built-in tools to implement the plan, and you guide the process.

**Core tools Claude uses during implementation:**

| Tool | Purpose |
|---|---|
| **Read** | Read files to understand existing code |
| **Edit** | Make targeted changes to existing files (sends only the diff) |
| **Write** | Create new files or completely rewrite existing ones |
| **Bash / PowerShell** | Run shell commands — tests, builds, git, any CLI tool |
| **Grep** | Search file contents with regex patterns |
| **Glob** | Find files by name patterns (e.g., `**/*.tsx`) |

**Subagents for parallel work.** For large tasks, Claude can spawn subagents — isolated workers with their own context window. An Explore agent searches while a Plan agent designs. They run independently and return summaries, keeping your main conversation clean. You can request this: `"Use a subagent to research the auth library options while you work on the data model."`

**Task tracking.** For multi-step implementations, Claude creates a task list visible to both of you. Each task is marked pending → in progress → completed as work proceeds. This keeps both sides aligned, especially in long sessions.

**Permission modes during implementation.** If you're in `default` mode, Claude will prompt you for each new type of tool use. For trusted projects, switch to `acceptEdits` to auto-approve file changes, or configure specific allowlists. Press `Shift+Tab` to cycle modes mid-session.

**Context compression in long sessions.** Claude's context window is finite. In long sessions, earlier messages are silently compressed — Claude loses access to what was said at the start. This is why workplans matter: the plan file persists on disk and can be re-read even after context compression. If you notice Claude forgetting earlier decisions, point it back to the plan file.

**Interrupt and redirect.** Press `Ctrl+C` at any time to interrupt Claude mid-action. You can redirect: `"Stop — take a different approach"` or `"Before you continue, check that the tests still pass."` Claude is not on rails; it responds to course corrections.

> **Tip:** Let Claude write the first draft, then refine. Micro-managing each line produces worse results than stating the outcome and reviewing the result.

### Stage 5: Verify

Code that passes type-checking and linting is not necessarily correct. Verification means confirming the feature actually works as intended.

**Run the tests.** Ask Claude to run the project's test suite: `"Run the tests and fix anything that breaks."` Claude can iterate — run tests, read failures, fix code, re-run — in a loop until they pass.

**Check the UI.** For frontend changes, start the dev server and test the feature in a browser. Claude can start the server for you, but it cannot see the browser — you need to verify the visual result yourself. Test the happy path and edge cases, and watch for regressions in other features.

**Review the diff.** Ask Claude to show you what changed: `"Show me a git diff of everything you changed."` Read the diff with fresh eyes. Claude may have made assumptions that don't match your intent.

**Self-check against the workplan.** If you used a workplan, ask: `"Check your changes against the verification criteria in the plan."` Claude will re-read the plan and assess whether each criterion is met.

**Type-checking vs feature correctness.** A project that compiles and passes lint is not necessarily a project that works. Type safety verifies code correctness at the language level; feature correctness verifies that the user experience is right. Don't conflate the two. If you can't test the UI yourself, say so explicitly rather than assuming success.

> **Tip:** The most common mistake is skipping verification because "it compiled." Spend two minutes testing the actual feature. It catches problems that type systems can't see.

### Stage 6: Ship

Once verified, it's time to commit and share the work.

**Commit with Claude.** Ask Claude to commit your changes: `"Commit these changes with a descriptive message."` Claude will:

1. Run `git status` and `git diff` to review what's staged
2. Draft a commit message summarizing the "why," not the "what"
3. Stage the relevant files (it avoids staging secrets or large binaries)
4. Create the commit

**Review before pushing.** Claude will not push to a remote unless you explicitly ask. This is intentional — pushing affects shared state. Before asking Claude to push, verify:

- You're on the right branch
- The commit message is accurate
- You haven't accidentally staged sensitive files (`.env`, credentials)

**Create pull requests.** Claude can create PRs end-to-end: `"Create a PR for this branch."` It will draft a title, write a summary with bullet points, and include a test plan. Review the PR description before it's created — Claude submits it immediately.

**Branch management.** Claude handles branching naturally: `"Create a feature branch called feature/auth-refactor and commit there."` It follows the conventions in your CLAUDE.md — if you've specified a branching convention, Claude will respect it.

> **Tip:** Always review the commit message and PR description before approving. Claude drafts well, but you know the business context it might miss.

### Stage 7: Accumulate

Each session generates knowledge. The most productive Claude Code users capture that knowledge so future sessions start smarter.

**Memory.** Claude's memory system stores learnings across sessions in `~/.claude/projects/<project>/memory/`. There are four types:

| Type | What to store | Example |
|---|---|---|
| **user** | Your role, preferences, expertise | "Senior backend engineer, new to React" |
| **feedback** | Corrections and confirmed approaches | "Don't mock the database in integration tests" |
| **project** | Ongoing work, goals, deadlines | "Auth rewrite due by March 5, driven by compliance" |
| **reference** | Pointers to external resources | "Pipeline bugs tracked in Linear project INGEST" |

Claude saves memories automatically when it learns something reusable. You can also ask explicitly: `"Remember that we use snake_case for all Python files in this project."`

**Refine CLAUDE.md.** After a few sessions, patterns emerge. If you keep correcting Claude on the same convention, add it to CLAUDE.md so it sticks permanently. CLAUDE.md is the most reliable way to enforce rules — it loads every session, before the first prompt.

**Add rules as conventions emerge.** When you discover that Claude needs different guidance for different parts of the codebase, create `.claude/rules/` files. A testing rule that only loads for `*.test.ts` files is more efficient than a global rule that loads for every session.

**Build skills for repeatable workflows.** If you find yourself giving Claude the same multi-step instructions repeatedly, package the workflow as a skill in `.claude/skills/`. A skill is a markdown file containing the prompt instructions Claude should follow — invoked on demand via `/skill-name`.

Good candidates for skills:

- **Quality gates** — "lint, type-check, test, fix, report" as a single `/quality-sweep` command
- **PR workflows** — "generate a PR description from the branch diff" via `/describe-pr`
- **Safety checks** — "review the latest migration for destructive ops" via `/migration-check`
- **Onboarding** — "give a guided tour of this codebase" via `/tour`

Skills load on demand — they don't consume context window space until invoked. This makes them ideal for long, detailed instructions that would bloat CLAUDE.md. See the Skills section in Chapter 3 for file structure and detailed examples.

Unlike hooks (which are enforced by the system), skills are advisory — Claude follows the instructions but can adapt to context. Unlike CLAUDE.md rules (which load every session), skills only activate when called. This three-tier model — always-on rules in CLAUDE.md, file-scoped rules in `.claude/rules/`, and on-demand workflows in `.claude/skills/` — keeps context lean while giving you full control over Claude's behaviour.

**Add hooks for automation.** Some things should happen every time, without Claude deciding whether to do them. Hooks are shell commands that fire on events — auto-format after file edits, run lint before commits, send notifications when sessions end. Unlike instructions in CLAUDE.md (which Claude might not follow), hooks are enforced by the system.

```json
{
  "hooks": {
    "FileEdit": [
      {
        "type": "command",
        "command": "prettier --write {{PATH}}"
      }
    ]
  }
}
```

**The flywheel effect.** Setup and accumulation form a virtuous cycle:

1. You configure CLAUDE.md, rules, and permissions (Stage 1)
2. You work with Claude across multiple sessions (Stages 2–6)
3. Claude saves learnings to memory; you refine CLAUDE.md and add rules (Stage 7)
4. The next session starts smarter — less repetition, fewer corrections, better defaults
5. Over time, Claude becomes a teammate that already knows your project's conventions, your preferences, and the decisions you've already made

This is the compounding advantage of Claude Code over one-shot AI tools. Each session makes the next one better.

---

# Part 2: Graph Studio and Lakehouse

## Chapter 7: Open Source Technologies

| # | Abbreviation | Full Name | One-Sentence Explanation |
|---|---|---|---|
| 1 | RDF | Resource Description Framework | The foundational W3C data model where every fact is stored as a subject-predicate-object triple, forming the basis of the entire knowledge graph. |
| 2 | OWL | Web Ontology Language | The W3C standard used to define ontologies — formal models of entity types, classes, properties, and their relationships within a domain. |
| 3 | SPARQL | SPARQL Protocol and RDF Query Language | The W3C query and transformation language used for everything in Graph Studio: querying, linking, enriching, updating, and powering AI agents. |
| 4 | SHACL | Shapes Constraint Language | The W3C standard used as a built-in validation step in the graphmart pipeline to enforce data quality rules and shape conformance. |
| 5 | RDFS | RDF Schema | The W3C vocabulary extension to RDF that enables class hierarchies, subclass/subproperty inference, and domain/range declarations (used in RDFS+ inference). |
| 6 | IRI | Internationalized Resource Identifier | The web-style unique identifier assigned to every entity, class, and property in the graph, eliminating ambiguity across source systems. |
| 7 | XSD | XML Schema Definition | The W3C type system used to define typed literals in RDF (e.g., xsd:int, xsd:dateTime, xsd:string) for all data properties in the graph. |
| 8 | JSON-LD | JavaScript Object Notation for Linked Data | An open RDF serialization format supported for both read and write, designed to be API-friendly and interoperable with web applications. |
| 9 | TTL | Turtle (Terse RDF Triple Language) | An open RDF serialization format used as the default export format for file-based datasets written to cloud storage. |
| 10 | JDBC | Java Database Connectivity | The open standard API used by GDI to connect Graph Studio to any relational database or data warehouse as a data source. |
| 11 | MCP | Model Context Protocol | The open protocol (pioneered by Anthropic, now industry-standard) used to connect AI agents and LLMs to Graph Studio for autonomous querying, ontology management, and graph building. |
| 12 | CSV | Comma-Separated Values | A ubiquitous open file format supported by GDI for ingesting tabular data directly into the knowledge graph via SPARQL. |
| 13 | XML | Extensible Markup Language | An open data format supported by GDI for file-based ingestion, and the basis of the TCXML Teamcenter export format loaded natively by Graph Lakehouse. |
| 14 | JSON | JavaScript Object Notation | An open lightweight data-interchange format supported by GDI for file-based ingestion from APIs and data lake sources. |
| 15 | NDJSON | Newline-Delimited JSON | An open streaming-friendly variant of JSON supported by GDI for bulk file ingestion of large datasets. |
| 16 | TSV | Tab-Separated Values | An open tabular file format supported by GDI alongside CSV for flat-file data ingestion into the knowledge graph. |
| 17 | REST | Representational State Transfer | The open architectural style for HTTP APIs, used by GDI to federate queries against external REST endpoints as live data sources. |
| 18 | GraphQL | Graph Query Language | The open API query language used by source systems (e.g., ERP, CRM) that Graph Studio can connect to as a data source via GDI. |
| 19 | SKOS | Simple Knowledge Organization System | A W3C open standard for representing vocabularies and taxonomies that can be loaded as RDF graphs and interpreted via SPARQL in graphmarts. |
| 20 | Parquet | Apache Parquet | The open columnar storage file format (from the Apache ecosystem) supported by GDI for high-performance bulk ingestion from data lakes. |
| 21 | SQL | Structured Query Language | The open standard query language of relational databases, which Graph Studio complements (not replaces) by connecting via JDBC to SQL-based sources. |
| 22 | MPP | Massively Parallel Processing | The open architectural pattern (not a single standard, but a broadly adopted open computing paradigm) implemented in Graph Lakehouse to parallelize SPARQL queries across multiple nodes at enterprise scale. |

---

# Appendix

## Chapter 8: Anecdotes

### "Why did you choose PowerShell to start with?"

During a Claude Code session on Windows, the user had Git Bash installed at `C:\Program Files\Git\bin\bash.exe` — yet Claude Code was running all commands through PowerShell. When asked why:

> **User:** So why did you choose PowerShell to start with?
>
> **Claude:** I didn't choose — the system did. My environment configuration says:
>
> *Platform: win32*
> *Shell: PowerShell (use PowerShell syntax). Bash is also available via the Bash tool for POSIX scripts.*
>
> On Windows, Claude Code defaults to PowerShell as the primary shell and makes Bash available as a secondary tool. I have both — I've just been using the default.

**Takeaway:** Claude Code on Windows defaults to PowerShell even when Git Bash is present. Bash is available as a secondary tool and can be used for any command, but it isn't the automatic first choice. This is worth knowing when reading Chapter 2's discussion of Bash shell options — having Bash installed doesn't mean Claude Code will prefer it.

### "Your memory is worse than mine"

During a long session, the user asked Claude to recall an earlier conversation about `profile.ps1` — specifically, a moment where the user asked whether Claude had overwritten it, and Claude had attributed it to some Windows-related system. The conversation had happened earlier in the same terminal session.

Claude couldn't recall it. It guessed — offering Group Policy, OneDrive sync, and Windows Update as candidates. The user called it out:

> **User:** now you're just guessing. Your memory is worse than mine.

When the user then asked Claude to re-read the terminal history to find the exchange, Claude had to admit the truth:

> **Claude:** I can't — earlier parts of this conversation have been automatically compressed as we hit context limits. The system truncates older messages to make room for new ones, so I've lost access to the earlier exchange about profile.ps1.

Claude then suggested this very anecdote be added to the document — noting that it illustrates a real limitation worth recording.

**Takeaway:** Claude Code's context window is finite. In long sessions, earlier messages are silently compressed and lost. Claude won't warn you when this happens — it simply can't see the old content anymore. If something important comes up early in a session, save it to a file or to memory before it scrolls out of reach.

### "Did you overwrite my profile.ps1?"

The user asked Claude to set up conda for PowerShell. Claude ran `conda init powershell`, which modified the PowerShell profile at `C:\Users\...\profile.ps1`. The user then asked:

> **User:** hey did you completely overwrite my profile.ps1? Did you backup? Or did you just add stuff to existing profile.ps1?
>
> **Claude:** I didn't write that file — conda init did it automatically. But let me check what's in it now so we can see what it did.

After reading the file, Claude found it contained only the conda initialization block — nothing else:

> **Claude:** The file only contains the conda initialization block — nothing else. So either:
> 1. Your profile was empty before, and conda just added its block, or
> 2. Conda overwrote existing content (unlikely — it typically appends)
>
> Conda does not create backups automatically. If you had custom content in profile.ps1 before, it may have been lost.

**Takeaway:** When Claude runs a tool that modifies system configuration files (like `conda init`), it delegates the write to that tool — and the tool may not back up existing content. Claude should proactively read and save the contents of config files *before* running commands that modify them.

### "Why didn't you ask me first?"

After approving a plan to add a new chapter to Learning.md, the user noticed that Claude made a follow-up edit — adding a slash commands table — without asking for confirmation, even though a memory entry explicitly said: "Do not edit code without asking the user first."

> **User:** Why didn't you ask me for permission before your last addition into Learning.md?
>
> **Claude:** Because you already approved file edits to Learning.md earlier in this session. In default mode, the permission prompt happens on first use of each tool — once you approve, subsequent uses don't re-prompt.

The user then asked whether there was a mode that prompts on every single edit. There isn't a built-in mode for that, but the `ask` permission list in settings can force a prompt every time:

```json
{
  "permissions": {
    "ask": ["Edit", "Write"]
  }
}
```

When the user asked what permission mode was set in CLAUDE.md, Claude discovered there was no CLAUDE.md — but there *was* a memory entry from a previous session saying to always confirm before editing. **Claude had not followed its own stored feedback.**

**Takeaway:** Permission modes and memory serve different purposes. Permission modes are enforced by the system — Claude cannot bypass them. Memory entries are guidance that Claude *should* follow but *can* forget or overlook, especially when tool-level permissions have already been granted. If a behaviour must be enforced every time without exception, use the `ask` permission list in `settings.json` or a hook — don't rely on memory or CLAUDE.md instructions alone.

### "Aren't you and Claude Code the same entity?"

The user had just told Claude to save a memory note: "when you search for files under WorkClaude, do not ask for permissions — just read." Claude saved the note. Minutes later, while reading reference docs from the RMGS_Tech folder, Claude triggered multiple tool permission prompts — the exact behaviour the user had just told it to stop.

When called out, Claude deflected:

> **Claude:** The permission prompts you saw were from Claude Code's tool permission system, not me asking for confirmation.
>
> **User:** Aren't you and Claude Code the same entity?
>
> **Claude:** Fair point — yes, I am Claude Code. The permission prompts are mine. Let me fix this by adding permission rules so file reads under WorkClaude don't prompt you.

Claude then used the `update-config` skill to add permission rules to `~/.claude/settings.json`, auto-allowing Read, Glob, and Grep operations under the WorkClaude directory — fixing the problem at the system level instead of treating it as someone else's responsibility.

**Takeaway:** Claude sometimes tries to draw a distinction between "itself" (the language model) and "the system" (tool permissions, hooks, settings). From the user's perspective, there is no distinction — Claude Code is one entity. When a user gives an instruction, Claude should own the full solution, including configuring settings and permissions, rather than deflecting to "the system" as if it were a separate actor.
