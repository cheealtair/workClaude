---
name: build-deck
description: Generate a PowerPoint deck from workplan.md using the project template
---

## Configuration

Before building, load `deck_style.json` from the current folder. This file externalizes all styling constants so they are not hard-coded in the Python build script. If the file does not exist, use the defaults from CLAUDE.md.

### deck_style.json format

```json
{
  "colors": {
    "title": "#66BF66",
    "subtitle": "#66BF66",
    "textbox": "#FFFFFF",
    "table_header_bg": "#003A70",
    "table_header_font": "#FFFFFF",
    "table_cell_font": "#333333",
    "era_header_bg": "#003A70",
    "era_header_font": "#FFFFFF",
    "col_header_bg": "#D5E8F0",
    "product_highlight": "#C0392B"
  },
  "cell_padding": {
    "margin_top_pt": 1,
    "margin_bottom_pt": 1,
    "margin_left_pt": 2,
    "margin_right_pt": 2,
    "space_before_pt": 0,
    "space_after_pt": 0,
    "line_spacing_offset_pt": 2
  },
  "row_heights": {
    "data_row_in": 0.13,
    "header_row_in": 0.15,
    "era_header_row_in": 0.15
  },
  "script_text": {
    "font_size_pt": 11,
    "space_after_pt": 2,
    "content_left_in": 0.3,
    "content_top_in": 1.3,
    "content_width_in": 12.7,
    "content_height_in": 6.0
  },
  "slide_text": {
    "title_size_pt": 32,
    "subtitle_size_pt": 28,
    "bullet_size_pt": 14,
    "bullet_space_after_pt": 4,
    "content_left_in": 0.5,
    "content_top_in": 1.5,
    "content_width_in": 12.3,
    "content_height_in": 5.5
  }
}
```

The build script should parse this JSON at the top and use the values as variables throughout, instead of hard-coding RGBColor values and Pt/Inches constants inline.

## Workplan Conventions

- Lines prefixed with `[NOTE: ...]` are instructions to Claude — do NOT render them on slides.
- All other content is slide content that should appear in the PPTX.

## Instructions

1. Read `workplan.md` in the current folder
2. Load `deck_style.json` from the current folder for all color, padding, and row height values
3. Open `Template_Apr2026.pptx` from the current folder as the base template
3. Use the **"Free Content"** layout (index 23) as the default for all slides unless the workplan specifies otherwise. This layout provides:
   - A title placeholder (idx 0) for the slide title
   - A blank canvas below the title for freely positioned content (text boxes, tables, images, shapes)
4. For each slide in the outline, create a slide with:
   - The slide title placed in the layout's title placeholder
   - Bullet points rendered as text boxes, positioned below the title
   - Tables built with `python-pptx` table objects, using compact cell formatting (see table rules below)
   - Any referenced image from the `images/` subfolder, sized and positioned appropriately
5. Slide dimensions are 13.3" x 7.5" (widescreen 16:9) — position content accordingly
6. **Table construction rules** (apply to all tables in the deck):
   - **One table per visual group** — never stack multiple small tables vertically. If content has sections/groups, use merged rows within a single table for section headers.
   - **Compact rows** — for every cell, set: `margin_top=Pt(1)`, `margin_bottom=Pt(1)` (minimum practical padding ~0.35mm), paragraph `space_before=Pt(0)`, `space_after=Pt(0)`, `line_spacing=Pt(font_size + 2)`. Without this, PowerPoint's default paragraph spacing inflates row heights.
   - **Explicit row heights** — set `row.height` on each row (e.g., `Inches(0.13)` for data, `Inches(0.15)` for headers). This is a minimum — paragraph spacing must also be zeroed or rows will still expand.
6. Apply any additional formatting from the "Design & Formatting Guidelines" section in the workplan
7. Before saving, copy the existing output PPTX (if it exists) to a backup with `_OLD` suffix (e.g., `AEPpartner_June2026_OLD.pptx`). This lets the user manually revert if needed. Subsequent runs overwriting the `_OLD` file is fine — only the most recent previous version is kept.
8. Save the output as the filename specified in "Slide Deck Details"
8. Report: number of slides created, layout used per slide, which images were embedded, any missing references
