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

Four slide types are supported. Choose based on content structure.

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
- [ ] Slide list extracted and typed (cover / bullets / table / query)
- [ ] Output filename and folder confirmed with user
- [ ] Cover slide fields filled (tag, title, subtitle, sub2)
- [ ] Table slides have <= 4 columns and <= 6 rows
- [ ] Bullet slides have <= 8 items each
- [ ] Query slides have resultHeaders and resultRows populated with real data (not placeholders)
- [ ] SLIDES array count matches expected slide count
- [ ] No Unicode box-drawing characters in any string (use plain ASCII only)
- [ ] Presented proposed change to user and received approval before Write

---

## 12. Adding a New Slide

1. Append or insert an object into the `SLIDES` array
2. Choose `type` from: `cover`, `bullets`, `table`, `query`
3. Populate the required fields for that type (see Section 4)
4. No other changes needed -- the renderer and counter update automatically from `SLIDES.length`

## 13. Adding a New Layout Type

1. Add CSS for the new layout inside the `<style>` block (follow the `/* ---- Query slides ---- */` pattern)
2. Add an `else if (data.type === 'newtype') { ... }` branch inside `buildSlide()` before the final `return div;`
3. Document the new type in Section 4 of this file with: layout description, required fields, CSS classes used, and use-cases
