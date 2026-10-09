---
name: md-book-format
description: Reformat a Markdown document for book-quality PDF/ebook rendering via Pandoc + Eisvogel
---

Apply the following rules to restructure a Markdown file so it renders as a professional book when processed with Pandoc and the Eisvogel LaTeX template.

## Step 1 — Add YAML Frontmatter (if not present)

Insert at the very top of the file:

```yaml
---
title: "..."
subtitle: "..."
author: "..."
date: "..."
subject: "..."
lang: "en"
toc: true
toc-own-page: true
numbersections: true
colorlinks: true
linkcolor: blue
titlepage: true
titlepage-color: "108000"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "66BF66"
fontsize: 11pt
geometry: "margin=2.5cm"
---
```

Fill title, subtitle, author, date, subject from the document content.

## Step 2 — Heading Hierarchy

Enforce strictly — never skip levels:

- `#` = Part title only
- `##` = Chapter title only
- `###` = Section within a chapter
- `####` = Sub-section

## Step 3 — Page Breaks

Add `\newpage` on its own line before:
- Every Part opener (`#`)
- Every Chapter opener (`##`)
- The end of each chapter (before the closing note)

Pandoc/Eisvogel honours `\newpage`. GitHub's MD renderer ignores it harmlessly.

## Step 4 — Part Openers

Each Part must have a prose paragraph immediately after its `#` heading — before the first chapter begins. This paragraph explains what the Part covers and why it matters. No tables or bullets on the Part opener page.

## Step 5 — Chapter Openers

Every chapter (`##`) must open with at least one full prose paragraph before any table, bullet list, or sub-section heading. This sets the scene and reads like a book, not notes.

## Step 6 — Section Openers

Every `###` section should have at least one sentence of prose before lists or tables. A section that opens directly with a bullet list reads as raw notes, not finished content.

## Step 7 — No Orphan Bullets

Never use a bullet list for a single item. Write it as a sentence instead.

## Step 8 — No Horizontal Rules

Remove all `---` horizontal rules used as visual dividers within chapters and sections. They create clutter in rendered output. Section headings provide the visual separation.

## Step 9 — Blank Line Discipline

- One blank line between paragraphs
- Two blank lines before a `###` or `####` heading (improves source readability)
- One blank line after every heading before content begins

## Step 10 — Render Command

After reformatting, remind the user of the render command:

```bash
pandoc <filename>.md -o <filename>.pdf --pdf-engine=xelatex --template=eisvogel
```

Pandoc 3.10.2 and Eisvogel 3.5.1 are installed on this machine.
XeLaTeX (MiKTeX or TeX Live) is required for local PDF rendering but is not yet installed — GitHub Actions runners have it available.
