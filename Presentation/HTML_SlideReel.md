# HTML Slide Reel -- Generation Reference

A self-contained pattern for generating a browser-based slide reel deck from any content document.
No npm, no build step, no dependencies. One `.html` file, opens in any browser.

---

## 1. Human Intake -- Ask These Before Starting

Before generating, confirm the following with the user:

1. **Where is the content document?**
   The source of slide content. This can be:
   - A Python deck builder (`build_deck.py`) -- extract slide titles and content from the slide functions
   - A Markdown workplan -- find the PPTX section or slide outline
   - A plain description from the user -- convert to slide structure yourself

2. **What is the output filename and folder?**
   Suggested convention: `<TopicName>_reel.html` in the same folder as the source content.

3. **What is the presentation title and subtitle?**
   For the cover slide. If not given, derive from the content document.

4. **Any colour scheme preference?**
   Default is Siemens brand (documented below). Confirm if a different palette is needed.

5. **Confirm slide count is reasonable.**
   Ideal range: 10-25 slides. More than 30 becomes hard to navigate in a reel format.

6. **Which slide types are needed?**
   Eight types are available: `cover`, `bullets`, `table`, `query` (code + results), `diagram`
   (boxes-and-arrows flow drawn as inline SVG), `split` (two panels: anatomy or versus), `stats`
   (large figures with their sentences) and `bars` (proportional bar, or value gauges). Use `diagram`
   for processes, flows and architectures; use `split`, `stats` or `bars` to make bullet-heavy slides
   show the shape of their content (comparison, evidence figures, proportions) without cutting text.

---

## 2. Design System -- Siemens Brand Palette

```
--deepblue : #000028   (slide background)
--petrol   : #009999   (table headers, accent lines)
--lpetrol  : #00C1B6   (slide titles, cover title, progress bar)
--orange   : #FF9000   (bullet dots, decorative line on cover)
--blue     : #5AA5FF   (secondary accent)
--white    : #ffffff   (body text)
```

Typography: system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
Monospace (counter): `ui-monospace, SFMono-Regular, Menlo, monospace`

---

## 3. Stage Architecture

The deck uses a **fixed 1600x900px canvas** scaled to fit any screen via CSS `transform: scale()`.
This gives pixel-perfect layout at any resolution without media queries.

```
body (overflow: hidden, background: #000)
  #stage (position: absolute, 1600x900px, scaled via JS)
    .slide x N  (position: absolute, inset: 0, opacity transitions)
  #bar          (fixed, top progress bar)
  #counter      (fixed, top-right "N / total")
  #prev #next   (fixed, arrow buttons)
  #dots         (fixed, bottom dot indicators)
```

Key CSS rule:
```css
#stage {
  position: absolute; top: 50%; left: 50%;
  width: 1600px; height: 900px;
  transform-origin: center center;
}
```

Scale function in JS:
```js
function scaleStage() {
  var sx = window.innerWidth / 1600;
  var sy = window.innerHeight / 900;
  var s = Math.min(sx, sy);
  stage.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
}
window.addEventListener('resize', scaleStage);
scaleStage();
```

---

## 4. Slide Types

Eight slide types are supported. Choose based on content structure.

### 4a. Cover Slide (`type: 'cover'`)

Used for slide 1 only. Centred layout, large title, decorative line.

Required fields:
- `tag` -- small label at top (e.g. `"BFSI | Tax Enforcement | Thailand"`)
- `title` -- large title text (use `\n` for line break)
- `subtitle` -- medium subtitle line
- `sub2` -- smaller tagline (e.g. product names)

### 4b. Bullet List Slide (`type: 'bullets'`)

Used for most content slides. Title + 4-8 bullet points.

Required fields:
- `title` -- slide heading
- `items` -- array of strings (bullet points, keep each under ~120 chars)

### 4c. Table Slide (`type: 'table'`)

Used when content is comparative or has clear columns.

Required fields:
- `title` -- slide heading
- `headers` -- array of column header strings
- `rows` -- 2D array of cell strings

Keep tables to 3-4 columns and 4-6 rows for readability at 1600x900.

### 4d. Results-page Slide (`type: 'query'`)

Used to show a SPARQL (or any code) query alongside its results, with a plain-language explanation above.
Ideal for technical demos to mixed audiences.

Layout:
- TOP ~38%: slide title + `explanation` paragraph, full width, white text
- BOTTOM ~62%: two side-by-side panels
  - LEFT (~48%): labelled "SPARQL" in petrol, query code in monospace on dark background
  - RIGHT (~48%): labelled "Live Results" in petrol, mini results table (headers + rows)

Required fields:
- `title` -- slide heading
- `explanation` -- plain-language paragraph for non-technical audience
- `sparql` -- the SPARQL query text (raw string, newlines preserved via `white-space: pre`)
- `resultHeaders` -- array of column header strings for the results table
- `resultRows` -- 2D array of result cell strings

CSS classes used: `.query-body`, `.query-explanation`, `.query-panels`, `.query-panel`,
`.query-panel-label`, `.query-code`, `.query-result-wrap`, `.query-result-table`

Optional fields (need the panel-label add-on in Section 7b):
- `codeLabel` -- replaces the left panel label "SPARQL" (e.g. `'Python - simplified from lab04_agent_loop.py'`)
- `resultLabel` -- replaces the right panel label "Live Results" (e.g. `'Real output - 2026-11-18'`)

Use these when the code is not SPARQL. Labels are set with `textContent`, never as markup.

### 4e. Diagram Slide (`type: 'diagram'`)

A boxes-and-arrows flow diagram, drawn as inline SVG from data. Use it for processes, flows,
loops and architectures (e.g. agent loops, workflow patterns, request/response cycles).

Layout:
- TOP: slide title, then a one- or two-sentence `caption` in plain language
- BELOW: an SVG drawing area, 600px high, full slide width

Coordinate system: the SVG uses `viewBox="0 0 1400 600"` (scaled to fit, aspect preserved).
All x/y values are in that space; (0,0) is top-left. Node x/y is the box CENTRE.

Required fields:
- `title` -- slide heading
- `caption` -- plain-language explanation shown above the diagram
- `nodes` -- array of boxes:
  - `id` -- unique string, referenced by edges
  - `label` -- box text; use `\n` for line breaks
  - `x`, `y` -- centre of the box
  - `w`, `h` -- optional width/height (defaults 220 x 84)
  - `kind` -- optional style: `'accent'` (orange), `'gate'` (blue), `'ghost'` (dashed outline); omit for the default petrol box

Optional fields:
- `edges` -- array of arrows:
  - `from`, `to` -- node ids (an edge whose ids do not exist is silently skipped)
  - `label` -- optional text on the arrow
  - `curve` -- optional bend in px (positive or negative; 0 or absent = straight line). Use opposite
    curves for a pair of arrows going both ways, or a large curve for a loop-back
  - `dashed` -- optional `true` for a dashed arrow (e.g. feedback or "next call")
  - `dx`, `dy` -- optional nudge of the edge label position
- `labels` -- array of free text notes: `x`, `y`, `text` (`\n` allowed), optional `cls`
  (`'diagram-note'` default, or `'diagram-section'` for an upper-case section heading) and optional
  `anchor` (`'middle'` default, `'start'`, `'end'`)

Text safety: all diagram text (node labels, edge labels, notes) is set with `textContent` /
SVG `tspan` elements, never `innerHTML`, so no markup can be injected. Title and caption go
through the engine's `esc()` function.

CSS classes used: `.diagram-caption`, `.diagram-wrap`, `.diagram-svg`, `.diagram-node`
(`.accent`, `.gate`, `.ghost`), `.diagram-edge` (`.dashed`), `.diagram-arrowhead`,
`.diagram-edge-label`, `.diagram-note`, `.diagram-section`

Requires the CSS add-on (Section 6b) and the JS add-on (Section 7b).

### 4f. Split Slide (`type: 'split'`)

Two titled panels side by side, joined by a connector, with an optional lead sentence above and an
optional full-width "shared" band below. Two connector modes:
- `connector: 'arrow'` (default): an orange arrow with an optional label -- use for an anatomy
  (input on the left, output on the right, e.g. request -> response).
- `connector: 'divider'`: a vertical line with a centred label such as `'vs'` -- use for a head-to-head
  comparison (e.g. workflow vs agent), with what both sides share in the band.

Fields:
- `title` -- slide heading (required)
- `lead` -- optional sentence shown full width above the panels
- `left`, `right` -- required objects: `{ title, tag (optional short italic line), items: [strings] }`
  The left panel is outlined in petrol, the right panel in orange.
- `connector` -- `'arrow'` or `'divider'`; `connectorLabel` -- optional short label
- `shared` -- optional `{ title, items: [strings] }` band under the panels (blue rule)

Budget: about 5-7 items in total at 20px. All text is set with `textContent` (never `innerHTML`).

CSS classes used: `.x-lead`, `.x-list`, `.split-row`, `.split-panel` (`.left`, `.right`),
`.split-panel-title`, `.split-tag`, `.split-connector` (`.arrow`, `.divider`), `.split-vline`,
`.split-connector-label`, `.split-shared`, `.split-shared-title`

### 4g. Stats Slide (`type: 'stats'`)

A row of tiles, each with one large orange figure above the original sentence it comes from, then an
optional "change of view" pair (before -> after) and an optional highlighted footer line. Use for
evidence slides whose bullets each carry a key number. Keep it to one or two slides per deck so the
large figures stay special.

Fields:
- `title` -- slide heading (required)
- `tiles` -- required array of `{ figure, text, span (optional, default 1) }`. `figure` must be a
  number that already appears in `text`; `span: 2` gives a long figure (e.g. a range) a double-width
  tile. Columns = sum of spans; 4-5 columns fit at 1600 px.
- `pair` -- optional `{ title, before: { when, text }, after: { when, text } }`, drawn with an arrow
- `footer` -- optional single sentence in a tinted band

CSS classes used: `.stats-grid`, `.stat-tile`, `.stat-figure`, `.stat-text`, `.stats-pair`,
`.stats-pair-title`, `.stats-pair-side` (`.after`), `.stats-pair-when`, `.stats-pair-text`,
`.stats-pair-arrow`, `.stats-footer`

### 4h. Bars Slide (`type: 'bars'`)

Two modes, both for quantities that are parts of a whole or percentages:
- Default mode: one proportional horizontal bar split into segments (petrol, blue, orange in order),
  with a column of detail under each segment whose width matches the segment. Optional header line
  above, optional note under the bar, optional footer list.
- `mode: 'gauges'`: value gauges (label, large value, filled track, caption) in a left column beside a
  compact list on the right. Use to contrast two or three rates (e.g. pass@k vs pass^k).

Fields (default mode):
- `title` (required), `head` (optional sentence)
- `segments` -- required array of `{ label, value, display (optional, e.g. 'about 44%'), text }`.
  `value` sets the proportional width (values need not sum to 100); up to 3 segments use the palette.
- `barNote` -- optional small note under the bar (e.g. how totals were derived)
- `footer` -- optional array of strings

Fields (`mode: 'gauges'`):
- `title` (required), `head` (optional)
- `gauges` -- array of `{ label, value (0-100, fill width), display (optional), caption, low (true = orange) }`
- `gaugeNote` -- optional small note under the gauges
- `items` -- array of strings shown as the list on the right

CSS classes used: `.bars-head`, `.bars-track`, `.bars-seg` (`.c0`-`.c2`), `.bars-note`, `.bars-cols`,
`.bars-col`, `.bars-col-title` (`.c0`-`.c2`), `.bars-col-text`, `.bars-foot`, `.gauges-row`, `.gauges`,
`.gauge` (`.low`), `.gauge-top`, `.gauge-label`, `.gauge-value`, `.gauge-track`, `.gauge-fill`,
`.gauge-caption`, `.gauge-note`, `.gauges-list`

Types 4f-4h require the CSS add-on (Section 6c) and the JS add-on (Section 7c). The JS add-on uses
`svgEl()` from the diagram helpers (Section 7b, Piece 1), so paste that piece too.

---

## 5. SLIDES Data Array Format

All slide content lives in a `SLIDES` array of objects. This is the only section that changes per deck.

```js
const SLIDES = [
  {
    type: 'cover',
    tag: 'TOPIC | REGION | PRODUCT',
    title: 'Main Title\nSecond Line',
    subtitle: 'Descriptive subtitle',
    sub2: 'Product A  |  Product B  |  Product C'
  },
  {
    type: 'bullets',
    title: 'Slide Title Here',
    items: [
      "First bullet point",
      "Second bullet point",
      "Third bullet point"
    ]
  },
  {
    type: 'table',
    title: 'Comparative Slide Title',
    headers: ['Column 1', 'Column 2', 'Column 3'],
    rows: [
      ['Row 1 A', 'Row 1 B', 'Row 1 C'],
      ['Row 2 A', 'Row 2 B', 'Row 2 C']
    ]
  },
  {
    type: 'query',
    title: 'Query Slide Title',
    explanation: 'Plain-language explanation for a non-technical audience. Describe what the query finds and why it matters for fraud detection.',
    sparql: 'PREFIX ex: <http://example.com/>\nSELECT ?entity ?value\nWHERE {\n  ?entity ex:hasFlag true ;\n          ex:value ?value .\n}\nLIMIT 10',
    resultHeaders: ['Entity', 'Value'],
    resultRows: [
      ['entity:001', '450000'],
      ['entity:002', '380000']
    ]
  },
  {
    type: 'diagram',
    title: 'Tools: the model asks, your code acts',
    caption: "Tool use is a contract. The model emits a structured request, your code runs the operation, and the result flows back. 'The model never runs anything on its own.' (Anthropic docs)",
    nodes: [
      { id: 'model', label: 'Model', x: 230, y: 320, w: 220, kind: 'accent' },
      { id: 'prog', label: 'Your program', x: 700, y: 320, w: 260 },
      { id: 'tool', label: 'Tool function\n(your code)', x: 1170, y: 320, w: 260 }
    ],
    edges: [
      { from: 'prog', to: 'model', label: '1. message + tool schemas', curve: 90 },
      { from: 'model', to: 'prog', label: '2. tool_use request', curve: 90, dy: 40 },
      { from: 'prog', to: 'tool', label: '3. run it', curve: 90, dy: 40 },
      { from: 'tool', to: 'prog', label: '4. output', curve: 90 },
      { from: 'prog', to: 'model', label: '5. tool_result (next call)', curve: 230, dashed: true }
    ],
    labels: [
      { x: 700, y: 540, text: 'The model only ever sees the schema and the result - never your Python code (Anthropic docs).', cls: 'diagram-note' }
    ]
  },
  {
    type: 'split',
    title: 'Agent or workflow? The definitions that matter',
    left: { title: 'Workflow', tag: 'your code decides the path',
            items: ["Workflow: 'LLMs and tools are orchestrated through predefined code paths' (Anthropic 2024)."] },
    connector: 'divider',
    connectorLabel: 'vs',
    right: { title: 'Agent', tag: 'the model directs its own process',
             items: ["Agent: LLMs 'dynamically direct their own processes and tool usage' (Anthropic 2024)."] },
    shared: { title: 'Where both views agree',
              items: ["Shared building block: the augmented LLM - a model plus retrieval, tools and memory (Anthropic 2024)."] }
  },
  {
    type: 'stats',
    title: 'When multi-agent helps - and when it hurts',
    tiles: [
      { figure: '90.2%', text: "Anthropic's research system beat single-agent Opus by 90.2% on its internal eval, at about 15x chat tokens (Anthropic 2025)." },
      { figure: '+80.8% / -70.0%', span: 2, text: "Across 260 configurations, multi-agent ranged from +80.8% to -70.0% versus one agent (Kim et al. 2025)." }
    ],
    pair: {
      title: 'Cognition changed its view',
      before: { when: '2025', text: "Cognition 2025: 'Don't build multi-agents' - share full context; actions carry implicit decisions." },
      after: { when: '2026', text: "Cognition 2026: it works when 'writes stay single-threaded' and extra agents add intelligence, not actions." }
    },
    footer: "Good fit: parallel, separable, high-value work. Poor fit: tightly coupled work, such as most coding (Anthropic 2025)."
  },
  {
    type: 'bars',
    title: 'How multi-agent systems fail: the MAST study',
    head: "1,642 annotated traces from 7 multi-agent frameworks; 14 failure modes in 3 groups (Cemri et al. 2025).",
    segments: [
      { label: 'System design', value: 44, display: 'about 44%', text: "System design, about 44% (derived): ..." },
      { label: 'Inter-agent misalignment', value: 32, display: 'about 32%', text: "Inter-agent misalignment, about 32% (derived): ..." },
      { label: 'Task verification', value: 23.5, display: 'about 23.5%', text: "Task verification, about 23.5% (derived): ..." }
    ],
    barNote: 'Share of observed failures by group. Group totals are derived by summing the published per-mode figures.',
    footer: ["Lesson: design termination and verification in from the start - do not bolt them on later."]
  },
  {
    type: 'bars',
    mode: 'gauges',
    title: 'Evaluation: measure outcomes, not impressions',
    gauges: [
      { label: 'pass@3', value: 98, display: '98%', caption: 'at least one of 3 trials succeeds' },
      { label: 'pass^3', value: 42, display: '42%', caption: 'all 3 trials succeed', low: true }
    ],
    gaugeNote: 'Same agent, 75% success per trial, k = 3. Values rounded (arithmetic).',
    items: ["pass@k: at least one of k trials succeeds. pass^k: all k succeed - the reliability number (Anthropic evals; tau-bench)."]
  }
];
```

---

## 6. Full CSS Block (paste verbatim, do not modify)

```css
:root {
  --deepblue: #000028;
  --petrol: #009999;
  --lpetrol: #00C1B6;
  --orange: #FF9000;
  --blue: #5AA5FF;
  --white: #ffffff;
  --dur: 320ms;
  --ease: cubic-bezier(.2,.7,.3,1);
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  height: 100%; overflow: hidden;
  background: #000;
  font-family: var(--font);
  color: var(--white);
  -webkit-font-smoothing: antialiased;
}

#stage {
  position: absolute; top: 50%; left: 50%;
  width: 1600px; height: 900px;
  transform-origin: center center;
}

.slide {
  position: absolute; inset: 0;
  opacity: 0; pointer-events: none;
  padding: 64px 96px 56px;
  background: var(--deepblue);
  transition: opacity var(--dur) var(--ease), transform var(--dur) var(--ease);
  transform: translateY(22px);
  overflow: hidden;
}
.slide.active  { opacity: 1; pointer-events: auto; transform: translateY(0); }
.slide.out     { opacity: 0; transform: translateY(-22px); }

.slide::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, var(--petrol), var(--lpetrol));
}

.slide.cover {
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  text-align: center; padding: 70px 130px;
}
.cover-tag {
  font-size: 14px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--petrol); margin-bottom: 28px; font-weight: 600;
}
.cover-title {
  font-size: 66px; font-weight: 700; line-height: 1.12;
  color: var(--lpetrol); margin-bottom: 8px;
}
.cover-line {
  width: 72px; height: 3px; background: var(--orange); margin: 26px auto;
}
.cover-subtitle {
  font-size: 28px; color: rgba(255,255,255,0.88);
  margin-bottom: 14px; font-weight: 400;
}
.cover-tags {
  font-size: 18px; color: var(--petrol); font-weight: 500; letter-spacing: 0.04em;
}

.slide-title {
  font-size: 30px; font-weight: 700; color: var(--lpetrol);
  margin-bottom: 26px; line-height: 1.25;
  padding-bottom: 14px; border-bottom: 2px solid rgba(0,153,153,0.55);
}

.bullet-list { list-style: none; padding: 0; margin: 0; }
.bullet-list li {
  font-size: 20px; line-height: 1.48;
  color: rgba(255,255,255,0.90);
  margin-bottom: 14px; padding-left: 26px; position: relative;
}
.bullet-list li::before {
  content: ""; position: absolute; left: 0; top: 11px;
  width: 9px; height: 9px; background: var(--orange); border-radius: 50%;
}

.reel-table { width: 100%; border-collapse: collapse; }
.reel-table th {
  background: var(--petrol); color: var(--white);
  padding: 13px 16px; text-align: left;
  font-weight: 600; font-size: 19px;
}
.reel-table td {
  padding: 11px 16px; color: rgba(255,255,255,0.88);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  vertical-align: top; line-height: 1.42; font-size: 18px;
}
.reel-table tr:nth-child(even) td { background: rgba(255,255,255,0.04); }
.reel-table tr:hover td { background: rgba(0,153,153,0.14); transition: background .15s; }
.reel-table td:first-child { color: var(--lpetrol); font-weight: 600; white-space: nowrap; }

/* ---- Query slides (type: 'query') ---- */
.query-body {
  display: flex; flex-direction: column;
  height: calc(100% - 64px);
}
.query-explanation {
  font-size: 19px; line-height: 1.55;
  color: rgba(255,255,255,0.88);
  margin-bottom: 18px;
  flex: 0 0 auto;
}
.query-panels {
  display: flex; gap: 18px;
  flex: 1 1 0; min-height: 0;
}
.query-panel {
  flex: 1 1 0; min-width: 0;
  display: flex; flex-direction: column;
}
.query-panel-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--petrol); margin-bottom: 6px;
}
.query-code {
  flex: 1 1 0; overflow-y: auto;
  background: #001428; border-radius: 6px;
  padding: 12px 14px;
  font-family: var(--mono); font-size: 17px; line-height: 1.55;
  color: rgba(255,255,255,0.85);
  white-space: pre; border: 1px solid rgba(0,153,153,0.22);
}
.query-result-wrap {
  flex: 1 1 0; overflow-y: auto;
  background: rgba(0,0,40,0.55); border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.08);
}
.query-result-table { width: 100%; border-collapse: collapse; font-size: 17px; }
.query-result-table th {
  background: rgba(0,153,153,0.40); color: var(--white);
  padding: 5px 8px; text-align: left; font-weight: 600; white-space: nowrap;
}
.query-result-table td {
  padding: 4px 8px; color: rgba(255,255,255,0.85);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  vertical-align: top; line-height: 1.40;
}
.query-result-table tr:nth-child(even) td { background: rgba(255,255,255,0.04); }

#bar {
  position: fixed; top: 0; left: 0; height: 3px;
  background: var(--lpetrol); width: 0%;
  transition: width .4s var(--ease); z-index: 100;
}
#counter {
  position: fixed; top: 13px; right: 18px; z-index: 100;
  font-size: 12px; font-family: var(--mono);
  color: rgba(255,255,255,0.30); letter-spacing: 0.06em;
}
#dots {
  position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 4px; z-index: 100;
}
.dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255,255,255,0.18); cursor: pointer;
  transition: background .2s, transform .2s;
}
.dot.on { background: var(--lpetrol); transform: scale(1.6); }

.arr {
  position: fixed; top: 50%; transform: translateY(-50%);
  background: rgba(0,0,30,0.75); border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.45); font-size: 22px;
  width: 44px; height: 44px; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  z-index: 100; backdrop-filter: blur(6px);
  transition: background .2s, color .2s;
}
.arr:hover { background: rgba(0,153,153,0.30); color: var(--white); }
#prev { left: 14px; }
#next { right: 14px; }
```

### 6b. Diagram CSS add-on (only if the deck uses `diagram` slides)

Paste verbatim at the END of the `<style>` block, after the Section 6 CSS. Do not modify the Section 6 block itself.

```css
/* ==== ADDED LAYOUT TYPE: Diagram slides (type: 'diagram') - begin ==== */
.diagram-caption {
  font-size: 20px; line-height: 1.5;
  color: rgba(255,255,255,0.88);
  margin-bottom: 12px;
}
.diagram-wrap { width: 100%; height: 600px; }
.diagram-svg { width: 100%; height: 100%; display: block; }
.diagram-node rect { fill: rgba(0,153,153,0.22); stroke: var(--petrol); stroke-width: 2.5; }
.diagram-node text { fill: var(--white); font-family: var(--font); font-size: 22px; font-weight: 600; }
.diagram-node.accent rect { fill: rgba(255,144,0,0.16); stroke: var(--orange); }
.diagram-node.gate rect { fill: rgba(90,165,255,0.16); stroke: var(--blue); }
.diagram-node.ghost rect { fill: none; stroke-dasharray: 8 6; }
.diagram-edge { fill: none; stroke: var(--orange); stroke-width: 3; }
.diagram-edge.dashed { stroke-dasharray: 10 8; }
.diagram-arrowhead { fill: var(--orange); }
.diagram-edge-label {
  fill: var(--lpetrol); font-family: var(--font); font-size: 19px; font-weight: 600;
  paint-order: stroke; stroke: var(--deepblue); stroke-width: 6px; stroke-linejoin: round;
}
.diagram-note { fill: rgba(255,255,255,0.78); font-family: var(--font); font-size: 18px; }
.diagram-section { fill: var(--lpetrol); font-family: var(--font); font-size: 18px; font-weight: 700; letter-spacing: 0.08em; }
/* ==== ADDED LAYOUT TYPE: Diagram slides - end ==== */
```

### 6c. Split / stats / bars CSS add-on (only if the deck uses `split`, `stats` or `bars` slides)

Paste verbatim at the END of the `<style>` block, after the Section 6 CSS (and after 6b if present).

```css
/* ==== ADDED LAYOUT TYPES: split / stats / bars slides - begin ==== */
.x-lead {
  font-size: 22px; line-height: 1.45; color: rgba(255,255,255,0.92);
  margin-bottom: 22px; max-width: 1300px;
}
.x-list { list-style: none; padding: 0; margin: 0; }
.x-list li {
  font-size: 20px; line-height: 1.45; color: rgba(255,255,255,0.90);
  padding-left: 20px; position: relative; margin-bottom: 12px;
}
.x-list li::before {
  content: ""; position: absolute; left: 0; top: 7px;
  width: 6px; height: 16px; border-radius: 2px; background: var(--petrol);
}

/* split: two panels joined by an arrow (anatomy) or a divider (versus) */
.split-row { display: flex; align-items: stretch; }
.split-panel {
  flex: 1 1 0; min-width: 0; padding: 22px 26px 10px;
  border: 2px solid rgba(0,153,153,0.70); border-radius: 10px;
  background: rgba(0,153,153,0.08);
}
.split-panel.right { border-color: rgba(255,144,0,0.75); background: rgba(255,144,0,0.06); }
.split-panel-title { font-size: 26px; font-weight: 700; color: var(--lpetrol); margin-bottom: 4px; }
.split-panel.right .split-panel-title { color: var(--orange); }
.split-tag { font-size: 18px; font-style: italic; color: rgba(255,255,255,0.65); margin-bottom: 16px; }
.split-panel.right .x-list li::before { background: var(--orange); }
.split-connector {
  flex: 0 0 130px; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.split-connector svg { width: 110px; height: 40px; display: block; }
.split-connector-label { font-size: 18px; font-weight: 600; color: var(--lpetrol); margin-bottom: 8px; text-align: center; }
.split-connector.divider .split-vline { width: 2px; flex: 1 1 auto; background: rgba(255,255,255,0.25); }
.split-connector.divider .split-connector-label { font-size: 24px; color: var(--white); margin: 12px 0; }
.split-shared {
  display: flex; gap: 28px; align-items: flex-start;
  margin-top: 24px; padding-top: 16px; border-top: 2px solid rgba(90,165,255,0.60);
}
.split-shared-title { flex: 0 0 230px; font-size: 21px; font-weight: 700; color: var(--blue); line-height: 1.4; }
.split-shared .x-list { flex: 1 1 0; }
.split-shared .x-list li::before { background: var(--blue); }

/* stats: large figures, each with its original sentence */
.stats-grid {
  display: grid; gap: 0;
  border-top: 1px solid rgba(255,255,255,0.18); border-bottom: 1px solid rgba(255,255,255,0.18);
}
.stat-tile { padding: 18px 22px 20px; border-left: 1px solid rgba(255,255,255,0.18); min-width: 0; }
.stat-tile:first-child { border-left: none; padding-left: 0; }
.stat-figure {
  font-size: 54px; font-weight: 800; line-height: 1.05; letter-spacing: -0.02em;
  color: var(--orange); margin-bottom: 10px; white-space: nowrap;
}
.stat-text { font-size: 20px; line-height: 1.42; color: rgba(255,255,255,0.88); }
.stats-pair { display: flex; align-items: stretch; margin-top: 26px; }
.stats-pair-title { flex: 0 0 210px; font-size: 22px; font-weight: 700; color: var(--lpetrol); line-height: 1.3; padding-top: 4px; }
.stats-pair-side { flex: 1 1 0; min-width: 0; padding: 0 22px; border-left: 3px solid var(--petrol); }
.stats-pair-side.after { border-left-color: var(--orange); }
.stats-pair-when { font-size: 30px; font-weight: 800; color: var(--white); margin-bottom: 4px; }
.stats-pair-text { font-size: 20px; line-height: 1.42; color: rgba(255,255,255,0.88); }
.stats-pair-arrow { flex: 0 0 64px; display: flex; align-items: center; justify-content: center; }
.stats-pair-arrow svg { width: 56px; height: 30px; display: block; }
.stats-footer {
  margin-top: 26px; padding: 14px 20px; border-radius: 8px;
  font-size: 21px; line-height: 1.45; color: var(--white); background: rgba(0,193,182,0.12);
}

/* bars: one proportional bar with a column of detail under each segment */
.bars-head { font-size: 21px; line-height: 1.45; color: rgba(255,255,255,0.90); margin-bottom: 20px; }
.bars-track { display: flex; height: 64px; border-radius: 8px; overflow: hidden; }
.bars-seg {
  flex-basis: 0; min-width: 0; display: flex; align-items: center; padding: 0 16px;
  font-size: 22px; font-weight: 700; color: var(--deepblue); white-space: nowrap; overflow: hidden;
}
.bars-seg.c0 { background: var(--lpetrol); }
.bars-seg.c1 { background: var(--blue); }
.bars-seg.c2 { background: var(--orange); }
.bars-note { font-size: 18px; color: rgba(255,255,255,0.62); margin-top: 8px; }
.bars-cols { display: flex; }
.bars-col { flex-basis: 0; min-width: 0; padding: 14px 20px 0 0; }
.bars-col-title { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.bars-col-title.c0 { color: var(--lpetrol); }
.bars-col-title.c1 { color: var(--blue); }
.bars-col-title.c2 { color: var(--orange); }
.bars-col-text { font-size: 20px; line-height: 1.42; color: rgba(255,255,255,0.88); }
.bars-foot { margin-top: 26px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.18); }

/* bars, mode 'gauges': value gauges beside a compact list */
.gauges-row { display: flex; gap: 48px; align-items: flex-start; }
.gauges { flex: 0 0 470px; }
.gauge { margin-bottom: 30px; }
.gauge-top { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px; }
.gauge-label { font-size: 30px; font-weight: 700; color: var(--white); }
.gauge-value { font-size: 58px; font-weight: 800; line-height: 1; color: var(--lpetrol); }
.gauge.low .gauge-value { color: var(--orange); }
.gauge-track { height: 22px; border-radius: 11px; overflow: hidden; background: rgba(255,255,255,0.10); }
.gauge-fill { height: 100%; background: var(--lpetrol); }
.gauge.low .gauge-fill { background: var(--orange); }
.gauge-caption { font-size: 20px; color: rgba(255,255,255,0.78); margin-top: 8px; }
.gauge-note { font-size: 18px; line-height: 1.4; color: rgba(255,255,255,0.62); }
.gauges-list { flex: 1 1 0; min-width: 0; }
/* ==== ADDED LAYOUT TYPES: split / stats / bars slides - end ==== */
```

---

## 7. Full JS Engine Block (paste verbatim, do not modify)

Paste this after the closing `</style>` tag, before `</head>`, or just before `</body>`.
The `SLIDES` array goes at the top of this block.

```js
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function buildSlide(data) {
  var div = document.createElement('div');
  div.className = 'slide' + (data.type === 'cover' ? ' cover' : '');

  if (data.type === 'cover') {
    div.innerHTML =
      '<div class="cover-tag">' + esc(data.tag) + '</div>' +
      '<div class="cover-title">' + esc(data.title).replace('\n', '<br>') + '</div>' +
      '<div class="cover-line"></div>' +
      '<div class="cover-subtitle">' + esc(data.subtitle) + '</div>' +
      '<div class="cover-tags">' + esc(data.sub2) + '</div>';

  } else if (data.type === 'bullets') {
    var lis = data.items.map(function(i) { return '<li>' + esc(i) + '</li>'; }).join('');
    div.innerHTML =
      '<div class="slide-title">' + esc(data.title) + '</div>' +
      '<ul class="bullet-list">' + lis + '</ul>';

  } else if (data.type === 'table') {
    var ths = data.headers.map(function(h) { return '<th>' + esc(h) + '</th>'; }).join('');
    var trs = data.rows.map(function(row) {
      return '<tr>' + row.map(function(c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>';
    }).join('');
    div.innerHTML =
      '<div class="slide-title">' + esc(data.title) + '</div>' +
      '<table class="reel-table"><thead><tr>' + ths + '</tr></thead>' +
      '<tbody>' + trs + '</tbody></table>';

  } else if (data.type === 'query') {
    var rths = data.resultHeaders.map(function(h) { return '<th>' + esc(h) + '</th>'; }).join('');
    var rtrs = data.resultRows.map(function(row) {
      return '<tr>' + row.map(function(c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>';
    }).join('');
    div.innerHTML =
      '<div class="slide-title">' + esc(data.title) + '</div>' +
      '<div class="query-body">' +
        '<div class="query-explanation">' + esc(data.explanation) + '</div>' +
        '<div class="query-panels">' +
          '<div class="query-panel">' +
            '<div class="query-panel-label">SPARQL</div>' +
            '<div class="query-code">' + esc(data.sparql) + '</div>' +
          '</div>' +
          '<div class="query-panel">' +
            '<div class="query-panel-label">Live Results</div>' +
            '<div class="query-result-wrap">' +
              '<table class="query-result-table">' +
                '<thead><tr>' + rths + '</tr></thead>' +
                '<tbody>' + rtrs + '</tbody>' +
              '</table>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }
  return div;
}

var stage = document.getElementById('stage');
var slideEls = SLIDES.map(function(s) {
  var el = buildSlide(s);
  stage.appendChild(el);
  return el;
});

var dotsEl = document.getElementById('dots');
SLIDES.forEach(function(_, i) {
  var d = document.createElement('div');
  d.className = 'dot';
  d.addEventListener('click', function() { goTo(i); });
  dotsEl.appendChild(d);
});
var dotEls = dotsEl.querySelectorAll('.dot');

var current = 0;
var animating = false;

function goTo(n) {
  if (n === current || animating) return;
  animating = true;
  var prev = slideEls[current];
  var next = slideEls[n];
  prev.classList.add('out');
  prev.classList.remove('active');
  setTimeout(function() { prev.classList.remove('out'); }, 360);
  next.classList.add('active');
  current = n;
  updateChrome();
  setTimeout(function() { animating = false; }, 360);
}

function updateChrome() {
  var pct = ((current + 1) / SLIDES.length) * 100;
  document.getElementById('bar').style.width = pct + '%';
  document.getElementById('counter').textContent = (current + 1) + ' / ' + SLIDES.length;
  dotEls.forEach(function(d, i) { d.classList.toggle('on', i === current); });
}

function scaleStage() {
  var sx = window.innerWidth / 1600;
  var sy = window.innerHeight / 900;
  var s = Math.min(sx, sy);
  stage.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
}

slideEls[0].classList.add('active');
updateChrome();
scaleStage();
window.addEventListener('resize', scaleStage);

document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
    if (current < SLIDES.length - 1) goTo(current + 1);
    e.preventDefault();
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    if (current > 0) goTo(current - 1);
    e.preventDefault();
  }
});

document.getElementById('next').addEventListener('click', function() {
  if (current < SLIDES.length - 1) goTo(current + 1);
});
document.getElementById('prev').addEventListener('click', function() {
  if (current > 0) goTo(current - 1);
});
```

### 7b. JS add-ons (only if the deck uses `diagram` slides or query panel labels)

The Section 7 engine stays verbatim except for one inserted branch. Three pieces, each delimited by `ADDED` comments:

**Piece 1 -- diagram renderer helpers.** Paste right after the `SLIDES` array, before `function esc(s)`:

```js
/* ==== ADDED LAYOUT TYPE: Diagram renderer helpers - begin ==== */
/* Builds an inline SVG from static SLIDES data only. All text is set with
   textContent (never innerHTML), so no markup can be injected. */
var SVGNS = 'http://www.w3.org/2000/svg';
var diagramCount = 0;

function svgEl(tag, attrs) {
  var el = document.createElementNS(SVGNS, tag);
  for (var k in attrs) {
    if (Object.prototype.hasOwnProperty.call(attrs, k)) el.setAttribute(k, attrs[k]);
  }
  return el;
}

function boxEdgePoint(n, tx, ty) {
  var dx = tx - n.x, dy = ty - n.y;
  if (dx === 0 && dy === 0) return { x: n.x, y: n.y };
  var hw = n.w / 2, hh = n.h / 2;
  var tX = dx !== 0 ? hw / Math.abs(dx) : Infinity;
  var tY = dy !== 0 ? hh / Math.abs(dy) : Infinity;
  var t = Math.min(tX, tY);
  return { x: n.x + dx * t, y: n.y + dy * t };
}

function svgMultiline(textEl, x, y, text, lineHeight) {
  var lines = String(text).split('\n');
  textEl.setAttribute('x', x);
  textEl.setAttribute('y', y - (lines.length - 1) * lineHeight / 2);
  lines.forEach(function(line, i) {
    var ts = svgEl('tspan', { x: x, dy: i === 0 ? 0 : lineHeight });
    ts.textContent = line;
    textEl.appendChild(ts);
  });
}

function buildDiagram(data) {
  diagramCount += 1;
  var markerId = 'arrowhead-' + diagramCount;
  var wrap = document.createElement('div');
  wrap.className = 'diagram-wrap';
  var svg = svgEl('svg', { viewBox: '0 0 1400 600', 'class': 'diagram-svg', preserveAspectRatio: 'xMidYMid meet' });
  var defs = svgEl('defs', {});
  var marker = svgEl('marker', { id: markerId, viewBox: '0 0 10 10', refX: '9', refY: '5',
                                 markerWidth: '7', markerHeight: '7', orient: 'auto' });
  marker.appendChild(svgEl('path', { d: 'M 0 0 L 10 5 L 0 10 z', 'class': 'diagram-arrowhead' }));
  defs.appendChild(marker);
  svg.appendChild(defs);

  var byId = {};
  data.nodes.forEach(function(n) {
    byId[n.id] = { x: n.x, y: n.y, w: n.w || 220, h: n.h || 84 };
  });

  var edgeLayer = svgEl('g', {});
  var nodeLayer = svgEl('g', {});
  var labelLayer = svgEl('g', {});

  (data.edges || []).forEach(function(e) {
    var a = byId[e.from], b = byId[e.to];
    if (!a || !b) return;
    var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    var c = e.curve || 0, cx = mx, cy = my;
    if (c) {
      var ddx = b.x - a.x, ddy = b.y - a.y;
      var len = Math.sqrt(ddx * ddx + ddy * ddy) || 1;
      cx = mx - ddy / len * c;
      cy = my + ddx / len * c;
    }
    var p1 = boxEdgePoint(a, c ? cx : b.x, c ? cy : b.y);
    var p2 = boxEdgePoint(b, c ? cx : a.x, c ? cy : a.y);
    var d = c
      ? 'M ' + p1.x + ' ' + p1.y + ' Q ' + cx + ' ' + cy + ' ' + p2.x + ' ' + p2.y
      : 'M ' + p1.x + ' ' + p1.y + ' L ' + p2.x + ' ' + p2.y;
    edgeLayer.appendChild(svgEl('path', {
      d: d,
      'class': 'diagram-edge' + (e.dashed ? ' dashed' : ''),
      'marker-end': 'url(#' + markerId + ')'
    }));
    if (e.label) {
      var lx = c ? (0.25 * p1.x + 0.5 * cx + 0.25 * p2.x) : (p1.x + p2.x) / 2;
      var ly = c ? (0.25 * p1.y + 0.5 * cy + 0.25 * p2.y) : (p1.y + p2.y) / 2;
      var t = svgEl('text', { x: lx + (e.dx || 0), y: ly + (e.dy || 0) - 10,
                              'class': 'diagram-edge-label', 'text-anchor': 'middle' });
      t.textContent = e.label;
      labelLayer.appendChild(t);
    }
  });

  data.nodes.forEach(function(n) {
    var m = byId[n.id];
    var g = svgEl('g', { 'class': 'diagram-node' + (n.kind ? ' ' + n.kind : '') });
    g.appendChild(svgEl('rect', { x: m.x - m.w / 2, y: m.y - m.h / 2, width: m.w, height: m.h, rx: 10, ry: 10 }));
    var tx = svgEl('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central' });
    svgMultiline(tx, m.x, m.y, n.label, 26);
    g.appendChild(tx);
    nodeLayer.appendChild(g);
  });

  (data.labels || []).forEach(function(l) {
    var lt = svgEl('text', { 'class': l.cls || 'diagram-note', 'text-anchor': l.anchor || 'middle' });
    svgMultiline(lt, l.x, l.y, l.text, 24);
    labelLayer.appendChild(lt);
  });

  svg.appendChild(edgeLayer);
  svg.appendChild(nodeLayer);
  svg.appendChild(labelLayer);
  wrap.appendChild(svg);
  return wrap;
}
/* ==== ADDED LAYOUT TYPE: Diagram renderer helpers - end ==== */
```

**Piece 2 -- diagram branch in `buildSlide()`.** This is where the renderer is called. Insert it after the
`query` branch's closing `'</div>';` and before the final `}` that closes the if/else chain (just above `return div;`):

```js
  /* ==== ADDED LAYOUT TYPE: diagram branch - begin ==== */
  } else if (data.type === 'diagram') {
    div.innerHTML =
      '<div class="slide-title">' + esc(data.title) + '</div>' +
      '<div class="diagram-caption">' + esc(data.caption) + '</div>';
    div.appendChild(buildDiagram(data));
  /* ==== ADDED LAYOUT TYPE: diagram branch - end ==== */
```

**Piece 3 -- optional query panel labels (`codeLabel` / `resultLabel`).** Paste at the very end of the
script, after the `prev`/`next` click handlers (it needs `slideEls`, which the engine has already built):

```js
/* ==== ADDED: optional panel labels for query slides (codeLabel / resultLabel) - begin ==== */
/* The verbatim engine labels query panels 'SPARQL' / 'Live Results'. This deck shows
   Python, so slides may override the labels. textContent only - no markup injection. */
SLIDES.forEach(function(s, i) {
  if (s.type !== 'query') return;
  var labels = slideEls[i].querySelectorAll('.query-panel-label');
  if (s.codeLabel && labels[0]) labels[0].textContent = s.codeLabel;
  if (s.resultLabel && labels[1]) labels[1].textContent = s.resultLabel;
});
/* ==== ADDED: optional panel labels for query slides - end ==== */
```

### 7c. JS add-ons for `split`, `stats` and `bars` slides

Two pieces, each delimited by `ADDED` comments. They rely on `svgEl()` from Section 7b Piece 1, so
paste that piece as well even if the deck has no diagram slides.

**Piece 1 -- renderers.** Paste right after the Section 7b Piece 1 helpers, before `function esc(s)`:

```js
/* ==== ADDED LAYOUT TYPES: split / stats / bars renderers - begin ==== */
/* Build DOM from static SLIDES data only. All text is set with textContent
   (never innerHTML), so no markup can be injected. Uses svgEl() above. */
function xEl(tag, cls, text) {
  var e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) e.textContent = text;
  return e;
}

function xList(items) {
  var ul = xEl('ul', 'x-list');
  (items || []).forEach(function(t) { ul.appendChild(xEl('li', null, t)); });
  return ul;
}

function xArrow(w, h) {
  var svg = svgEl('svg', { viewBox: '0 0 ' + w + ' ' + h });
  var mid = h / 2;
  svg.appendChild(svgEl('path', { d: 'M 4 ' + mid + ' L ' + (w - 18) + ' ' + mid,
                                  stroke: '#FF9000', 'stroke-width': '4', fill: 'none' }));
  svg.appendChild(svgEl('path', { d: 'M ' + (w - 20) + ' ' + (mid - 12) + ' L ' + (w - 2) + ' ' + mid +
                                     ' L ' + (w - 20) + ' ' + (mid + 12) + ' z', fill: '#FF9000' }));
  return svg;
}

function buildSplit(data, div) {
  if (data.lead) div.appendChild(xEl('div', 'x-lead', data.lead));
  var row = xEl('div', 'split-row');
  function panel(p, side) {
    var d = xEl('div', 'split-panel ' + side);
    d.appendChild(xEl('div', 'split-panel-title', p.title));
    if (p.tag) d.appendChild(xEl('div', 'split-tag', p.tag));
    d.appendChild(xList(p.items));
    return d;
  }
  row.appendChild(panel(data.left, 'left'));
  var mode = data.connector === 'divider' ? 'divider' : 'arrow';
  var conn = xEl('div', 'split-connector ' + mode);
  if (mode === 'divider') {
    conn.appendChild(xEl('div', 'split-vline'));
    conn.appendChild(xEl('div', 'split-connector-label', data.connectorLabel || ''));
    conn.appendChild(xEl('div', 'split-vline'));
  } else {
    if (data.connectorLabel) conn.appendChild(xEl('div', 'split-connector-label', data.connectorLabel));
    conn.appendChild(xArrow(110, 40));
  }
  row.appendChild(conn);
  row.appendChild(panel(data.right, 'right'));
  div.appendChild(row);
  if (data.shared) {
    var sh = xEl('div', 'split-shared');
    sh.appendChild(xEl('div', 'split-shared-title', data.shared.title));
    sh.appendChild(xList(data.shared.items));
    div.appendChild(sh);
  }
}

function buildStats(data, div) {
  var cols = 0;
  data.tiles.forEach(function(t) { cols += t.span || 1; });
  var grid = xEl('div', 'stats-grid');
  grid.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';
  data.tiles.forEach(function(t) {
    var tile = xEl('div', 'stat-tile');
    if (t.span) tile.style.gridColumn = 'span ' + t.span;
    tile.appendChild(xEl('div', 'stat-figure', t.figure));
    tile.appendChild(xEl('div', 'stat-text', t.text));
    grid.appendChild(tile);
  });
  div.appendChild(grid);
  if (data.pair) {
    var pr = xEl('div', 'stats-pair');
    pr.appendChild(xEl('div', 'stats-pair-title', data.pair.title));
    [data.pair.before, data.pair.after].forEach(function(s, i) {
      if (i === 1) {
        var ar = xEl('div', 'stats-pair-arrow');
        ar.appendChild(xArrow(56, 30));
        pr.appendChild(ar);
      }
      var side = xEl('div', 'stats-pair-side' + (i === 1 ? ' after' : ''));
      side.appendChild(xEl('div', 'stats-pair-when', s.when));
      side.appendChild(xEl('div', 'stats-pair-text', s.text));
      pr.appendChild(side);
    });
    div.appendChild(pr);
  }
  if (data.footer) div.appendChild(xEl('div', 'stats-footer', data.footer));
}

function buildBars(data, div) {
  if (data.head) div.appendChild(xEl('div', 'bars-head', data.head));
  if (data.mode === 'gauges') {
    var row = xEl('div', 'gauges-row');
    var gs = xEl('div', 'gauges');
    data.gauges.forEach(function(g) {
      var gd = xEl('div', 'gauge' + (g.low ? ' low' : ''));
      var top = xEl('div', 'gauge-top');
      top.appendChild(xEl('div', 'gauge-label', g.label));
      top.appendChild(xEl('div', 'gauge-value', g.display || (g.value + '%')));
      gd.appendChild(top);
      var track = xEl('div', 'gauge-track');
      var fill = xEl('div', 'gauge-fill');
      fill.style.width = Math.max(0, Math.min(100, g.value)) + '%';
      track.appendChild(fill);
      gd.appendChild(track);
      if (g.caption) gd.appendChild(xEl('div', 'gauge-caption', g.caption));
      gs.appendChild(gd);
    });
    if (data.gaugeNote) gs.appendChild(xEl('div', 'gauge-note', data.gaugeNote));
    row.appendChild(gs);
    var lst = xEl('div', 'gauges-list');
    lst.appendChild(xList(data.items));
    row.appendChild(lst);
    div.appendChild(row);
    return;
  }
  var trk = xEl('div', 'bars-track');
  var colsEl = xEl('div', 'bars-cols');
  data.segments.forEach(function(s, i) {
    var c = 'c' + (i % 3);
    var seg = xEl('div', 'bars-seg ' + c, s.display || (s.value + '%'));
    seg.style.flexGrow = s.value;
    trk.appendChild(seg);
    var col = xEl('div', 'bars-col');
    col.style.flexGrow = s.value;
    col.appendChild(xEl('div', 'bars-col-title ' + c, s.label));
    col.appendChild(xEl('div', 'bars-col-text', s.text));
    colsEl.appendChild(col);
  });
  div.appendChild(trk);
  if (data.barNote) div.appendChild(xEl('div', 'bars-note', data.barNote));
  div.appendChild(colsEl);
  if (data.footer) {
    var ft = xEl('div', 'bars-foot');
    ft.appendChild(xList(data.footer));
    div.appendChild(ft);
  }
}
/* ==== ADDED LAYOUT TYPES: split / stats / bars renderers - end ==== */
```

**Piece 2 -- branch in `buildSlide()`.** Insert directly after the diagram branch (Section 7b Piece 2),
before the final `}` that closes the if/else chain (just above `return div;`):

```js
  /* ==== ADDED LAYOUT TYPES: split / stats / bars branch - begin ==== */
  } else if (data.type === 'split' || data.type === 'stats' || data.type === 'bars') {
    div.appendChild(xEl('div', 'slide-title', data.title));
    if (data.type === 'split') buildSplit(data, div);
    else if (data.type === 'stats') buildStats(data, div);
    else buildBars(data, div);
  /* ==== ADDED LAYOUT TYPES: split / stats / bars branch - end ==== */
```

---

## 8. Full HTML Shell (the outer wrapper -- never changes)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DECK TITLE HERE</title>
<style>
  /* PASTE CSS BLOCK HERE (Section 6) */
</style>
</head>
<body>

<div id="bar"></div>
<div id="counter">1 / 22</div>  <!-- JS overwrites this immediately from SLIDES.length; the hardcoded value is a placeholder only -->
<button class="arr" id="prev">&#8249;</button>
<button class="arr" id="next">&#8250;</button>
<div id="dots"></div>
<div id="stage"></div>

<script>
const SLIDES = [ /* PASTE SLIDE DATA HERE (Section 5) */ ];

/* PASTE JS ENGINE HERE (Section 7) */
</script>
</body>
</html>
```

---

## 9. Content Extraction Rules

### From a `build_deck.py` file
- Each `slide = prs.slides.add_slide(...)` block = one slide
- `set_text(ph.text_frame, "TITLE TEXT", ...)` on placeholder idx 0 = the slide title
- `add_bullet_list(..., items=[...])` = `type: 'bullets'`, items array is the content
- `add_table(..., headers=[...], rows=[...])` = `type: 'table'`
- Slide 1 with centered title + subtitle textboxes = `type: 'cover'`

### From a Markdown workplan
- Look for the PPTX generation section (usually labelled "Slide N --" or "## Slides")
- Each slide heading becomes the `title`
- Bullet lists beneath become `items`
- Tables (Markdown pipe format) become `type: 'table'` rows

### Content quality rules
- Bullet text: trim to one idea per bullet, max ~120 characters per line
- Table cells: keep concise; long cells cause overflow at 1600x900
- Slide count: 10-25 slides is the sweet spot; over 30 the dot nav gets cramped

---

## 10. Output and File Naming

- Output file: `<TopicName>_reel.html` in the same folder as the source content
- No companion files needed -- the HTML is fully self-contained
- No build step, no server -- just open in any browser
- Navigation: arrow keys, spacebar, click arrows, click dots

---

## 11. Pre-Write Checklist

Before running the Write tool:

- [ ] Content source confirmed and read
- [ ] Slide list extracted and typed (cover / bullets / table / query / diagram / split / stats / bars)
- [ ] Output filename and folder confirmed with user
- [ ] Cover slide fields filled (tag, title, subtitle, sub2)
- [ ] Table slides have <= 4 columns and <= 6 rows
- [ ] Bullet slides have <= 8 items each
- [ ] Query slides have resultHeaders and resultRows populated with real data (not placeholders)
- [ ] SLIDES array count matches expected slide count
- [ ] No Unicode box-drawing characters in any string (use plain ASCII only)
- [ ] Diagram slides: every edge `from`/`to` references an existing node `id` (bad ids are silently dropped)
- [ ] Diagram slides: every node box (x +/- w/2, y +/- h/2) fits inside the 1400 x 600 viewBox
- [ ] Diagram or panel-label add-ons used: Section 6b CSS and Section 7b JS pieces pasted
- [ ] Split / stats / bars used: Section 6c CSS and Section 7c JS pieces pasted (plus 7b Piece 1 for `svgEl()`)
- [ ] Restyling bullet slides: every original item string still appears verbatim in the new slide data (check by script)
- [ ] Stats tiles: each `figure` already appears in its own `text`; long figures use `span: 2`
- [ ] Bars: segment `value`s are the real figures (label derived totals as derived); gauges `value` 0-100
- [ ] Layout checked in a browser (or headless Chrome screenshot) at 1600x900: no text clipped by the slide's `overflow: hidden`
- [ ] Script syntax checked: extract the `<script>` content and run `node --check` on it (if node is available)
- [ ] Whole file scanned for non-ASCII characters (zero expected)
- [ ] Presented proposed change to user and received approval before Write

---

## 12. Adding a New Slide

1. Append or insert an object into the `SLIDES` array
2. Choose `type` from: `cover`, `bullets`, `table`, `query`, `diagram`, `split`, `stats`, `bars`
3. Populate the required fields for that type (see Section 4)
4. No other changes needed -- the renderer and counter update automatically from `SLIDES.length`

## 13. Adding a New Layout Type

1. Add CSS for the new layout inside the `<style>` block (follow the `/* ---- Query slides ---- */` pattern)
2. Add an `else if (data.type === 'newtype') { ... }` branch inside `buildSlide()` before the final `return div;`
3. Document the new type in Section 4 of this file with: layout description, required fields, CSS classes used, and use-cases

Note: the `diagram` type (Section 4e, add-ons in 6b and 7b) was added this way on 2026-11-18 for `AgentOrchestration/research_desk/AgentOrchestration_reel.html`.

Note: the `split`, `stats` and `bars` types (Sections 4f-4h, add-ons in 6c and 7c) were added the same way on 2026-11-18 for the same reel, to restyle bullet-only slides without removing any text (slides 2, 3, 14, 17 and 18 of that deck).
