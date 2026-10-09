# pptx-theme-graft

Transfer visual style from one PPTX (the "style donor") onto the content of
another PPTX (the "content source"), producing a new output PPTX with zero
content alteration and correct font sizing for the target language.

---

## Inputs required

| Input | Description |
|---|---|
| content_src | PPTX whose shapes, text, and positions are preserved exactly |
| style_donor | PPTX whose visual palette (background, fill colors) is adopted |
| output_path | Destination file — only this file is written |

---

## Step 1 — Diagnose before touching anything

Run three checks FIRST. Do not skip.

1. **Slide size** — content_src and style_donor may differ (e.g. 13.33" vs 20").
   Record content_src dimensions. Output inherits them.
2. **Font inheritance** — for every text shape in content_src, check whether
   `sz` is explicit in `rPr`, in `lstStyle/defRPr`, or absent entirely (= inherited
   from layout/master chain). Record which shapes have `sz=None`.
3. **Color model** — check whether shape fills and text colors use explicit RGB
   (`srgbClr`) or scheme references (`schemeClr`). Scheme colors resolve through
   the theme; swapping the theme changes them silently.

**Key diagnostic: if sz=None count > 50%, the theme must NOT be replaced.**
Replacing the theme breaks the entire inheritance chain for font size and color.

---

## Step 2 — Extract style from donor (read-only)

From style_donor, extract only:
- Background color: read `p:bg/p:bgPr/a:solidFill/a:srgbClr/@val` from slide 1
- Text color palette: collect all `a:srgbClr/@val` from `a:rPr` elements
  across all slides. Most frequent values = primary palette.
- Shape fill color palette: collect all `a:srgbClr/@val` from `spPr/solidFill`

Do NOT copy theme XML. Do NOT copy slide master or layout.

---

## Step 3 — Build color map

Map content_src fill colors to donor palette equivalents by hue similarity:
- content_src teal accent -> donor teal accent
- content_src dark fill -> donor dark fill
- content_src highlight fill -> donor highlight fill
- Text: all runs get donor's primary text color (typically FFFFFF on dark bg)

---

## Step 4 — Apply at slide XML level (zipfile + lxml)

Work at the raw zip level. Never use python-pptx shape factory on files
with complex elements — it raises `AttributeError: 'list' has no attribute
'has_ph_elm'` on grouped or non-standard shapes.

```python
with zipfile.ZipFile(content_src) as src, zipfile.ZipFile(output, 'w') as out:
    for item in src.infolist():
        data = src.read(item.filename)
        if item.filename.startswith('ppt/slides/slide') and item.filename.endswith('.xml'):
            data = process_slide(data, color_map, bg_color)
        out.writestr(item, data)
```

In `process_slide`:
1. Inject `<p:bg><p:bgPr><a:solidFill>...</a:solidFill></p:bgPr></p:bg>` into
   `p:cSld` BEFORE `p:spTree` (not inside it)
2. Remap all `solidFill/srgbClr` values using color_map
3. Convert all `solidFill/schemeClr` to explicit RGB using color_map
4. Inject explicit donor text color into every `a:rPr`

---

## Step 5 — Font size: Pillow-based fit calculation

**Why this is needed:** text in content_src may have been sized for a different
language (e.g. Japanese). Translated text (e.g. English) has different character
counts and metrics. Inherited font sizes cannot be trusted to fit.

### Resolve effective start size per shape

Walk the inheritance chain bottom-up until sz is found:
1. `a:rPr/@sz` in any run
2. `a:pPr/a:defRPr/@sz` in any paragraph
3. `a:lstStyle/*/a:defRPr/@sz` in the text body
4. Same search in slide layout XML (`ppt/slideLayouts/slideLayoutN.xml`)
5. Same search in slide master XML (`ppt/slideMasters/slideMaster1.xml`)
6. Default fallback: 12pt

### Calculate inner box dimensions

```python
inner_w_pt = (cx - lIns - rIns) / 12700   # EMU to points
inner_h_pt = (cy - tIns - bIns) / 12700
# default insets: lIns=rIns=91440, tIns=bIns=45720 EMU
```

### Binary-search for max fitting font size

```python
from PIL import ImageFont

def fits(text, font_pt, box_w_pt, box_h_pt, font_path):
    font_px = int(font_pt * 96 / 72)
    fnt = ImageFont.truetype(font_path, font_px)
    box_w_px = box_w_pt * 96 / 72
    words = text.split()
    lines, cur = [], []
    for word in words:
        if fnt.getlength(' '.join(cur + [word])) <= box_w_px or not cur:
            cur.append(word)
        else:
            lines.append(' '.join(cur)); cur = [word]
    if cur: lines.append(' '.join(cur))
    line_h = fnt.getbbox('Ag')[3] * 1.15
    return (len(lines) * line_h / (96/72)) <= box_h_pt
```

### Group snap for visual consistency

Group shapes by fill color. Within each fill-color group, take the MINIMUM
fitting font size and apply it to all shapes in the group.

Exception: `no_fill` shapes are too diverse (titles, labels, footers) — apply
per-shape sizing, do not snap.

```python
group_snap = {
    color_key: max(6, min(optimal_sizes_for_group))
    for color_key, optimal_sizes_for_group in groups.items()
    if color_key != 'no_fill'
}
```

### Inject explicit sz into XML

```python
sz_hundredths = int(round(final_pt * 100))
for rPr in txBody.findall('.//{NS_A}rPr'):
    rPr.set('sz', str(sz_hundredths))
for defRPr in txBody.findall('.//{NS_A}defRPr'):
    defRPr.set('sz', str(sz_hundredths))
```

---

## Namespace reference

```python
NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
```

txBody is in NS_P. All drawing elements (xfrm, solidFill, rPr, t) are in NS_A.
This mismatch causes silent failures when iterating shapes.

---

## Known failure modes

| Failure | Cause | Fix |
|---|---|---|
| Text invisible on dark bg | scheme text color (tx1=black) on dark bg | Inject explicit donor text color in all rPr |
| Bounding box overflow | Font changed via theme swap | Never swap theme; resolve sz via chain + Pillow |
| 0 shapes found | txBody searched in NS_A but it is in NS_P | Use NS_P for txBody, NS_A for drawing children |
| File locked on write | PowerPoint has file open | Write to temp path; rename after |
| shape factory crash | python-pptx on grouped/non-standard shapes | Use zipfile+lxml only; avoid pptx shape factory |
| Group snap too small | no_fill group too diverse (mixes titles + tiny labels) | Exclude no_fill from group snap; use per-shape sizing |
