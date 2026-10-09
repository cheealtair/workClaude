---
name: multi-column
description: Create a slide with content equally divided across multiple columns (default 2)
---

## Instructions

When asked to create a multi-column slide:

1. **Determine the number of columns**: Use the number specified by the user. If not specified, default to **2 columns**.
2. **Count the total rows** of content (table rows, bullet points, or list items) to be displayed.
3. **Divide rows equally** across columns:
   - Total rows / number of columns = rows per column
   - If the division is uneven, place the extra rows in the leftmost column(s)
   - Example: 17 rows across 3 columns = 6, 6, 5
4. **Calculate positioning** based on the slide dimensions (13.3" x 7.5"):
   - Usable width: 12.3" (0.5" margin on each side)
   - Column width: usable width / number of columns, with 0.2" gap between columns
   - All columns start at the same vertical position (below the title)
5. **Render each column as a single table** — never stack multiple small tables vertically within a column. Instead, flatten all content into one table per column. If there are section/group headers (e.g., era names), render them as merged rows within the single table with distinct background colors. This eliminates overlap caused by python-pptx height estimates diverging from PowerPoint's rendered heights.
6. **Preserve continuity**: if the content has headers (e.g., a table), repeat the header row at the top of each column (or after each section header row) so each column is independently readable
7. **Compact row heights**: PowerPoint auto-expands rows based on paragraph spacing, not just font size. To prevent oversized rows:
   - Set cell `margin_top` and `margin_bottom` to `Pt(1)` — the minimum practical padding (~0.35mm) that keeps text from touching the cell border without inflating row height
   - Set paragraph `space_before` and `space_after` to `Pt(0)`
   - Set `line_spacing` to `Pt(font_size + 2)` for tight vertical fit
   - Set explicit `row.height` on each row (e.g., `Inches(0.13)` for data rows, `Inches(0.15)` for header rows)
   - Note: `row.height` is a minimum — without zeroing paragraph spacing, PowerPoint will still expand rows
8. **Keep formatting consistent** across all columns — same font size, colors, and cell padding

### Column width formula

```
gap = 0.2 inches
total_gaps = (num_columns - 1) * gap
column_width = (usable_width - total_gaps) / num_columns
column_left(i) = left_margin + i * (column_width + gap)
```

### Key lessons learned

- **Never stack multiple tables vertically** in a column. python-pptx cannot predict PowerPoint's rendered table height, so stacked tables will overlap. Use one table per column with section headers as merged rows.
- **Paragraph spacing is the main culprit** for oversized rows, not cell margins or row.height. Always zero out `space_before` and `space_after` on every paragraph in every cell.

### Examples

- "Make this a multi-column slide" → 2 columns, rows split evenly
- "Use 3 columns for this slide" → 3 columns
- "Put this table in 4 columns" → 4 columns, header repeated in each
