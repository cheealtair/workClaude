# The Research Desk: Project Description and Build Plans

A demonstration of agent orchestration. One question goes in. A planner splits it, parallel workers research the pieces, a synthesizer merges them, and a critic gates the result. Every step is recorded, and a human can watch, replay and inspect the interaction among the agents.

Created: 2026-10-08. Current revision: 3.

---

## Document Map

| Part | Title | Contains | Build details? |
|---|---|---|---|
| A | Project Description | Purpose, use case, agent architecture, business requirements (BR), functional requirements (FR), non-functional requirements (NFR), acceptance criteria, risks | NO. Solution-neutral. No tech stack, no product names for the build. |
| B | Build 1: Python and Streamlit | Tech stack, design, event log format, interfaces, visualisation and animation design, phases, tests, risks | YES |
| C | Build 2: Mendix (parallel, alternative) | Skeleton: relationship to Part A, starting facts, concept mapping, requirement-to-platform gap table, open questions | YES, but only a skeleton for now |
| D | Revision history | What changed in each revision | n/a |

Rules for reading and editing this document:
1. Part A is the single source of truth for WHAT the system does. Parts B and C describe HOW, and each must trace back to Part A requirement IDs (BR-xx, FR-xx, NFR-xx).
2. Parts B and C are independent. Either can be built without the other. They share Part A and the same acceptance tests (section A7), so the two builds can be compared fairly.
3. If a build cannot meet a Part A requirement, that is recorded as a gap in that build's part; Part A is not quietly changed to suit the build.
4. Decisions made in a build part never leak into Part A. If a decision belongs in Part A, it is moved there explicitly and logged in Part D.

Status of the work (2026-10-08):
- Part A: written in this revision, awaiting the owner's review.
- Part B: Phase 1 (LLM wrapper) is DONE. Phase 0 is PARTIAL. Everything from Phase 2 onward is NOT built.
- Part C: skeleton only. Nothing researched beyond the starting facts in C2.

---
---

# PART A: PROJECT DESCRIPTION (solution-neutral)

---

## A1. Purpose, Audience, Learning Goals, Non-Goals

### A1.1 Purpose

Agent orchestration is the practice of coordinating several AI agents, each with a narrow job, to complete a task that one agent would do less well or more slowly. It is easy to describe and hard to see. The Research Desk is a small working example that makes orchestration visible and measurable: a viewer can watch the agents divide the work, run in parallel, hand results to each other, be checked, and be bounded, and can see what it all cost compared with asking a single agent.

The example task is research: answering a question by decomposing it, researching the parts, and assembling a checked answer. Research is chosen because it parallelises naturally, which is where orchestration has the strongest evidence of paying off (see A3.7).

### A1.2 Audience (assumed; to be confirmed by the owner)

| Id | Audience | What they want from it |
|---|---|---|
| U1 | Presenter (for example a pre-sales engineer) | A demo that explains agent orchestration to a customer in minutes and holds up to questions |
| U2 | Learner or builder | A small, readable example to study before designing a real orchestrated system |
| U3 | Reviewer or sceptic | Evidence: what exactly did each agent say, and what did it cost, so claims can be checked |

### A1.3 Learning goals

The demonstration exists to show the following, not merely to state them:

- LG-1 **Orchestrator-workers**: a central agent decomposes a task whose subtasks are not known in advance, delegates, and synthesizes.
- LG-2 **Parallelisation (sectioning)**: independent subtasks run at the same time, so elapsed time is about one worker, not the sum of all workers.
- LG-3 **Evaluator-optimiser**: a critic scores a draft against a rubric and feeds back; the draft is revised.
- LG-4 **Code-driven control**: loop caps, retries, timeouts and budgets are enforced by ordinary program logic, not by asking a model to stop. No model decides when to stop looping.
- LG-5 **Model routing**: a stronger model plans and judges; a cheaper model does the bulk work.
- LG-6 **The cost tradeoff**: orchestrated mode is compared with a single-agent baseline on tokens, seconds and quality, so the claim "more agents costs more" is shown with real numbers.
- LG-7 **Context isolation versus shared context**: workers see only their own brief; the synthesizer sees everything. This illustrates why conflicting decisions arise when parallel agents lack each other's context.
- LG-8 **Human in the loop**: an optional approval step before synthesis.
- LG-9 **Observability**: a human can see who called whom, when, with what input, and at what cost.

### A1.4 Non-goals

- Not a production framework, and no attempt to compete with existing orchestration frameworks.
- No persistence requirement beyond saved run records.
- No live web browsing: workers answer from model knowledge unless a tool is added in a later extension (A8.4).
- No multi-user, authentication or permission features.
- No claim that orchestration is better than a single agent. The purpose is to show when it is and is not.

---

## A2. The Use Case in Plain Terms

### A2.1 Scenario

A presenter types a research question. The system shows a small team of agents at work: one agent splits the question into parts, several agents research the parts at the same time, one agent merges the findings into an answer, and one agent checks the answer and may send it back for another pass. The presenter can optionally approve the findings before the answer is written. When the run ends, the presenter sees the answer, a picture of who did what, a timeline showing the parallel work, and the cost. The presenter can then ask the same question of a single agent and compare.

### A2.2 Worked example (illustrative; invented for explanation, not output of the system)

Question: "Compare five approaches to long-term memory for LLM agents, covering storage, retrieval, cost and failure modes."

1. The planner splits this into three briefs, for example: (1) storage options and their tradeoffs, (2) retrieval approaches, (3) cost and failure modes. Each brief states an objective, a boundary (what the worker must NOT cover, to avoid overlap) and an output format.
2. Three workers run at the same time, one per brief. Each sees only its own brief. Each returns an answer, a confidence level and a list of key claims.
3. Optionally, the presenter reviews the three worker answers and approves, edits or rejects.
4. The synthesizer receives the original question and all three worker outputs and writes one draft. If a worker failed, the synthesizer is told which brief has no answer. If two workers contradict each other, the synthesizer must state the conflict.
5. The critic scores the draft on accuracy, completeness, clarity and consistency. Suppose it fails the draft with feedback "the cost section has no numbers".
6. The synthesizer revises using the feedback. The critic scores again. Suppose it passes.
7. The run ends. The record shows seven or so agent calls, the handoffs between them, the time each took, the tokens each used, and the number of revision loops.

Then the same question goes to a single agent, and the compare view shows tokens, seconds, calls, answer length and critic score side by side.

### A2.3 What the viewer takes away

- The work was divided, and the division is inspectable.
- Parallel work really overlapped in time.
- A checker caught something, or did not, and the loop was bounded.
- The orchestrated answer cost a measurable multiple of the single answer, and that is what bought whatever extra quality appeared.

---

## A3. Agent Architecture

This section is the focus of the project. It is solution-neutral: it describes agents, flow and rules, not technology.

### A3.1 Roles

| Role | Capability tier | Input | Output | What it can see |
|---|---|---|---|---|
| Planner | Strong | The user question | 2 to N briefs (objective, boundary, output format) | The question only |
| Worker (one per brief) | Cheap | One brief | Answer, confidence, key claims | Its own brief only |
| Synthesizer | Strong or mid | Question, all worker outputs, and on revisions the critic feedback and previous draft | A draft answer | Everything |
| Critic | Strong | Question and draft (and the worker claims for the consistency check) | Rubric scores, pass or fail, feedback | The question, the draft and the worker claims |
| Single agent (baseline only) | Mid | The question | An answer | The question only |

Capability tiers are abstract (strong, mid, cheap). Concrete model names are build decisions and live in Parts B and C.

### A3.2 Flow

```
                       +-----------+
   question ---------> |  PLANNER  |
                       +-----+-----+
                             | N briefs (validated)
              +--------------+--------------+
              |              |              |
         +----v---+     +----v---+     +----v---+
         |WORKER 1|     |WORKER 2|     |WORKER 3|    (run at the same time)
         +----+---+     +----+---+     +----+---+
              |              |              |
              +--------------+--------------+
                             | all worker outputs
                     [optional human approval step]
                             |
                       +-----v------+
                       | SYNTHESIZER|<-------------+
                       +-----+------+              |
                             | draft               | feedback (at most K loops)
                       +-----v------+              |
                       |   CRITIC   |--- fail -----+
                       +-----+------+
                             | pass (or loop limit reached)
                             v
                        final answer + full record
```

### A3.3 Patterns demonstrated

| Pattern | Where it appears |
|---|---|
| Orchestrator-workers | Planner decomposes dynamically; workers execute; synthesizer assembles |
| Parallelisation (sectioning) | The workers run simultaneously on independent briefs |
| Evaluator-optimiser | Synthesizer and critic loop |
| Routing (model tiers, not input routing) | Strong model for planning and judging, cheap model for workers |
| Code-driven control | Limits, retries, timeouts and budgets enforced outside the models |
| Agents-as-tools style ownership | The orchestration layer, not any worker, owns the final answer |

### A3.4 Control rules (all enforced outside the models)

- CR-1 The planner output must be valid and well-formed. One automatic retry is allowed, with the error described to the planner. A second failure ends the run with a clear error.
- CR-2 The number of workers is the planner's count, capped by a configured maximum.
- CR-3 Each worker has a time limit. A worker that exceeds it is marked failed; the run continues with the others, and the synthesizer is told which brief has no answer.
- CR-4 The revision loop runs at most a configured number of times. When the limit is reached the latest draft is returned and flagged "limit reached". No model can extend the loop.
- CR-5 There is a total token budget. If it is exceeded mid-run the run stops cleanly with the best available draft and a "budget exceeded" flag.
- CR-6 Duplicate or overlapping briefs are rejected or merged before workers start.
- CR-7 A critic reply that is malformed is retried once, then treated as inconclusive and flagged.

### A3.5 Information rules

- IR-1 Workers are isolated: each sees only its own brief. This makes parallelism safe and also makes the cost of lost context visible.
- IR-2 Synthesis is single-threaded and sees all worker output, so conflicting decisions are resolved in one place (the lesson that parallel agents making independent decisions can conflict).
- IR-3 The planner's briefs carry explicit boundaries so workers do not duplicate each other.
- IR-4 Anything an agent receives or produces is recorded in full, so it can be inspected afterwards.

### A3.6 Observability contract (what must be observable)

The system must make the following observable, whatever the technology. How they are stored is a build decision.

| Observable | Meaning | Key content |
|---|---|---|
| Run started | A run begins | Run identifier, mode, question, the settings in force |
| Agent call started | An agent begins work | Call identifier, parent call, role, model tier and name, input text, time |
| Agent call finished | An agent completes | Output text, tokens in, tokens out, seconds, status |
| Agent call failed | Error or time limit | Error, retry count |
| Handoff | Data passes from one call to another | Source call, target call, size of payload, short preview |
| Approval waiting | The human step opens | What the human is shown |
| Approval decided | The human acts | Approve, edit or reject, and any edited text |
| Critic verdict | The critic returns | Scores, pass or fail, feedback, loop index |
| Run finished | The run ends | Final answer, totals, limit-reached flag, budget-exceeded flag, status |

Every observable is time-stamped and ordered. A finished run can be fully reconstructed from these alone (FR-33).

### A3.7 Research evidence behind the design

Gathered 2026-10-08 from primary sources fetched directly. WebSearch was blocked by organisation policy for the model in use, so only directly fetched pages were used; statements about sources not fetched are marked as such.

| Finding | Source | Consequence for the design |
|---|---|---|
| Five workflow patterns: prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimiser. Start simple and add complexity only when simpler setups demonstrably underperform. | Anthropic, Building Effective Agents | The demo combines three of the five and keeps all control in program logic. |
| An Opus lead with Sonnet subagents beat single-agent Opus by 90.2% on an internal research eval. Token usage explained about 80% of the variance, and the system used about 15 times the tokens of chat. | Anthropic, multi-agent research system | The single-agent baseline and token accounting reproduce the tradeoff at small scale. |
| Delegation briefs need objective, output format, tool guidance and boundaries. Effort-scaling rules prevent runaway agent counts (early systems spawned 50 or more subagents for simple queries). | Same | Planner emits structured briefs; worker count is capped. |
| Start evaluations with about 20 cases; use an LLM judge with a rubric; add human testing. | Same | The critic uses a fixed rubric; a small test set is part of acceptance. |
| Multi-agent suits heavy parallelism, work exceeding one context window, and many tools; it suits shared-context work such as coding less. | Same | Only research reading is parallelised; synthesis is single-threaded. |
| Actions carry implicit decisions; share full traces, not just messages; a single-threaded agent is a safe default. | Cognition, Don't Build Multi-Agents | IR-1 and IR-2. |
| 14 failure modes in 3 groups: system design, inter-agent misalignment, task verification. 1,600 or more annotated traces across 7 frameworks. | MAST paper (arXiv 2503.13657) | Failure scenarios in A7.3 map to these groups. |
| LLM-driven versus code-driven orchestration; agents-as-tools versus handoffs. | OpenAI Agents SDK documentation | Code-driven control; the orchestration layer owns the final answer. |
| LangGraph models state, nodes and edges, with a dynamic worker mechanism. | LangGraph documentation | The visual vocabulary of nodes (agent calls) and edges (handoffs). |
| Durable execution gives retries, checkpoint-resume and human-approval signals. | Temporal AI cookbook | Out of scope to build; the approval step and run record echo the ideas. |
| MCP connects agents to tools; A2A connects agents to agents. | A2A documentation | Mentioned for context; neither is used. |
| Subagents have isolated context, tool allowlists, a default nesting limit of 3 and a default concurrency limit of 20. | Claude Code documentation | Informs isolation rules and the worker cap. |
| Tool design: consolidate tools, namespace them, return concise responses. | Anthropic, Writing Tools for Agents | Applies if a search tool is added later. |

---

## A4. Business Requirements

Stakeholder-level needs. Each BR is satisfied by one or more FR or NFR.

| Id | Business requirement | Satisfied by |
|---|---|---|
| BR-01 | Demonstrate, with a working example, what agent orchestration is and when it pays off. | FR-01 to FR-19, A7 |
| BR-02 | Let a non-technical viewer see which agent did what, in what order, with what result. | FR-40 to FR-49 |
| BR-03 | Make the cost and time tradeoff of orchestration versus a single agent visible with real, measured numbers. | FR-19, FR-45, FR-46, NFR-05 |
| BR-04 | Show that orchestration can be controlled and bounded: loops limited, budgets enforced, failures contained. | FR-20 to FR-24 |
| BR-05 | Show a human decision point within an automated process. | FR-04, FR-50 |
| BR-06 | Be shareable: a recorded run can be given to others who can view it without running anything. | FR-60 to FR-62, NFR-04 |
| BR-07 | Be safe on corporate accounts and data: no credential exposure and no execution of untrusted generated text. | NFR-01 to NFR-03 |
| BR-08 | Be simple enough to explain in one sitting and small enough to build quickly; illustrative, not production. | A1.4, scope of FR list |
| BR-09 | Be buildable on more than one platform from the same description so platforms can be compared fairly. | Document rules 1 to 3, A7 |
| BR-10 | Produce evidence: every run leaves a complete, inspectable record. | FR-30 to FR-33, FR-47, FR-62 |

---

## A5. Functional Requirements

Written as "the system shall". Solution-neutral.

### A5.1 Run and input

- FR-01 The system shall accept a free-text question and start a run.
- FR-02 The system shall support three run modes: orchestrated, single-agent, and compare (both, on the same question).
- FR-03 Each run shall have a unique identifier and be stored with its full record.
- FR-04 The system shall support an optional human approval step per run, switched on or off when the run starts.

### A5.2 Agents

- FR-10 The planner shall decompose the question into a bounded number of briefs, each with an objective, a boundary and an output format.
- FR-11 The planner's output shall be validated. An invalid output shall trigger exactly one retry; a second failure shall end the run with a clear error.
- FR-12 Duplicate or overlapping briefs shall be rejected or merged before work starts.
- FR-13 Workers shall execute their briefs in parallel, each seeing only its own brief.
- FR-14 Each worker shall return an answer, a confidence level and a list of key claims.
- FR-15 The synthesizer shall receive the question and all worker outputs, shall be told of any failed brief, and shall state any conflict between workers.
- FR-16 The critic shall score the draft against a rubric (accuracy, completeness, clarity, consistency), and return pass or fail with feedback.
- FR-17 A failing draft shall be revised using the critic's feedback, up to a configured maximum number of revisions.
- FR-18 The capability tier (and so the model) of each role shall be configurable.
- FR-19 A single-agent baseline shall answer the same question with one call, for comparison.

### A5.3 Control

- FR-20 The revision limit shall be enforced outside the models, and the run shall be flagged when the limit is reached.
- FR-21 Each worker shall have a time limit; on expiry the run shall continue with the remaining workers.
- FR-22 A total token budget shall be enforced; on exceeding it the run shall stop cleanly with the best available draft.
- FR-23 A malformed critic reply shall be retried once and then treated as inconclusive and flagged.
- FR-24 All limits (worker count, time limit, revision limit, token budget, output size) shall be changeable without changing the program.

### A5.4 Observability and record

- FR-30 The system shall record every agent call with start and end, role, model, input, output, tokens in and out, seconds, status and parent call.
- FR-31 The system shall record every handoff, with the size of the payload.
- FR-32 The system shall record approval waiting and decisions, critic verdicts and run totals.
- FR-33 Records shall be ordered and time-stamped, and a finished run shall be fully reconstructable from the record alone.

### A5.5 Visualisation

- FR-40 A flow view shall show agents as nodes and handoffs as links, with status, tokens and seconds per node, and a fixed, readable layout for the standard flow including the revision loop-back.
- FR-41 The flow view shall update live while a run is in progress.
- FR-42 State changes shall appear as smooth transitions, not abrupt jumps, with visible effects for: an agent working, an agent finishing, an agent failing or retrying, data travelling along a handoff, fan-out and fan-in, the revision loop-back, and the approval step waiting. The result shall look continuous at a visual update rate of about 3 updates per second or better.
- FR-43 A timeline view shall show one lane per agent with a bar per call over time, so that parallel work is visibly overlapping, and shall distinguish human waiting time from model time.
- FR-44 A conversation view shall list the messages passed between agents in order, and selecting any call shall show its full input, full output, model, tokens, seconds and retry count, with a difference view between successive drafts.
- FR-45 A cost view shall show tokens and seconds by role, estimated money cost when rates have been supplied, and the critical path (the chain of calls that determined total elapsed time).
- FR-46 A compare view shall show orchestrated and single-agent results side by side on tokens, seconds, number of calls, answer length and critic score (scored by the same critic for fairness), shall state the ratios, shall not declare a winner, and shall label results as single samples.
- FR-47 A raw record view shall show all recorded events, filterable and downloadable.
- FR-48 A replay facility shall let a viewer play, pause, change speed and move to any point of a finished run, with the flow and timeline views following.
- FR-49 A legend shall explain the visual encoding.

### A5.6 Human approval

- FR-50 When approval is switched on, the system shall pause before synthesis and show the worker answers. The human may approve, edit a worker answer, or reject. A rejection ends the run with status rejected. The decision shall be recorded.

### A5.7 Sharing and reuse

- FR-60 A finished run shall be exportable as one self-contained file that can be viewed offline and contains the flow, timeline and conversation views and the replay facility.
- FR-61 A finished run shall be exportable as a plain-text diagram of its flow.
- FR-62 Past runs shall be listable and re-openable.

### A5.8 Configuration

- FR-70 Models per role, limits, rubric weights and cost rates shall be held outside the program logic.
- FR-71 The instructions given to each agent (prompts) shall be editable separately from the program logic.

---

## A6. Non-Functional Requirements

- NFR-01 Credentials shall never appear in code, configuration, logs, run records or exports.
- NFR-02 All text produced or received by an agent is untrusted. It shall never be executed, interpreted as markup, or concatenated into markup or script anywhere in the system, including exports. Labels in diagrams shall be fixed role names, not model text.
- NFR-03 Only corporate-approved model access shall be used.
- NFR-04 Exports shall work offline with no external network access.
- NFR-05 Any token count that is estimated rather than measured shall be labelled as an estimate in every view.
- NFR-06 Display shall be a pure function of the recorded events: the same record shall always produce the same display.
- NFR-07 Usability: a first-time viewer shall be able to answer "which agent said what to whom, and what did it cost" using the visual interface alone, without reading code or logs.
- NFR-08 Parallel efficiency: the worker phase shall complete in no more than 1.5 times the duration of the slowest single worker.
- NFR-09 Estimated cost values shall be shown only when rates have been supplied by the owner; rates shall never be guessed.

---

## A7. Acceptance

The same acceptance suite applies to every build (Parts B and C).

### A7.1 Test questions

| Id | Question type | Example | Expected behaviour | What it shows |
|---|---|---|---|---|
| Q1 | Narrow factual comparison | "What is the difference between a B-tree and an LSM-tree index?" | A single agent is nearly as good; orchestrated costs several times more tokens | Orchestration is not free; small tasks do not need it |
| Q2 | Multi-part research question | "Compare five approaches to long-term memory for LLM agents, covering storage, retrieval, cost and failure modes." | Orchestrated answer is more complete (higher completeness score) | Where decomposition and parallelism pay off |
| Q3 | Deliberately vague question | "Tell me about agents." | The planner makes arbitrary splits; the critic flags low focus; the revision limit may be reached | Garbage in gives orchestrated garbage out; the limit protects cost |

### A7.2 Success criteria

- SC-1 In compare mode the report shows orchestrated token use as a multiple of single-agent token use, computed from recorded usage, not asserted. (BR-03, FR-46)
- SC-2 The worker phase is within 1.5 times the slowest single worker, and the timeline shows overlapping bars. (NFR-08, FR-43)
- SC-3 The flow view matches the record exactly: every recorded call appears as a node, every recorded handoff as a link, and nothing else appears. (FR-33, NFR-06, FR-40)
- SC-4 The revision limit and the invalid-output retry both demonstrably fire under test. (FR-11, FR-20)
- SC-5 A first-time viewer can answer "which agent said what to whom, and what did it cost" using only the visual interface. (NFR-07)
- SC-6 The exported file works offline in a browser with no network access. (FR-60, NFR-04)
- SC-7 Hostile text (script and markup strings) in agent output is shown as plain text and nothing executes. (NFR-02)
- SC-8 State changes in the flow view appear as smooth transitions during a live run and during replay. (FR-42)

### A7.3 Failure scenarios (mapped to the MAST failure groups)

| Group | Injected fault | Expected response | Requirement |
|---|---|---|---|
| System design | Planner returns two near-identical briefs | Duplicates rejected or merged; event recorded | FR-12 |
| System design | Planner returns 12 briefs | Capped to the maximum; event recorded | FR-10, CR-2 |
| Inter-agent misalignment | A worker ignores its output format | One retry, then marked failed; synthesizer told | FR-14, CR-3 |
| Inter-agent misalignment | Two workers give contradictory claims | Synthesizer states the conflict; critic's consistency score reflects it | FR-15, FR-16 |
| Task verification | Critic always returns fail | Loop stops at the limit; limit-reached flag visible | FR-17, FR-20 |
| Task verification | Critic returns malformed output | One retry, then inconclusive and flagged | FR-23 |
| Infrastructure | A worker times out | Run continues without it | FR-21 |
| Infrastructure | Token budget exceeded mid-run | Clean stop with best draft and budget-exceeded flag | FR-22 |
| Security | Agent output contains script and markup text | Displayed as plain text only | NFR-02 |

---

## A8. Assumptions, Risks, Open Decisions, Glossary

### A8.1 Assumptions

- The audiences in A1.2 are assumed and have not been confirmed.
- Model access is available through the corporate-approved route for the builds.
- Single runs are samples; a few runs prove little (see A8.2).
- Cost rates will be supplied by the owner; until then only tokens are shown.

### A8.2 Risks (solution-neutral)

- **Single-run variance:** one run of each question proves little; the compare view labels results as single samples. A repeat option is a candidate extension.
- **Judge noise:** the critic is itself a model and may be inconsistent, especially a weaker model; this weakens the compare view.
- **Untrusted text in the display:** model output flowing into a page is the main security risk of any visual interface (NFR-02).
- **Token estimates:** if a model service does not return usage, counts are estimates (NFR-05).
- **Over-claiming:** the demo must not suggest orchestration always wins; Q1 is included to show otherwise.

### A8.3 Open decisions for the owner

- Confirm or correct the audiences in A1.2.
- Supply cost rates per model when wanted (NFR-09).
- Decide whether the repeat-run option (A8.2) is in scope.

### A8.4 Possible extensions (not in scope now)

- Give workers a real search tool, then show tool calls as extra nodes in the flow view.
- Add an initial routing step (simple versus complex question) that skips orchestration for easy questions.
- Add durable checkpointing so a run can resume after a crash.
- Add voting: run the critic several times and take a majority.
- Repeat runs with averaged results.

### A8.5 Glossary

| Term | Meaning |
|---|---|
| Agent | A model call (or a short loop of calls) given a role, instructions and inputs |
| Orchestrator | The control layer that sequences agents, enforces limits and owns the final answer |
| Brief | The planner's instruction to one worker: objective, boundary and output format |
| Handoff | Data passing from one agent call to another |
| Span or call | One recorded agent invocation |
| Critic | The agent that scores a draft against a rubric |
| Revision loop | Synthesize, criticise, revise, repeated at most a set number of times |
| Capability tier | Strong, mid or cheap: an abstract class of model, resolved to a named model in each build |
| Record | The ordered, time-stamped list of observables for a run (A3.6) |

---
---

# PART B: BUILD 1, PYTHON AND STREAMLIT

Part B describes how Build 1 meets Part A. Every phase lists the requirements it covers.

---

## B1. Build Decisions and Constraints

### B1.1 Backend and models

- Backend chosen by the owner: the Siemens Claude proxy at `https://llm.sdc.siemens.cloud`. The local LiteLLM and Qwen route is deferred and not implemented.
- The API key is read from the `ANTHROPIC_API_KEY` environment variable. It is never written to code, configuration, logs, run records or exports (NFR-01).
- Model IDs, taken from the owner's Claude Code settings:
  - Planner: `claude-opus-5-5`
  - Critic: `claude-opus-5-5`
  - Synthesizer: `claude-sonnet-5-5`
  - Single-agent baseline: `claude-sonnet-5-5`
  - Worker: `claude-haiku-4-5-20251001`
- Cost rates in `config.json` are blank (null), because the owner has not supplied them. The cost view shows tokens only until they are filled in (NFR-09).

### B1.2 Environment (checked 2026-10-08)

- Python 3.12 in conda environment `py_claude` (the only permitted Python location is `C:\miniforge3`; environments live under `C:\miniforge3\envs\`).
- Installed in `py_claude`: streamlit 1.57.0, altair 6.1.0, httpx 0.28.1, requests, pandas, and pytest 9.1.1 (installed this session with the owner's approval).
- Not installed and not needed: the `anthropic` Python package and the Graphviz `dot` binary.
- Engine uses the standard library plus httpx: `concurrent.futures`, `json`, `time`, `dataclasses`, `argparse`, `uuid`, `threading`, `queue`.

### B1.3 Rules this build must follow

- ASCII only in all source files, comments and generated files. No Unicode box-drawing or decorative characters.
- No hard-coded colours, model names, rates or limits in code. They live in `config.json` and `viewer_style.json`.
- The engine does not run git or spawn processes other than the program itself.
- Siemens security: no credentials in code or committed files.
- Zscaler state matters: if a model call fails to connect, check the Zscaler state first.

### B1.4 Escaping rule (implements NFR-02)

All agent input and output is untrusted. It reaches the browser only as JSON data inside a data block and is displayed by inserting it as text, never concatenated into HTML, SVG or script text. Node labels in the SVG are fixed role names, not model text. The HTML export escapes all embedded text, and the JSON block is serialised so that it cannot close its own script tag. A test feeds an event whose text contains script and markup strings and asserts that nothing executes and nothing renders as markup (SC-7).

---

## B2. Component Design and Folder Layout

### B2.1 Components

| Component | File | Responsibility |
|---|---|---|
| Configuration | `config.json`, `viewer_style.json` | Models, backend, limits, rates, rubric weights, colours and layout constants (FR-70) |
| Model wrapper | `llm.py` | `chat(model, system, user)` returning text, tokens in, tokens out, seconds; retries; authentication fallback (DONE) |
| Events | `events.py` | Event dataclass, event bus, JSONL writer and reader |
| Agents | `agents.py` | Planner, worker, synthesizer, critic and single-agent functions |
| Engine | `engine.py` | Orchestrated run, single run, compare run, gate handling, limit enforcement |
| CLI | `desk.py` | Command-line entry point |
| Viewer | `viewer.py` | Streamlit application |
| Renderers | `render.py` | Flow SVG, timeline data, draft diff, Mermaid export, HTML export |
| Player | `assets/player_template.html` | Self-contained SVG, CSS and JavaScript animation player |
| Prompts | `prompts/*.md` | Instructions for each agent (FR-71) |
| Tests | `tests/` | Unit, failure-injection and escaping tests |
| Runs | `runs/` | One folder per run: `events.jsonl`, `final.md`, `trace.mmd`, `trace.html` |

### B2.2 Layout

```
research_desk/
  workplan.md            this document
  config.json            backend, models, limits, rates, rubric weights   (exists)
  viewer_style.json      status colours, fonts, layout constants
  llm.py                 model wrapper                                    (exists)
  events.py              Event dataclass, EventBus, JSONL writer and reader
  agents.py              planner, worker, synthesizer, critic, single_agent
  engine.py              orchestrated, single and compare runs, gate handling
  desk.py                CLI entry point
  viewer.py              Streamlit app (6 tabs, replay player, gate panel)
  render.py              flow graph SVG, timeline data, draft diff, Mermaid export, HTML export
  assets/
    player_template.html self-contained SVG, CSS and JS animation player
  prompts/
    planner.md           system prompt and output format
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
    test_escaping.py
    questions.json       the three test questions with expected behaviours
  runs/
```

### B2.3 Control logic (implements A3.4)

- The planner's reply must parse as JSON and match the schema. One automatic retry with the parse error appended; a second failure ends the run with an error event.
- Worker count is the smaller of the planner's count and `limits.max_workers`.
- Each worker has a timeout (`limits.worker_timeout_s`). A timeout produces an agent-failed event; the run continues, and the synthesizer is told which brief has no answer.
- The critic loop runs at most `limits.max_revisions` times, then returns the latest draft flagged `cap_reached`.
- If cumulative tokens exceed `limits.token_budget`, the run stops with the best draft and a `budget_exceeded` flag.

---

## B3. Event Log Format (implements A3.6, FR-30 to FR-33)

Stored as JSON Lines, one event per line, flushed on every write so a viewer tailing the file sees events immediately. Every event carries `run_id`, a monotonic `seq` and an ISO timestamp.

| Event type | Fired when | Key fields |
|---|---|---|
| `run_started` | Run begins | run_id, mode, question, configuration snapshot |
| `agent_started` | An agent call begins | span_id, parent_span_id, role, model, input_text, ts |
| `agent_finished` | An agent call ends | span_id, output_text, tokens_in, tokens_out, seconds, status, estimated |
| `agent_failed` | Error or timeout | span_id, error, retry_count |
| `handoff` | Data passes between spans | from_span, to_span, payload_preview, payload_chars |
| `gate_waiting` | Approval step opens | gate_id, summary |
| `gate_resolved` | Human decides | gate_id, decision, edited_text (optional) |
| `critic_verdict` | Critic returns | scores, pass, feedback, loop_index |
| `run_finished` | Run ends | final_answer, totals, cap_reached, budget_exceeded, status |

Design principle: the engine does not talk to any interface. It emits events. The CLI, the viewer and the exporters are all consumers of the same stream. This gives live view, replay and later analysis from one mechanism (NFR-06).

---

## B4. Interfaces

### B4.1 Command line: `desk.py`

```
python desk.py "Compare vector databases and graph databases for CRM"
python desk.py "..." --single            single-agent baseline only
python desk.py "..." --compare           run orchestrated AND single, print comparison table
python desk.py "..." --approve           pause for human approval before synthesis (terminal prompt)
python desk.py --replay runs/<run_id>    re-print a finished run from its event log
python desk.py --export runs/<run_id>    write trace.mmd and trace.html
```

Terminal output while running: one line per event with role, model, elapsed time and token counts, then a final summary table. This is the fallback view for headless use. (A `--backend` switch is not needed while only the proxy is implemented.)

### B4.2 Web viewer: `viewer.py` (Streamlit)

Streamlit is chosen because it is already used elsewhere in this workspace and needs no front-end build step. The viewer is a separate process from the engine. It either launches a run in a background thread and tails the event file, or opens a finished run from `runs/`.

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

### B4.3 Static export

`--export` produces:
- `trace.mmd`: a Mermaid diagram of the run (secondary artefact for sharing; implements FR-61).
- `trace.html`: a single self-contained HTML file (inline CSS and JavaScript, no network, no CDN) containing the animated flow view, timeline, conversation and replay player (implements FR-60). Source is ASCII only.

---

## B5. Visualisation and Animation Design

### B5.1 The six views (implement FR-40 to FR-49)

**View 1: Flow graph (who talked to whom).**
- Nodes are agent calls; edges are handoffs. Layout is left to right: planner, workers (stacked), synthesizer, critic, with a curved back-edge from critic to synthesizer for each revision.
- Node colour shows status: grey waiting, blue running, green finished, red failed, amber retried.
- Node label shows role, model tier, tokens and seconds. Edge label shows payload size.
- Clicking a node opens the inspector (View 3) for that call.
- Implementation: hand-drawn SVG generated in Python (`render.py`), animated in the browser by the JavaScript player (B5.2). The layout is fixed because the topology is fixed. No Graphviz, no Mermaid library, no extra install.

**View 2: Timeline (when did things happen, and what ran in parallel).**
- One horizontal lane per agent, time on the x-axis, a bar per call from start to finish. The three workers appear as overlapping bars; a sequential run would show a staircase.
- Critic and revision loops appear as alternating bars at the end. Approval waiting time is drawn as a hatched bar so human latency is distinguishable from model latency.
- Implementation: Altair horizontal bars (Altair ships with Streamlit), refreshed on a fragment tick.

**View 3: Conversation and inspector (what exactly was said).**
- A chat-style transcript ordered by `seq`, each message tagged with role and span id: planner to workers (briefs), workers to synthesizer (answers), synthesizer to critic (draft), critic to synthesizer (feedback).
- Selecting any span shows full input, full output, model, tokens, seconds, retry count, and a difference view between draft N and draft N+1.
- A toggle highlights text that was passed on versus text that was dropped, making information loss between agents visible.

**View 4: Cost and efficiency (what did it cost).**
- Stacked bar of tokens by role. Table: calls, tokens in, tokens out, seconds and, when rates are supplied, estimated money cost per role (clearly labelled as estimates). A critical-path indicator shows which chain of calls determined total elapsed time.

**View 5: Compare (is orchestration worth it).**
- Side-by-side orchestrated and single-agent answers. Metrics row: total tokens, total seconds, number of calls, answer length, critic score of each (same critic for both). The verdict line states ratios only, for example "orchestrated used 6.2x tokens and 1.4x time for +1.3 rubric points"; it never declares a winner. Results are labelled as single samples.

**View 6: Raw events (trust but verify).**
- The event stream as a filterable table with a download button, so the other five views can be audited against the underlying data.

**Cross-cutting aids.**
- **Replay player:** play, pause, speed (0.5x, 1x, 2x, 4x) and a scrubber over `seq` replay a finished run, with the flow graph and timeline revealing events progressively. The same player is used in the live viewer and in `trace.html`.
- **Approval panel:** when `gate_waiting` fires, a banner shows the worker answers with Approve, Edit and Reject buttons. Approve continues; Edit lets the human alter a worker answer before synthesis; Reject ends the run with status rejected. The decision is logged as `gate_resolved`.
- **Legend:** a small fixed legend explains colours and shapes.

### B5.2 Animation design (implements FR-41, FR-42, SC-8)

**What animation means here.** Agent events arrive seconds apart, not several per second, so the animation is smooth state change between events plus small motion effects, not frame-by-frame video. A tick rate of about 3 per second (roughly 333 ms) is enough because the browser interpolates between ticks.

| Effect | Trigger event | Visual |
|---|---|---|
| Node waiting to running | `agent_started` | Fill fades from grey to blue; a slow pulse ring while running |
| Node finished | `agent_finished` | Fill fades to green; token count ticks up to its final value |
| Node failed or retried | `agent_failed` | Fill red or amber; brief shake |
| Handoff | `handoff` | A small dot travels along the edge; edge thickness reflects payload size |
| Fan-out and fan-in | Planner finishes; workers finish | Three dots leave the planner together; three converge on the synthesizer |
| Revision loop | `critic_verdict` with fail | A dot travels the back-edge from critic to synthesizer; a loop counter increments |
| Gate waiting | `gate_waiting` | Node outline blinks until `gate_resolved` |
| Timeline bars | `agent_started` to `agent_finished` | Bar grows to the right in step with the clock |
| Counters | Every event | Status-bar totals (tokens, seconds, calls) count up smoothly |

**Player architecture.**
- One self-contained player (`assets/player_template.html`): inline SVG, CSS and a small script, no network access, no external libraries, ASCII only.
- The Python side renders the static SVG (nodes, edges, lanes) and embeds the event list as a JSON data block.
- The script keeps its own clock. Given the event list it computes, for any time t, the state of every node and edge, and applies it by switching CSS classes. CSS transitions of about 0.3 s supply the smoothness, so the redraw rate from Python can stay low.
- Replay mode: the whole event list is loaded once; play, pause, speed and scrubber are handled entirely in the browser.
- Live mode: a Streamlit fragment with `run_every` of about 1 to 2 seconds appends new events. Browser clock and transitions do the smoothing, so Python does not need three redraws per second.
- Export mode: the identical template, written out as `trace.html`, replays offline.

**Delivery inside Streamlit.**
- Use `st.html` with `unsafe_allow_javascript=True`. Do not use `components.html` (deprecated in Streamlit 1.56.0; the installed version is 1.57.0).
- Open unknowns, to be settled by the Phase 9B spike before the viewer is built: whether the script survives or restarts on a rerun, and whether the sanitiser (DOMPurify) leaves the SVG and CSS animation intact when JavaScript is enabled.
- Fallback 1: show `trace.html` through an iframe pointing at a file, or open the export in a browser tab. Whether the iframe route is itself deprecated has not been checked.
- Fallback 2 (last resort): redraw SVG from Python on a fragment timer. From reasoning, not a test: replacing the whole element each tick means CSS transitions have no previous state to animate from, so changes will snap.

**Timeline and cost charts.** Altair charts redraw on a fragment tick and need no animation beyond growing bars; about 1 to 2 redraws per second is acceptable.

### B5.3 Decision record: flow graph rendering

Decision: hand-drawn SVG with a browser-side player. Date: 2026-10-08. Based on documentation fetched that day plus general knowledge; items marked "not verified" were not tested on this machine.

| Option | Verdict | Reason |
|---|---|---|
| Hand-drawn SVG plus CSS and JavaScript player | CHOSEN | Fixed topology makes layout trivial; per-node status colours, click handling, replay and offline export come from one code path; no install |
| `st.graphviz_chart` with a DOT string | Not chosen | Renders in the browser (d3-graphviz with Graphviz WebAssembly) and docs say the `graphviz` pip package must be installed, with no mention of `dot.exe`; but the whole graph is re-laid-out on each update so nodes can jump, and there is no evidence of smooth transitions in Streamlit's wrapper. Not tested here. |
| Graphviz with `dot.exe` | Not chosen | A standalone program (graphviz.org, winget or conda-forge), not a Python package; may need admin rights or approval on a managed machine; the `graphviz` pip package is only a wrapper around it |
| Mermaid | Secondary only | Text export for sharing; weak for status colours, click handling and animation |
| pyvis / vis-network | Rejected | Physics layout keeps nodes moving; wrong kind of motion for showing state (not verified here) |
| networkx plus matplotlib | Rejected | Static images; layouts unsuited to layered flows (not verified here) |
| Plotly or Altair with manual nodes | Rejected | No better than hand SVG, more awkward for arrows and curves |
| Cytoscape.js with dagre layout | Upgrade path | Built-in animation and interaction; worth the JavaScript effort only if the topology becomes dynamic (tools, nested subagents, routers) |

Graphviz remains useful as a one-time layout engine if the graph ever becomes arbitrary; out of scope now.

### B5.4 Streamlit documentation findings that shaped Part B

| Finding | Source | Consequence |
|---|---|---|
| `st.components.v1.html` deprecated in 1.56.0 and to be removed; the custom-components intro page still recommends it, so the docs contradict each other | Streamlit docs | Do not build on it; the deprecation notice is trusted |
| `st.html` strips JavaScript by default (DOMPurify); `unsafe_allow_javascript=True` runs scripts; content is not iframed; docs do not say whether script state survives reruns | Streamlit docs | Player delivered through `st.html`; behaviour verified by the spike |
| Both HTML pages warn never to pass untrusted content, explicitly including LLM output | Streamlit docs | Escaping rule B1.4 |
| `st.fragment(run_every=...)` reruns a fragment on a timer without rerunning the whole app | Streamlit docs | Live refresh in live mode |
| SMIL SVG animation: an MDN summary called it deprecated but the page did not say so (unverified); CSS and the Web Animations API are the documented modern routes | MDN (summarised) | CSS transitions and JavaScript, not SMIL |

---

## B6. Phases, Tasks and Done-When Criteria

Requirement coverage is listed per phase.

### Phase 0: Setup and confirmation - PARTIAL
Covers: BR-07, NFR-01, NFR-03, FR-70.
- Create the folder skeleton in B2.2. (NOT DONE: only `config.json` and `llm.py` exist so far; create prompts/, tests/, runs/ and assets/ when Phase 2 starts.)
- Verify `py_claude` exists and which packages are installed. (DONE 2026-10-08; pytest installed with the owner's approval.)
- Obtain from the owner: backend choice, model names for each tier, endpoint settings. (DONE: Siemens proxy; Opus plans and judges, Sonnet synthesizes, Haiku works; endpoint and model IDs from the owner's Claude Code settings; key from the environment.)
Done when: skeleton exists, environment check printed, `config.json` filled with owner-supplied values.

### Phase 1: Model wrapper - DONE 2026-10-08
Covers: FR-18, FR-24, FR-70, NFR-01, NFR-05.
Result: `python llm.py --ping` succeeded on all three tiers with real (not estimated) token counts. Haiku 1.4 s, Sonnet 2.2 s, Opus 1.8 s for a trivial prompt.
- Implement `chat()` with timeouts and one retry on transient errors; authentication tries `x-api-key` first and falls back to a bearer header.
- Return text plus token counts; if the service omits usage, estimate by character count and mark `estimated: true`.
- Add a `--ping` self-test.
Done when: one call on each tier prints a reply and token usage. (MET)

### Phase 2: Events and record
Covers: FR-30 to FR-33, NFR-06.
- Define the Event dataclass and all event types in B3.
- JSONL writer (flush on every event) and reader; event bus with subscriber callbacks; the terminal printer is the first subscriber; span id and parent span id helpers.
Done when: a dummy run with fake agents produces a valid `events.jsonl` that round-trips through the reader, with correct parent-child links.

### Phase 3: Planner
Covers: FR-10, FR-11, FR-12, CR-1, CR-2, CR-6.
- Prompt that outputs strict JSON: `{"briefs":[{"id","objective","boundary","output_format"}]}`.
- Schema validation, one retry with the parse error appended, then an abort event.
- Enforce a count between 2 and `max_workers`; reject duplicate or overlapping objectives (identical `objective` strings as the first check).
Done when: valid output passes, malformed output triggers exactly one retry, and a second failure aborts cleanly.

### Phase 4: Parallel workers
Covers: FR-13, FR-14, FR-21, CR-3, NFR-08.
- Run briefs through a `ThreadPoolExecutor` sized to the brief count (capped by configuration).
- Each worker returns `{"answer","confidence","key_claims"}`; per-worker timeout; partial-failure handling per B2.3.
- Emit `handoff` events from planner to each worker.
Done when: three simulated 2-second workers finish in about 2 seconds total (the test asserts under 3.5 s), and one forced timeout still lets the run continue.

### Phase 5: Synthesizer
Covers: FR-15.
- Build the synthesis prompt from the question plus all worker outputs, listing any failed briefs explicitly and requiring any conflict to be stated.
- On revision, include the critic feedback and the previous draft.
Done when: a run produces a draft that references all non-failed worker outputs.

### Phase 6: Critic loop
Covers: FR-16, FR-17, FR-20, FR-23, CR-4, CR-7.
- Rubric (accuracy, completeness, clarity, consistency with worker claims), each scored 1 to 5, with weights from configuration and a pass threshold.
- Critic returns strict JSON (scores, pass, feedback); validate and retry once.
- Loop controller in code with `max_revisions`; emit `critic_verdict` on each pass; set `cap_reached`.
Done when: a forced-fail critic stub stops at exactly the cap, and a pass on the first try produces zero revisions.

### Phase 7: Single-agent baseline and compare
Covers: FR-02, FR-19, FR-46, BR-03, SC-1.
- `single_agent()` makes one call with the question and a general instruction.
- Compare mode runs both, then scores both answers with the same critic prompt.
- Comparison table: tokens, seconds, calls, answer length, rubric score, ratios.
Done when: `--compare` prints the table and writes both runs under `runs/`.

### Phase 8: CLI polish, token budget and replay
Covers: FR-01, FR-03, FR-04, FR-22, FR-50 (terminal form), FR-62, CR-5.
- `--approve` terminal gate, `--replay`, `--export` wiring, token-budget enforcement, exit codes, error messages.
Done when: every CLI flag in B4.1 works against a real run.

### Phase 9: Renderers and animation player
Covers: FR-40 to FR-42, FR-43 (data), FR-48, FR-49, FR-60, FR-61, NFR-02, NFR-04, SC-3, SC-6, SC-7, SC-8.
- `render.py`: SVG generation of the fixed flow layout (planner, up to `max_workers` worker nodes, synthesizer, critic, back-edge) with fixed role labels; timeline data frame; draft-diff helper; Mermaid text export.
- `assets/player_template.html`: self-contained player implementing the effects in B5.2: own clock, CSS-transition state changes, travelling handoff dots, play, pause, speed, scrubber. Event list embedded as a JSON data block; all text inserted as text, never as markup (B1.4).
- Static HTML builder: injects the SVG and the serialised event list into the template and writes `trace.html`.
- A test rebuilds the node and edge set from `events.jsonl` and compares it with the SVG (SC-3).
- An escaping test per B1.4 (SC-7).
Done when: `trace.html` opens offline in a browser, animates a recorded run end to end at 1x and 4x, the scrubber jumps correctly, `trace.mmd` pastes into a Mermaid renderer, and the escaping test passes.

### Phase 9B: Animation spike (throwaway, before Phase 10)
Purpose: settle the unknowns in B5.2 before building the viewer around them.
- Make a minimal Streamlit page that embeds a tiny SVG with a CSS transition and a script timer through `st.html(unsafe_allow_javascript=True)`.
- Check four things: (1) does DOMPurify keep the SVG and CSS intact; (2) does the script run at all; (3) does the script keep its state or restart when a fragment with `run_every` of 1 second reruns; (4) does a node colour change animate smoothly or snap.
- Try the fallbacks in B5.2 only if needed, and note whether an iframe route is deprecated.
- Record results in the decision record (B5.3). The spike code is discarded afterwards.
Done when: the delivery route for Phase 10 is chosen from observed behaviour, not documentation alone.

### Phase 10: Streamlit viewer
Covers: FR-01 to FR-04, FR-41, FR-43 to FR-50, FR-62, NFR-07.
- Run panel (question, mode, approval toggle) launching the engine in a background thread.
- Live tailing of `events.jsonl` with a fragment refresh (`run_every` about 1 to 2 seconds).
- Flow tab embeds the Phase 9 player using the route chosen in Phase 9B; Timeline and Cost tabs use Altair.
- Tabs 1 to 6 as specified in B5.1; replay player; approval panel with Approve, Edit and Reject; status bar; legend.
- Open-existing-run picker reading `runs/`.
- All displayed agent text follows the escaping rule (B1.4).
Done when: a live run visibly lights up the flow graph with smooth transitions, the timeline shows overlapping worker bars, and approving at the gate resumes the run.

### Phase 11: Tests and evaluation
Covers: A7 in full, SC-1 to SC-8.
- Unit tests listed in B2.2; failure-injection tests for every row of A7.3.
- Run the three test questions in compare mode and record results in `runs/` plus a short findings note (written only on request).
- Ask a first-time viewer to answer the SC-5 question using only the viewer.
Done when: tests pass and the three questions have comparison results saved.

---

## B7. Traceability: Requirements to Phases

| Requirement group | Covered in |
|---|---|
| FR-01 to FR-04 (run and input) | Phases 8, 10 |
| FR-10 to FR-19 (agents) | Phases 1, 3, 4, 5, 6, 7 |
| FR-20 to FR-24 (control) | Phases 1, 4, 6, 8 |
| FR-30 to FR-33 (record) | Phase 2 |
| FR-40 to FR-49 (visualisation) | Phases 9, 10 |
| FR-50 (approval) | Phases 8 (terminal), 10 (viewer) |
| FR-60 to FR-62 (sharing) | Phases 8, 9, 10 |
| FR-70, FR-71 (configuration) | Phases 0, 1, 3 to 6 |
| NFR-01 to NFR-09 | Phases 0, 1, 4, 9, 10, 11 |
| SC-1 to SC-8, A7.3 failure scenarios | Phase 11 |

---

## B8. Build Risks and Open Unknowns

- **Backend and models: resolved 2026-10-08.** Siemens proxy; tiers as in B1.1. The local LiteLLM route is deferred.
- **Animation delivery is unverified.** `st.html` with JavaScript may sanitise SVG or restart scripts on rerun; the Phase 9B spike decides the route. If every in-Streamlit route fails, the fallback is to open `trace.html` in a browser tab and keep Streamlit for the non-animated tabs.
- **Streamlit docs contradict each other** on `components.html` (deprecated in 1.56.0 versus still recommended on the intro page). The deprecation notice is trusted; recheck the docs if Streamlit is upgraded.
- **Untrusted text in HTML.** Model output flowing into the page is the main security risk of the viewer; see B1.4 and its test.
- **Judge noise.** A weaker critic model would make the compare view noisy; Opus is used for the critic for that reason.
- **Token counts.** If the proxy omits usage on some responses, counts are estimates and are labelled as such.
- **Zscaler.** Model calls through the proxy need the corporate network path; if a call fails to connect, check Zscaler state first.
- **Single-run variance.** Results are single samples and are labelled so; a repeat option is a candidate extension (A8.4).
- **Graphviz is not used.** It is a separate program (`dot.exe`), not a Python package, and the viewer does not need it. Revisit only if the graph topology becomes dynamic (B5.3).

---

## B9. Build-Specific Extensions

- Replace the hand-drawn SVG with Cytoscape.js (dagre layout) if the topology becomes dynamic, to gain automatic layout, built-in animation and click handling.
- Look at Streamlit's newer two-way custom components (not read during this planning) if the player ever needs to send events back to Python.
- Port the same flow to LangGraph or the Claude Agent SDK to compare behaviour across frameworks.
- Add a Mermaid or SVG per-run snapshot for the compare view.

---

## B10. Status Log

| Date | Item | State |
|---|---|---|
| 2026-10-08 | Backend, models and key route decided | DONE |
| 2026-10-08 | pytest installed in `py_claude` | DONE |
| 2026-10-08 | `config.json` and `llm.py` written; proxy ping to Haiku, Sonnet and Opus succeeded | DONE |
| 2026-10-08 | Folder skeleton (prompts, tests, runs, assets) | NOT DONE |
| 2026-10-08 | Phases 2 to 11, including spike 9B | NOT STARTED |

---
---

# PART C: BUILD 2, MENDIX (PARALLEL, ALTERNATIVE) - SKELETON

Status: skeleton only. Nothing in this part has been verified on this machine. Items marked "unverified" come from the owner's wiki or general knowledge and must be confirmed before any build decision.

---

## C1. Purpose and Relationship to Part A

- Build the same system described in Part A on the Mendix low-code platform, independently of Part B.
- Part A is unchanged by this build. If Mendix cannot meet a requirement, the shortfall is recorded in the gap table (C4), not hidden by changing Part A.
- Both builds run the same acceptance suite (A7) so that results are comparable.
- Learning value: it shows how an agent orchestration design maps onto a visual, model-driven platform, and where that mapping is awkward.

---

## C2. Starting Facts (from the owner's wiki and notes; unverified for this use)

Source: `Notes_LLMwiki/wiki/entities/mendix.md` and `Mendix_ClaudeCode.md` in the workspace.

- Mendix is an enterprise low-code platform, acquired by Siemens in 2018. Main parts: Studio Pro (IDE), domain model (entities, attributes, associations), microflows (visual business logic), pages (UI).
- Studio Pro 11.2 introduced an MCP server integration (port 7782). The Concord terminal (Marketplace) connects the Mendix AI assistant to external models, with Claude recommended. A documented workflow exists in which Claude builds Mendix apps inside Studio Pro, and `Mendix_ClaudeCode.md` records a full example session (a Plant Asset Care application).
- Mendix has a native integration with Altair Graph Studio (reading and writing knowledge-graph data).
- Deployment options include Mendix Cloud, Mendix Cloud Dedicated, private cloud and on-premises.
- Not known: whether Studio Pro is installed on this machine, which version, and which licence or environment is available. These must be checked first.

---

## C3. Concept Mapping (hypotheses to test)

| Part A concept | Likely Mendix concept | Confidence |
|---|---|---|
| Run, call (span), event, handoff | Persistent entities in the domain model (Run, Span, Event) | High (general knowledge) |
| Planner, worker, synthesizer, critic calls | Microflows that call the model service over REST and parse JSON | High (general knowledge) |
| Prompts held outside the logic (FR-71) | Constants or a Prompt entity editable in an admin page | Medium |
| Configuration (FR-70) | App constants and a Settings entity | High |
| Question entry and run controls | A page with a form and microflow buttons | High |
| Approval step (FR-50) | A page with Approve, Edit and Reject buttons, or a workflow user task | Medium (workflow feature unverified) |
| Parallel workers (FR-13) | Possibly the task queue, workflow parallel split, or a custom Java action with threads | Low (unverified; see C4) |
| Flow view with animation (FR-40 to FR-42) | A custom pluggable widget or an HTML and JavaScript widget | Low (unverified; likely the hardest part) |
| Timeline and cost charts (FR-43, FR-45) | A charting widget from the Marketplace | Medium (unverified) |
| Offline export (FR-60) | A Java action or microflow generating a file from a template | Low (unverified) |

---

## C4. Requirement-to-Platform Gap Table (to be completed)

Status values: UNKNOWN (not researched), LIKELY (plausible from general knowledge), GAP (known not to fit), OK (verified).

| Requirement | Mendix approach | Status | To check |
|---|---|---|---|
| FR-01 to FR-04 | Page, microflows, run entity | LIKELY | Basic modelling |
| FR-10 to FR-12 | REST call to the model service, JSON import mapping, validation microflow | LIKELY | Can the app reach the model service endpoint? |
| FR-13 (parallel workers) | Unknown mechanism | UNKNOWN | Microflows run step by step; check task queue, workflows and Java actions |
| FR-14 to FR-19 | Microflows | LIKELY | JSON handling of model replies |
| FR-20 to FR-24 | Microflow logic and constants | LIKELY | Time limits per call |
| FR-30 to FR-33 | Event entity, ordered by sequence and time | LIKELY | Event volume and write cost |
| FR-40 to FR-42 (animated flow) | Custom widget | UNKNOWN | Whether a widget can embed SVG and script; effort to build |
| FR-43, FR-45 (timeline, cost) | Charts | UNKNOWN | Widget availability |
| FR-44, FR-47 (inspector, raw table) | Data grid and detail pages | LIKELY | Basic UI |
| FR-46 (compare) | Page with computed values | LIKELY | None |
| FR-48 (replay) | Custom widget or timed page refresh | UNKNOWN | Same as FR-42 |
| FR-50 (approval) | Page or workflow user task | LIKELY | Pausing a run while waiting for a human |
| FR-60 to FR-62 (export, reopen) | File generation; list page | UNKNOWN for the export | Self-contained offline file |
| NFR-01 (no credentials in the record) | Encrypted or environment-specific constants | LIKELY | How secrets are stored and kept out of exports |
| NFR-02 (untrusted text) | Platform output encoding plus rules for any custom widget | UNKNOWN | Default encoding behaviour; custom widget rules |
| NFR-03 (approved model access only) | Same corporate route as Build 1 | UNKNOWN | Whether the Mendix runtime may reach the proxy (a cloud-deployed app may not) |
| NFR-08 (parallel efficiency) | Depends on the FR-13 answer | UNKNOWN | Measure |

---

## C5. Candidate Approaches (to evaluate)

1. **Native microflow build:** microflows call the model service over REST; the domain model stores events; pages show the views. Simplest to reason about; parallelism and animation are the hard parts.
2. **Platform AI features as the engine:** check whether Mendix's own AI and agent features (the Mendix AI assistant, any GenAI connector or agent tooling) could serve as the agent engine, which would change the build from writing orchestration to configuring it. Unverified: what exists, and whether it fits the A3 control rules (code-driven limits, parallel workers, full record).
3. **Hybrid:** Mendix for the application shell, data and pages; a small external service (for example the Part B engine) for orchestration, called over REST. This would test integration rather than pure low-code, and would reduce the comparison's fairness; it is listed for completeness.
4. **Claude builds the Mendix app:** use the documented Concord workflow so that Claude Code builds the app inside Studio Pro, following `Mendix_ClaudeCode.md`. This is a way of executing approach 1 or 2, and is itself a demonstration.

---

## C6. Phase Outline (to be detailed once C4 is researched)

- C-Phase 0: confirm what is installed and licensed; confirm network reach to the model service from where the app will run.
- C-Phase 1: model service connection and a one-call test (equivalent of B Phase 1).
- C-Phase 2: domain model for runs, spans and events.
- C-Phase 3: planner, worker, synthesizer and critic microflows, in a sequential first version.
- C-Phase 4: parallel workers, using the mechanism chosen from C4.
- C-Phase 5: control rules (limits, timeouts, budget, retries).
- C-Phase 6: approval step.
- C-Phase 7: views: flow, timeline, conversation, cost, compare, raw.
- C-Phase 8: animation and replay, or a documented gap.
- C-Phase 9: export and re-open, or a documented gap.
- C-Phase 10: run the A7 acceptance suite and compare with Build 1.

---

## C7. Open Questions

- Is Mendix Studio Pro installed and licensed on this machine? Which version?
- Can a Mendix runtime (local or cloud) reach the corporate model proxy?
- What is the supported way to run several model calls in parallel in the target Mendix version?
- Can a widget embed SVG and script, and is there an existing Marketplace widget that does what the flow view needs?
- Does the platform's own AI tooling provide an agent orchestration engine, and does it satisfy the Part A control rules?
- What is the licensing and deployment cost implication of running this as a demo?

---

## C8. Comparison Criteria Against Build 1

When both builds exist, compare on:

| Criterion | How measured |
|---|---|
| Requirement coverage | Count of FR and NFR that are OK, partial or gap in each build |
| Acceptance results | Same Q1 to Q3 and A7.3 failure scenarios in each build |
| Build effort | Elapsed hours and number of working sessions per phase |
| Run behaviour | Elapsed seconds and tokens for the same questions; parallel efficiency (NFR-08) |
| Visual quality of the flow view and animation | Owner's judgement against SC-5 and SC-8 |
| Maintainability | How an agent prompt or limit is changed, and by whom |
| Deployment and cost | Where it runs, what it needs, what it costs |

The comparison reports measured differences and gaps. It does not declare a winner.

---
---

# PART D: REVISION HISTORY

| Revision | Date | Changes |
|---|---|---|
| 1 | 2026-10-08 | First complete workplan: purpose, architecture, interface, six views, phases 0 to 11, test questions, failure injection, risks |
| 2 | 2026-10-08 | Flow graph changed to hand-drawn SVG with a browser-side animation player; delivery changed to `st.html` instead of the deprecated `components.html`; escaping rule added; animation spike (Phase 9B) added; Phase 0 and 1 status recorded; backend, models and key route recorded |
| 3 | 2026-10-08 | Restructured into one document with internal Parts A (solution-neutral project description with numbered BR, FR, NFR, acceptance), B (Python and Streamlit build, traced to requirement IDs) and C (Mendix skeleton), plus this history. Added audiences (assumed), a worked example, information rules, a traceability table, and success criteria SC-7 and SC-8. No content from revision 2 was dropped; build-specific material moved to Part B |

Backups of earlier revisions: `workplan_A.md` holds revision 1; `workplan_B.md` holds revision 2.
