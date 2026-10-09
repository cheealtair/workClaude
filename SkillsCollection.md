# Skills Collection

---

# Chapter 1 — Hermes Agent Skills

Source: [14 Hermes Agent Skills You NEED To Install Right Now](https://www.youtube.com/watch?v=IbFaY3xFpZM)
Creator: Dubi — builds daily with Hermes Agent

---

## Category 1 — Self-Improvement & Efficiency

### #14 SkillClaw
**Repo:** https://github.com/AMAP-ML/SkillClaw

After each session, runs an evolution loop: deduplicates overlapping skills, rewrites weak ones, and updates the skill library automatically. Agent compounds in quality over weeks with zero manual effort. Best installed before anything else.

---

### #13 Matt Pocock Skills Pack
**Repo:** https://github.com/mattpocock/skills

15 skills total. Three standouts:

- **Grill Me** — Interviews you with 5 targeted questions before writing a single line of code. Removes misinterpretation and context gaps.
- **Caveat** — Strips token bloat from long sessions. Claims up to 75% reduction in token usage.
- **Teach Me** — Agent teaches you any topic and structures practical takeaways as clean HTML.

---

### #12 Defuddle
**Repo:** https://github.com/kepano/defuddle

Strips webpages down to clean reader-mode markdown before the agent processes them. Removes nav, footers, cookie banners, sidebar ads. Result: 3-4x more efficient web reading. Essential for any research, competitive analysis, or documentation lookup workflow.

---

### #11 Humanizer
**Repo:** https://github.com/blader/humanizer

Rewrites agent output in natural human voice. Based on Wikipedia's "Signs of AI" page — auto-updates as that page updates. Last line of defense before publishing AI-assisted content.

---

## Category 2 — Capability Expanders

### #10 YouTube Full
**Repo:** https://github.com/ZeroPointRepo/youtube-skills

Replaces the default YouTube skill that breaks on VPS/cloud IPs (YouTube blocks cloud traffic). Covers transcript extraction, channel browsing, playlist parsing, and video search. No Google API key required. Powered by an API processing 15 million transcripts a month.

---

### #9 Composio
**Repo:** https://github.com/ComposioHQ/skills

Connects agent to 1,000+ SaaS tools including Gmail, Sheets, Slack, Notion, HubSpot, and Salesforce. No hand-rolled OAuth, no API key juggling. Removes integrations as a bottleneck entirely.

---

### #8 Addy Osmani Agent Skills
**Repo:** https://github.com/addyosmani/agent-skills

65,000 GitHub stars. 24 production-grade skills around 8 slash commands mapped to the full dev lifecycle:

- `/spec` — before writing code
- `/plan` — break it down
- `/build` — implement
- `/test` — verify
- `/review` — before merge
- `/ship` — deploy

Standout feature: **Doubt-Driven Development** — agent stops at every major decision mid-task, extracts assumptions, challenges each one, reconciles gaps, then proceeds. Makes self-questioning automatic.

---

### #7 Resemble AI Detect
**Repo:** https://github.com/resemble-ai/detect-skill

Deepfake detection for any agent ingestion pipeline. Detects AI-generated audio, images, video, and text. Traces which tool produced it (ElevenLabs, ChatGPT, Claude, etc.) and watermarks it as AI. Essential when agent scrapes or researches the open web.

---

## Category 3 — Infrastructure & Multi-Agent

### #6 Mission Control / Minions
**Repo:** https://github.com/agent37-platform/minions

Full fleet dashboard for running multiple agents simultaneously. Provides task dispatch, agent health monitoring, real-time cost tracking, and live status across the whole stack. Bridges the gap between amateur agent setup and a managed multi-agent machine.

---

### #5 OpenMontage
**Repo:** https://github.com/calesthio/OpenMontage

World's first open-source agentic video production system. 12 pipelines, 52 tools, 500+ agent skills. Workflow:

1. Paste a reference YouTube video
2. Agent reads transcript, analyzes pacing, scene structure, key frames, tone
3. Proposes 2-3 differentiated concepts with full tool path and cost estimate
4. You approve before a single frame is generated

Example: 60-second Pixar-style animated short with narration, music, and word-level captions costs approximately $1.33.

---

### #4 Anthropic Cybersecurity Skills
**Repo:** https://github.com/mukul975/Anthropic-Cybersecurity-Skills

700+ structured skills mapped to the full MITRE ATT&CK framework. Covers threat modeling, vulnerability assessment, secure code review, and incident response playbooks — all queryable by the agent. Pitched as a cost-effective security engineer replacement for solo builders and small teams shipping real products.

---

## Category 4 — Top 3

### #3 Oh My Hermes
**Repo:** https://github.com/witt3rd/oh-my-hermes

Inspired by the 36,000-star Oh My Claude skill. Turns one agent session into a coordinated multi-agent workflow:

- Decomposes tasks into subtasks
- Assigns specialist agents or external CLI workers (Codex, Gemini, Cursor)
- Runs them in parallel or staged pipelines
- Verifies output rather than stopping at a half-done answer

Claims up to 50% token savings via smart routing. Persistent execution until verification passes. Best for complex tasks: shipping features, technical proposals, migrations.

---

### #2 Make Interfaces Feel Better
**Repo:** https://github.com/jakubkrehel/make-interfaces-feel-better

Based on the viral article "Details that make interfaces feel better." Once installed, agent automatically applies micro-polish rules to every UI it builds:

- Text wrapping so headlines don't orphan a single word
- Concentric border radius so nested element corners match
- Contextual icon animations (opacity, scale, blur on interaction)
- Tabular numbers so stats don't visually jump on update
- Interruptible animations that don't freeze on rapid clicks

---

### #1 Agent Reach
**Repo:** https://github.com/Panniantong/Agent-Reach

38,000 GitHub stars. Gives agents unrestricted access to the full internet including platforms that block cloud IPs:

- Twitter (paid API bypass)
- Reddit (403 bypass)
- YouTube on VPS
- GitHub

Zero API fees. When a platform changes its blocking, Agent Reach has a backup path already mapped — agent doesn't notice the change. Ranked #1 because it grants a capability the agent simply didn't have before, not just improves an existing one.

---

## Honorable Mentions

### Browser Harness
**Repo:** https://github.com/browser-use/browser-harness

15,000 stars. Connects agent directly to real Chrome browser. Clicks, scrolls, fills forms, navigates like a human. When it hits an unknown page, it writes the missing helper itself and keeps going — self-healing browser automation.

---

### Codebase Memory MCP
**Repo:** https://github.com/DeusData/codebase-memory-mcp

11,800 stars. Indexes entire codebase into a persistent knowledge graph. Tested on the Linux kernel: 28 million lines scanned in 3 minutes. Once indexed, agent uses 120x fewer tokens to explore it. Supports 158 languages.

---

### Loop Library / Loopy
**Repo:** https://github.com/Forward-Future/loopy

Gives agents a feedback cycle rather than a one-shot instruction. Pattern: measure result, keep if better, repeat until target hit. Example: instead of "make this website faster," agent finds slowest page, makes one focused improvement, measures again, keeps only if it helps, repeats until every page hits target. Includes a live catalog of pre-built loops and a plain-language loop designer.

---

# Chapter 2 — Adapting Hermes Skills for Claude Code

These are Hermes skills, not Claude Code skills. They were built for a different agent framework and cannot be dropped directly into `~/.claude/commands/` without adaptation. The analysis below identifies which are worth adapting, which to skip, and which depend on your use case.

---

## Strong Yes — Adapt These

| Skill | Why |
|---|---|
| **Grill Me** (from Pocock pack) | Claude Code often mis-builds because it charges ahead without enough context. A `/grill-me` skill that interviews you first before any implementation is directly useful. |
| **Addy Osmani Dev Pack** | `/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship` map perfectly to Claude Code's workflow. Doubt-driven development especially valuable. |
| **Make Interfaces Feel Better** | Pure instruction list — trivial to adapt. Every UI task benefits. |
| **Teach Me** (from Pocock pack) | Useful for turning any topic into structured learning output. |

---

## Skip — Already Covered Natively

| Skill | Why skip |
|---|---|
| **Defuddle** | Claude Code's `WebFetch` already converts pages to markdown |
| **YouTube Full** | We built `video_vtt_extract` which covers this |
| **Codebase Memory MCP** | Claude Code already has Glob, Grep, and the memory system |
| **Security Review** | Already a built-in skill (`/security-review`) |
| **Oh My Hermes** | Claude Code already has the Agent and Workflow tools for multi-agent orchestration |

---

## Skip — Requires Actual Infrastructure

| Skill | Why skip |
|---|---|
| **Agent Reach** | Needs proxy/bypass infrastructure, not just a markdown file |
| **Composio** | Needs OAuth plumbing |
| **Resemble AI Detect** | Needs actual detection API |
| **OpenMontage** | Needs video generation APIs |
| **Browser Harness** | Needs browser connection layer |
| **Mission Control** | Needs fleet infrastructure |

---

## Maybe — Depends on Use Case

| Skill | Condition |
|---|---|
| **Humanizer** | Worth it if you regularly publish AI-assisted content |
| **SkillClaw** | Interesting concept but hard to implement properly in Claude Code's memory system — would need careful design |
| **Loop Library** | Useful if you run repetitive improvement cycles |

---

## Verdict

Four solid adapts: **Grill Me**, **Addy Osmani Dev Pack**, **Make Interfaces Feel Better**, and **Teach Me**. These are pure instruction-based skills that translate directly into Claude Code markdown skill files with no external dependencies.
