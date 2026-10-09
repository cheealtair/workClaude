# Workplan: The Research Desk

A small, runnable demonstration of agent orchestration. One question goes in. A planner splits it, parallel workers research the pieces, a synthesizer merges them, and a critic gates the result. Every step is recorded as an event, and a web interface lets a human watch and replay the interaction among the agents.

Status (updated 2026-10-08, revision 2):
- Phase 1 (LLM wrapper) is DONE: `config.json` and `llm.py` exist and a ping to all three model tiers through the Siemens proxy succeeded.
- Phase 0 is PARTIAL: environment checked and `config.json` written; the folder skeleton (prompts/, tests/, runs/, assets/) is not yet created.
- Everything from Phase 2 onward is NOT built.
- Revision 2 changes: flow graph is now hand-drawn SVG with a browser-side animation player (see sections 5A and 5B); delivery uses `st.html` instead of the deprecated `components.html`; LLM text must never be turned into HTML or script (escaping rule, section 6); Phase 9 and 10 rewritten and a throwaway animation spike (Phase 9B) added.
Created: 2026-10-08

---

## 1. Purpose and Learning Goals

The demo exists to make the following ideas visible and measurable, not just described:

1. **Orchestrator-workers**: a central agent decomposes a task whose subtasks are not known in advance, delegates, and synthesizes.
2. **Parallelization (sectioning)**: independent subtasks run at the same time, so wall-clock time is about one worker, not three.
3. **Evaluator-optimizer**: a critic scores a draft against a rubric and feeds back; the synthesizer revises.
4. **Code-driven control**: the loop cap, retries, and sequencing live in ordinary code, not in a prompt. The LLM never decides when to stop looping.
5. **Model routing**: a stronger model plans and judges; a cheaper model does the bulk work.
6. **The cost tradeoff**: orchestrated mode is compared against a single-agent baseline on tokens, seconds, and quality, so the "more agents costs more tokens" claim is shown with real numbers.
7. **Context isolation vs. shared context**: workers see only their own brief; the synthesizer sees everything. This mirrors the lesson that conflicting decisions arise when parallel agents lack each other's context.
8. **Human-in-the-loop**: an optional approval gate before synthesis.
9. **Observability**: a human can see who called whom, when, with what input, and at what cost.

Non-goals: this is not a production framework, has no persistence beyond trace files, does not browse the web (workers answer from model knowledge unless a tool is added later), and does not try to beat existing frameworks.

---

## 2. Source Findings That Shaped This Design

Gathered 2026-10-08 from primary sources fetched directly (WebSearch was blocked by organisation policy for this model).

| Finding | Source | Design consequence |
|---|---|---|
| Five workflow patterns: chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer. Start simple. | Anthropic, Building Effective Agents | Demo combines three of the five and keeps all control in code. |
| Lead Opus + Sonnet subagents beat single Opus by 90.2% on an internal research eval; token use explained about 80% of variance; about 15x tokens vs chat. | Anthropic, multi-agent research system | Build the single-agent baseline and token accounting to reproduce the tradeoff at small scale. |
| Delegation briefs need objective, output format, tool guidance, and boundaries. Effort scaling rules prevent 50-subagent runaway. | Same | Planner emits structured briefs; worker count is capped in config. |
| Start evals with about 20 cases; LLM-as-judge with a rubric; add human testing. | Same | Critic uses a fixed rubric; a small test set is part of the plan. |
| Actions carry implicit decisions; share full traces, not just messages; single-threaded is a safe default. | Cognition, Don't Build Multi-Agents | Parallelize research only; synthesis is single-threaded and sees all worker output. |
| 14 failure modes in 3 groups: system design, inter-agent misalignment, task verification. 1,600+ traces, 7 frameworks. | MAST paper (arXiv 2503.13657) | Failure injection tests map to these groups (see section 11). |
| LLM-driven vs code-driven orchestration; agents-as-tools vs handoffs. | OpenAI Agents SDK docs | Demo uses code-driven control and agents-as-tools (the orchestrator owns the final answer). |
| LangGraph models state, nodes, edges, and a Send API for dynamic workers. | LangGraph docs | The event graph in the UI uses the same vocabulary: nodes (agent calls) and edges (data handoffs). |
| Durable execution gives retries, checkpoints, and approval signals. | Temporal AI cookbook | Out of scope to build, but the approval gate and trace file mimic checkpoint and pause concepts. |
| MCP is agent-to-tool; A2A is agent-to-agent. | A2A docs | Mentioned in the learning notes; the demo uses neither, to stay framework-free. |
| Subagents: isolated context, tool allowlists, default 3 nesting levels, 20 concurrent. | Claude Code docs | Informs the isolation rules and the concurrency cap in config. |
| Tool design: consolidate, namespace, concise responses. | Anthropic, Writing Tools for Agents | Applies if a search tool is added in a later phase. |
| `st.graphviz_chart` renders in the browser (d3-graphviz plus Graphviz WebAssembly) and accepts a DOT string; docs say the `graphviz` Python package (0.19 or newer) must be installed. No mention of needing `dot.exe`. Streamlit's own code (`graphviz_chart.py`) only forwards the DOT text to the front end. | Streamlit docs; installed Streamlit source | Graphviz is not needed for the viewer, but is also not the chosen renderer (section 5B). Not tested on this machine. |
| `st.components.v1.html` was deprecated in Streamlit 1.56.0 and will be removed; installed version is 1.57.0. The custom-components intro page still recommends it, so the docs contradict each other. | Streamlit docs | Do not build on `components.html`. |
| `st.html` strips JavaScript by default (DOMPurify); `unsafe_allow_javascript=True` lets scripts run; content is not iframed. Docs do not say whether script state survives reruns. | Streamlit docs | Animation player is delivered through `st.html`; rerun behaviour must be verified by a spike (Phase 9B). |
| Both Streamlit HTML pages warn never to pass untrusted content, explicitly including LLM output, into raw HTML. | Streamlit docs | Agent text is LLM output: hard escaping rule in section 6. |
| `st.fragment(run_every=...)` reruns a fragment on a timer without rerunning the whole app. | Streamlit docs | Used for live refresh in live mode. |
| SMIL SVG animation: an MDN summary called it "deprecated" but the page itself did not say so; treat as unverified. CSS and the Web Animations API are the documented modern routes. | MDN (summarized) | Use CSS transitions and JavaScript, not SMIL. |

---

## 3. Architecture

### 3.1 Agent roles

| Role | Default model tier | Input | Output | Sees |
|---|---|---|---|---|
| Planner | strong (config: `models.planner`) | the user question | JSON list of N sub-briefs | question only |
| Worker (xN) | cheap (config: `models.worker`) | one brief | answer, confidence, key claims | its own brief only |
| Synthesizer | strong or mid (config: `models.synthesizer`) | question + all worker outputs (+ critic feedback on revisions) | draft answer | everything |
| Critic | strong (config: `models.critic`) | question + draft | rubric scores, pass/fail, feedback | question + draft |

### 3.2 Flow

```
                       +-----------+
   question ---------> |  PLANNER  |
                       +-----+-----+
                             | N briefs (JSON, validated)
              +--------------+--------------+
              |              |              |
         +----v---+     +----v---+     +----v---+
         |WORKER 1|     |WORKER 2|     |WORKER 3|    (parallel threads)
         +----+---+     +----+---+     +----+---+
              |              |              |
              +--------------+--------------+
                             | all worker outputs
                     [optional human approval gate]
                             |
                       +-----v------+
                       | SYNTHESIZER|<-------------+
                       +-----+------+              |
                             | draft               | feedback (max K loops)
                       +-----v------+              |
                       |   CRITIC   |--- fail -----+
                       +-----+------+
                             | pass (or loop cap reached)
                             v
                        final answer + trace
```

### 3.3 Control rules (all in code)

- Planner output must parse as JSON and match a schema. One automatic retry with the parse error appended; a second failure aborts the run with a clear error event.
- Worker count is `min(planner_count, config.max_workers)`.
- Each worker has a timeout (`config.worker_timeout_s`). A timeout produces a `worker_failed` event; the run continues with the remaining workers and the synthesizer is told which brief has no answer.
- Critic loop runs at most `config.max_revisions` times. When the cap is reached, the latest draft is returned and flagged `cap_reached: true`. The LLM cannot extend the loop.
- Total token budget (`config.token_budget`): if exceeded mid-run, the run stops cleanly with the best available draft and a `budget_exceeded` event.

### 3.4 Event-driven design (the key to visualization)

The orchestrator does not talk to the UI. It emits **events** to an append-only JSONL file (one line per event) and optionally an in-process queue. The CLI, the web UI, and the exporters are all just consumers of the same event stream. This gives live view, replay, and post-hoc analysis from one mechanism.

Event types:

| Event | Fired when | Key fields |
|---|---|---|
| `run_started` | run begins | run_id, mode, question, config snapshot |
| `agent_started` | an agent call begins | span_id, parent_span_id, role, model, input_text, ts |
| `agent_finished` | an agent call ends | span_id, output_text, tokens_in, tokens_out, seconds, status |
| `agent_failed` | call error or timeout | span_id, error, retry_count |
| `handoff` | data passes from one span to another | from_span, to_span, payload_preview, payload_chars |
| `gate_waiting` | approval gate opens | gate_id, summary |
| `gate_resolved` | human decides | gate_id, decision, edited_text (optional) |
| `critic_verdict` | critic returns | scores, pass, feedback, loop_index |
| `run_finished` | run ends | final_answer, totals, cap_reached, budget_exceeded |

Every event carries `run_id`, a monotonic `seq`, and an ISO timestamp.

---

## 4. The Interface (what will be built)

Three interfaces share one engine. Build in this order: CLI, then Viewer, then static export.

### 4.1 CLI: `desk.py`

```
python desk.py "Compare vector databases and graph databases for CRM" 
python desk.py "..." --single            single-agent baseline only
python desk.py "..." --compare           run orchestrated AND single, print comparison table
python desk.py "..." --approve           pause for human approval before synthesis (terminal prompt)
python desk.py "..." --backend local     choose backend (proxy | local), overrides config
python desk.py --replay runs/<run_id>    re-print a finished run from its event log
python desk.py --export runs/<run_id>    write trace.mmd and trace.html
```

Terminal output while running: one line per event with role, model, elapsed time, and token counts, then a final summary table. This is the fallback view for headless use.

### 4.2 Web viewer: `viewer.py` (Streamlit)

Streamlit is chosen because it is already used elsewhere in this workspace (OrionBeltGraph) and needs no front-end build step. The viewer is a separate process from the engine. It either (a) launches a run by calling the engine in a background thread and tailing the event file, or (b) opens a finished run from `runs/`.

Layout (ASCII mockup):

```
+----------------------------------------------------------------------------+
| THE RESEARCH DESK                                    [Run] [Compare] [Open]|
| Question: [______________________________________________]                |
| Mode: (o) Orchestrated  ( ) Single  ( ) Compare   [x] Require approval     |
+----------------------------------------------------------------------------+
| Tabs:  1 Flow | 2 Timeline | 3 Conversation | 4 Cost | 5 Compare | 6 Raw   |
+----------------------------------------------------------------------------+
|                                                                            |
|   (active tab content)                                                     |
|                                                                            |
+----------------------------------------------------------------------------+
| Status bar: run abc123 | running | 4 of 6 agents done | 3,812 tokens | 9.4s |
+----------------------------------------------------------------------------+
```

### 4.3 Static export

`--export` produces:
- `trace.mmd`: a Mermaid diagram of the run.
- `trace.html`: a single self-contained HTML file (inline CSS and JS, no network, no CDN) with the flow graph, timeline, and conversation. It can be emailed or opened offline. Uses only ASCII in source.

---

## 5. How Humans Visualise the Interaction Among Agents

Six complementary views. Each answers a different question about the run.

### View 1: Flow graph ("who talked to whom")

- Nodes are agent calls (spans). Edges are handoffs.
- Layout is left to right: Planner, Workers (stacked), Synthesizer, Critic, with a curved back-edge from Critic to Synthesizer for each revision.
- Node colour shows status: grey waiting, blue running, green finished, red failed, amber retried.
- Node label shows role, model tier, tokens, and seconds. Edge label shows the size of the payload passed.
- Live: nodes light up as events arrive, so a human watches the fan-out and fan-in happen.
- Click a node to open the Inspector panel (see View 3) for that span.
- Implementation: hand-drawn SVG generated in Python (`render.py`), animated in the browser by a small JavaScript player (section 5A). The layout is fixed because the topology is fixed. No Graphviz, no Mermaid library, no extra install. A Mermaid text export (`trace.mmd`) is kept only as a secondary, shareable artefact.

### View 2: Timeline / swimlane ("when did things happen, and what ran in parallel")

- One horizontal lane per agent, time on the x-axis, a bar per call from `agent_started` to `agent_finished`.
- The three workers appear as overlapping bars, proving parallelism visually. A sequential run would show a staircase.
- Critic and revision loops appear as alternating bars in the tail.
- Gate waiting time is drawn as a hatched bar so human latency is distinguishable from model latency.
- Implementation: Plotly or Altair horizontal bar chart (pick one, confirm it is installed in `py_claude` first; Altair ships with Streamlit so prefer Altair).

### View 3: Conversation and inspector ("what exactly was said")

- A chat-style transcript ordered by `seq`, each message tagged with role and span id: Planner to Workers (the briefs), Workers to Synthesizer (answers), Synthesizer to Critic (draft), Critic to Synthesizer (feedback).
- Selecting any span shows: full input prompt, full output, model, tokens in and out, seconds, retry count, and a diff view between draft N and draft N+1 for revisions.
- A toggle highlights text that was passed on (the handoff payload) versus text that was dropped, making information loss between agents visible.

### View 4: Cost and efficiency ("what did it cost")

- Stacked bar of tokens by role (planner, workers, synthesizer, critic).
- Table: calls, tokens in, tokens out, seconds, estimated cost per role (cost rates come from `config.json`, clearly labelled as estimates).
- Critical-path indicator: which chain of spans determined total wall-clock time.

### View 5: Compare ("is orchestration worth it")

- Side-by-side: orchestrated answer vs single-agent answer for the same question.
- Metrics row: total tokens, total seconds, number of agent calls, answer length, critic score of each (the same critic scores both for fairness).
- Verdict line states the ratio, for example "orchestrated used 6.2x tokens and 1.4x time for +1.3 rubric points". The line reports numbers only; it does not declare a winner.

### View 6: Raw events ("trust but verify")

- The JSONL event stream as a filterable table, with a download button.
- Guarantees the other five views can be audited against the underlying data.

### Cross-cutting visual aids

- **Replay player**: play, pause, speed (0.5x, 1x, 2x, 4x) and a scrubber over `seq` replay a finished run, with the flow graph and timeline revealing events progressively. The same player is embedded in the live viewer and in `trace.html` (section 5A).
- **Approval gate panel**: when `gate_waiting` fires, a banner shows the worker answers with Approve, Edit, and Reject buttons. Approve continues; Edit lets the human alter a worker answer before synthesis; Reject aborts with a `run_finished` of status rejected. The decision is logged as `gate_resolved`.
- **Legend**: a small fixed legend explains colours and shapes.

---

## 5A. Animation Design (about 3 frames per second)

### What animation means here

Agent events arrive seconds apart, not several per second. So the animation is smooth state change between events, plus small motion effects, not frame-by-frame video. A tick rate of about 3 per second (roughly 333 ms) is enough; the browser interpolates between ticks.

### Effects

| Effect | Trigger event | Visual |
|---|---|---|
| Node waiting to running | `agent_started` | Node fill fades from grey to blue; a slow pulse ring while running |
| Node finished | `agent_finished` | Fill fades to green; token count ticks up to its final value |
| Node failed or retried | `agent_failed` | Fill red or amber; brief shake |
| Handoff | `handoff` | A small dot travels along the edge from source to target; edge thickness reflects payload size |
| Fan-out and fan-in | planner finishes, workers finish | Three dots leave the planner together; three converge on the synthesizer |
| Revision loop | `critic_verdict` with fail | Dot travels the back-edge from critic to synthesizer; loop counter increments |
| Gate waiting | `gate_waiting` | Node outline blinks until `gate_resolved` |
| Timeline bars | `agent_started` to `agent_finished` | Bar grows to the right in step with the clock |
| Counters | every event | Status bar totals (tokens, seconds, calls) count up smoothly |

### Architecture of the player

- One self-contained player (`assets/player_template.html`): inline SVG, CSS and a small script, no network access, no external libraries. ASCII only.
- The Python side renders the static SVG (nodes, edges, lanes) and embeds the event list as a JSON data block.
- The script keeps its own clock. Given the event list it computes, for any time t, the state of every node and edge, and applies it by switching CSS classes. CSS transitions (0.3 s) supply the smoothness, so the redraw rate can stay low.
- Replay mode: the whole event list is loaded once; play, pause, speed and scrubber are handled entirely in the browser. Nothing is redrawn from Python.
- Live mode: a Streamlit fragment with `run_every` of about 1 to 2 seconds appends new events. Because the browser clock and transitions do the smoothing, the graph does not need 3 redraws per second from Python.
- Export mode: the identical template, written out as `trace.html`, replays offline.

### Delivery inside Streamlit

- Use `st.html` with `unsafe_allow_javascript=True`. Do not use `components.html` (deprecated in 1.56.0; installed version is 1.57.0).
- Open unknowns (verified by the Phase 9B spike before the viewer is built): whether the script survives or restarts on a rerun, and whether DOMPurify leaves the SVG and CSS animation intact when JavaScript is enabled.
- Fallback if scripts do not behave: show `trace.html` through an iframe pointing at a file, or open the export in a browser tab. Whether the iframe route is itself deprecated has not been checked.
- Fallback of last resort: redraw SVG from Python on a fragment timer. From reasoning, not a test: replacing the whole element each tick means CSS transitions have no previous state to animate from, so changes will snap.

### Timeline and cost charts

Altair charts redraw on a fragment tick and need no animation beyond growing bars; this is acceptable at about 1 to 2 redraws per second.

---

## 5B. Decision Record: Flow Graph Rendering

Decision: hand-drawn SVG with a browser-side player. Date: 2026-10-08. Based on documentation fetched that day plus general knowledge; items marked "not verified" were not tested on this machine.

| Option | Verdict | Reason |
|---|---|---|
| Hand-drawn SVG plus CSS/JS player | CHOSEN | Fixed topology makes layout trivial; per-node status colours, click handling, replay and offline export come from one code path; no install |
| `st.graphviz_chart` with DOT | Not chosen | Browser re-lays out the whole graph on every update, so nodes can jump; needs the `graphviz` pip package; no evidence of smooth transitions in Streamlit's wrapper |
| Graphviz with `dot.exe` | Not chosen | A standalone program (graphviz.org, winget or conda-forge), not a Python package; may need admin rights or approval on a managed machine; the `graphviz` pip package is only a wrapper around it |
| Mermaid | Secondary only | Text export for sharing; weak for status colours, click handling and animation |
| pyvis / vis-network | Rejected | Physics layout keeps nodes moving; wrong kind of motion for showing state |
| networkx plus matplotlib | Rejected | Static images; layouts unsuited to layered flows |
| Plotly or Altair with manual nodes | Rejected | No better than hand SVG, more awkward for arrows and curves |
| Cytoscape.js (with dagre layout) | Upgrade path | Built-in animation and interaction; worth the JavaScript effort only if the topology becomes dynamic (tools, nested subagents, routers) |

Graphviz remains useful as a one-time layout engine if the graph ever becomes arbitrary; that is out of scope now.

---

## 6. Technology and Constraints

- Python 3.12, conda environment `py_claude` (the only Python location permitted is C:\miniforge3; envs under C:\miniforge3\envs\). Confirm the env exists with a check command before first use.
- Engine: standard library only (`concurrent.futures`, `json`, `time`, `dataclasses`, `argparse`, `uuid`, `threading`, `queue`).
- LLM access: a single `llm.py` wrapper. Backend chosen by the user: the Siemens Claude proxy (`https://llm.sdc.siemens.cloud`). The local LiteLLM/Qwen route is deferred and not implemented. The API key is read from the `ANTHROPIC_API_KEY` environment variable and never written to code, config, logs or trace files. Model IDs in `config.json` come from the user's Claude Code settings: Opus `claude-opus-5-5` (planner, critic), Sonnet `claude-sonnet-5-5` (synthesizer, single-agent baseline), Haiku `claude-haiku-4-5-20251001` (workers).
- Cost rates in `config.json` are blank (null) because they have not been supplied; the cost view shows tokens only until the user fills them in. Never guess rates.
- Environment facts checked 2026-10-08: `py_claude` has streamlit 1.57.0, altair 6.1.0, httpx 0.28.1, requests, pandas, and pytest 9.1.1 (installed this session). The `anthropic` package and the Graphviz `dot` binary are not installed and are not needed.
- Escaping rule (security, non-negotiable): all agent input and output is LLM output and must be treated as untrusted. It is passed to the browser only as JSON data inside a data block and displayed with `textContent`-style insertion, never concatenated into HTML, SVG or script text. Node labels in the SVG are fixed role names, not model text. The HTML export escapes all embedded text and the JSON block is serialised so it cannot close its own script tag. A test feeds an event whose text contains script and markup strings and asserts nothing executes or renders as markup.
- Viewer: Streamlit plus Altair (bundled) plus an SVG and JavaScript player delivered with `st.html(unsafe_allow_javascript=True)`. No Graphviz, no `components.html`.
- Code character safety: ASCII only in all source, comments, and generated files. No Unicode box-drawing characters anywhere.
- No hard-coded colours, model names, rates, or limits in code; all in `config.json` (and a `viewer_style.json` for UI colours, following the workspace convention of externalised styling).
- Hooks and process rules: the engine runs as a normal user script; nothing here touches git.
- Security: question and answer text are treated as untrusted when rendered; HTML export escapes all content.

---

## 7. File and Folder Layout

```
research_desk/
  workplan.md            this document
  config.json            models, backend, limits, rates, rubric weights
  viewer_style.json      status colours, fonts, layout constants
  llm.py                 chat(backend, model, system, user) -> text, tokens_in, tokens_out
  events.py              Event dataclass, EventBus, JSONL writer and reader
  agents.py              planner, worker, synthesizer, critic, single_agent functions
  engine.py              orchestrated run, single run, compare run, gate handling
  desk.py                CLI entry point
  viewer.py              Streamlit app (6 tabs, replay scrubber, gate panel)
  render.py              flow graph SVG, timeline data, draft diff, Mermaid export, HTML export
  assets/
    player_template.html self-contained SVG, CSS and JS animation player (replay, live, export)
  prompts/
    planner.md           system prompt and JSON schema instructions
    worker.md
    synthesizer.md
    critic.md            rubric text
    single.md
  tests/
    test_events.py
    test_planner_parse.py
    test_loop_cap.py
    test_parallel_timing.py
    test_failure_injection.py
    questions.json       the 3 test questions plus expected behaviours
  runs/                  one folder per run: events.jsonl, final.md, trace.mmd, trace.html
```

Prompts live in separate markdown files so they can be edited and versioned without touching code.

---

## 8. Phases, Tasks, and Done-When Criteria

### Phase 0: Setup and confirmation (small) - PARTIAL
Tasks:
- Create the folder skeleton above. (NOT DONE: only `config.json` and `llm.py` exist so far; create prompts/, tests/, runs/, assets/ when Phase 2 starts.)
- Verify `py_claude` exists and which packages are installed. (DONE 2026-10-08; pytest installed with the user's approval.)
- Obtain from the user: backend choice, model names for each tier, endpoint settings. (DONE: Siemens proxy; Opus plans and judges, Sonnet synthesizes, Haiku works; endpoint and model IDs taken from the user's Claude Code settings; key from the environment.)
Done when: skeleton exists, environment check printed, `config.json` filled with user-supplied values.

### Phase 1: LLM wrapper - DONE 2026-10-08
Result: `python llm.py --ping` succeeded on all three tiers with real (not estimated) token counts. Haiku 1.4 s, Sonnet 2.2 s, Opus 1.8 s for a trivial prompt.
Tasks:
- Implement `chat()` for both backends with timeouts and one retry on transient errors.
- Return text plus token counts; if a backend omits usage, estimate by character count and mark `estimated: true`.
- Add a `--ping` self-test.
Done when: one call on each backend prints a reply and token usage.

### Phase 2: Events and trace
Tasks:
- Define the Event dataclass and all event types in section 3.4.
- JSONL writer (flush on every event so a tailing UI sees it immediately) and reader.
- EventBus with subscriber callbacks; terminal printer is the first subscriber.
- Span id and parent span id helpers.
Done when: a dummy run with fake agents produces a valid `events.jsonl` that round-trips through the reader, with correct parent-child links.

### Phase 3: Planner
Tasks:
- Prompt that outputs strict JSON: `{"briefs":[{"id","objective","boundary","output_format"}]}`.
- Schema validation, one retry with the parse error appended, then abort event.
- Enforce N between 2 and `max_workers`; reject duplicate or overlapping objectives by checking identical `objective` strings.
Done when: valid output passes, malformed output triggers exactly one retry, and a second failure aborts cleanly.

### Phase 4: Parallel workers
Tasks:
- Run briefs through a `ThreadPoolExecutor` sized to the brief count (capped by config).
- Each worker returns `{"answer","confidence","key_claims"}`; per-worker timeout; partial-failure handling per section 3.3.
- Emit `handoff` events from planner to each worker.
Done when: three simulated 2-second workers finish in about 2 seconds total (test asserts under 3.5 s), and one forced timeout still lets the run continue.

### Phase 5: Synthesizer
Tasks:
- Build the synthesis prompt from the question plus all worker outputs, listing any failed briefs explicitly.
- On revision, include the critic feedback and the previous draft.
Done when: a run produces a draft that references all non-failed worker outputs.

### Phase 6: Critic loop
Tasks:
- Rubric (accuracy, completeness, clarity, consistency with worker claims), each scored 1 to 5, with weights from config and a pass threshold.
- Critic returns strict JSON (scores, pass, feedback); validate and retry once.
- Loop controller in code with `max_revisions`; emit `critic_verdict` each pass; set `cap_reached`.
Done when: a forced-fail critic stub stops at exactly the cap, and a pass on the first try produces zero revisions.

### Phase 7: Single-agent baseline and compare
Tasks:
- `single_agent()` makes one call with the question and a general instruction.
- `compare` mode runs both, then scores both answers with the same critic prompt.
- Comparison table: tokens, seconds, calls, answer length, rubric score, ratios.
Done when: `--compare` prints the table and writes both runs under `runs/`.

### Phase 8: CLI polish and replay
Tasks:
- `--approve` terminal gate, `--replay`, `--export` wiring, exit codes, error messages.
Done when: every CLI flag in 4.1 works against a real run.

### Phase 9: Renderers and animation player
Tasks:
- `render.py`: SVG generation of the fixed flow layout (planner, up to `max_workers` worker nodes, synthesizer, critic, back-edge) with fixed role labels; timeline data frame; draft-diff helper; Mermaid text export.
- `assets/player_template.html`: self-contained player implementing the effects table in section 5A: own clock, CSS-transition state changes, travelling handoff dots, play, pause, speed, scrubber. Event list embedded as a JSON data block; all text inserted as text, never as markup (escaping rule, section 6).
- Static HTML builder: injects the SVG and the serialised event list into the template and writes `trace.html`.
- A test rebuilds the node and edge set from `events.jsonl` and compares it with the SVG (success criterion 3).
- An escaping test per section 6.
Done when: `trace.html` opens offline in a browser, animates a recorded run end to end at 1x and 4x, the scrubber jumps correctly, `trace.mmd` pastes into a Mermaid renderer, and the escaping test passes.

### Phase 9B: Animation spike (throwaway, before Phase 10)
Purpose: settle the unknowns in section 5A before building the viewer around them.
Tasks:
- Make a minimal Streamlit page that embeds a tiny SVG with a CSS transition and a script timer through `st.html(unsafe_allow_javascript=True)`.
- Check four things: (1) does DOMPurify keep the SVG and CSS intact; (2) does the script run at all; (3) does the script keep its state or restart when a fragment with `run_every` of 1 second reruns the page; (4) does a node colour change animate smoothly or snap.
- Try the fallback routes in section 5A only if needed, and note whether an iframe route is deprecated.
- Record results in the Decision Record (section 5B). The spike code is discarded afterwards.
Done when: the delivery route for Phase 10 is chosen based on observed behaviour, not documentation alone.

### Phase 10: Streamlit viewer
Tasks:
- Run panel (question, mode, approval toggle) launching the engine in a background thread.
- Live tailing of `events.jsonl` with a fragment refresh (`run_every` about 1 to 2 seconds).
- Flow graph tab embeds the Phase 9 player using the route chosen in Phase 9B; Timeline and Cost tabs use Altair.
- Tabs 1 to 6 as specified in section 5; replay player; gate panel with Approve, Edit, Reject; status bar; legend.
- Open-existing-run picker reading `runs/`.
- All displayed agent text follows the escaping rule in section 6.
Done when: a live run visibly lights up the flow graph with smooth transitions, the timeline shows overlapping worker bars, and approving at the gate resumes the run.

### Phase 11: Tests and evaluation
Tasks:
- Unit tests listed in section 7; failure-injection tests in section 11.
- Run the 3 test questions in compare mode and record results in `runs/` plus a short findings note (written only on request).
Done when: tests pass and the three questions have comparison results saved.

---

## 9. Test Questions (to be stored in `tests/questions.json`)

| ID | Question type | Expected behaviour | What it shows |
|---|---|---|---|
| Q1 | Narrow factual comparison, for example "What is the difference between a B-tree and an LSM-tree index?" | Single agent is nearly as good, orchestrated costs several times more tokens | Orchestration is not free; small tasks do not need it |
| Q2 | Multi-part research question, for example "Compare five approaches to long-term memory for LLM agents, covering storage, retrieval, cost, and failure modes" | Orchestrated answer more complete (higher completeness score) | Where decomposition and parallelism pay off |
| Q3 | Deliberately vague, for example "Tell me about agents" | Planner makes arbitrary splits; critic flags low focus; may hit the loop cap | Garbage in, orchestrated garbage out; the cap protects cost |

---

## 10. Success Criteria

1. In compare mode the report shows orchestrated token use as a multiple of single-agent use, computed from recorded usage, not asserted.
2. The timeline shows worker bars overlapping; total worker-phase time is within 1.5x of the slowest single worker.
3. The flow graph in the viewer matches the event log exactly (node count and edges verified by a test that rebuilds the graph from `events.jsonl`).
4. The loop cap and the JSON retry both fire correctly under test.
5. A first-time viewer can answer "which agent said what, to whom, and what did it cost" using only the viewer, without reading code or logs.
6. `trace.html` works offline in a browser with no network access.

---

## 11. Failure Injection (mapped to the MAST failure groups)

| Group | Injected fault | Expected system response |
|---|---|---|
| System design | Planner returns two near-identical briefs | Duplicate check rejects or merges; event logged |
| System design | Planner returns 12 briefs | Capped to `max_workers`; event logged |
| Inter-agent misalignment | A worker ignores its output format | Parser retry once, then marked failed; synthesizer told |
| Inter-agent misalignment | Two workers give contradictory claims | Synthesizer prompt requires listing the conflict; critic rubric has a consistency score |
| Task verification | Critic always returns fail | Loop stops at cap; `cap_reached` shown in the viewer |
| Task verification | Critic returns malformed JSON | One retry, then treated as inconclusive and flagged |
| Infrastructure | Worker call times out | Run continues without it |
| Infrastructure | Token budget exceeded mid-run | Clean stop with best draft and `budget_exceeded` |

---

## 12. Risks and Open Items

- **Backend and models: resolved 2026-10-08.** Siemens proxy; Opus, Sonnet and Haiku tiers as in section 6. The local LiteLLM route is deferred.
- **Animation delivery is unverified.** `st.html` with JavaScript may sanitize SVG or restart scripts on rerun; the Phase 9B spike decides the route. If every in-Streamlit route fails, the fallback is to open `trace.html` in a browser tab and keep Streamlit for the non-animated tabs.
- **Streamlit docs contradict each other** on `components.html` (deprecated in 1.56.0 versus still recommended on the intro page). The deprecation notice is trusted; recheck docs if upgrading Streamlit.
- **Untrusted text in HTML.** LLM output flowing into the page is the main security risk of the viewer; see the escaping rule and its test.
- **Local model quality.** A local Qwen model may produce unreliable JSON; the retry logic exists for this, but the critic may be noisy, which weakens the compare view. Using a stronger model for planner and critic is recommended when available.
- **Token counts.** If a backend does not return usage, counts are estimates and are labelled as such in every view.
- **Graphviz is not used.** It is a separate program (`dot.exe`), not a Python package, and the viewer does not need it. Revisit only if the graph topology becomes dynamic (see section 5B).
- **Zscaler** must be ON or OFF depending on the backend (proxy needs corporate access; local needs none). Check this first when a call fails.
- **Single-run variance.** One run of each question proves little; the compare view should state that results are single samples. A repeat flag (`--repeat N`) is a candidate extension.

---

## 13. Possible Extensions (not in scope now)

- Add a real search tool to workers via a small MCP server, then show tool calls as extra nodes in the flow graph.
- Add a routing step before the planner (simple vs complex question) to demonstrate the routing pattern and skip orchestration for easy questions.
- Add durable checkpointing so a run can resume after a crash.
- Add voting: run the critic three times and take a majority.
- Port the same flow to LangGraph or the Claude Agent SDK to compare the same behaviour across frameworks.
- Replace the hand-drawn SVG with Cytoscape.js (dagre layout) if the topology becomes dynamic, to gain automatic layout, built-in animation and click handling.
- Look at Streamlit's newer two-way custom components (not read during this planning) if the player ever needs to send events back to Python.
