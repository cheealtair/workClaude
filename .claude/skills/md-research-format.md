---
name: md-research-format
description: Format a Markdown file as a research document — citable, confidence-marked, LLM-retrievable
---

Apply the following structure to a Markdown research document. This format is for working notes, findings, literature reviews, and evolving research — not for business ebooks (use /md-book-format) and not for technical build specs (use tagged technical spec format).

## YAML Frontmatter (required)

```yaml
---
title: "..."
type: research
topic: "..."
status: draft | active | complete
confidence: high | medium | low
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "..."
sources: []
related: []
tags: []
---
```

- `confidence` reflects overall confidence in the findings, not the writing quality
- `sources` lists raw source files, URLs, or documents consulted
- `related` lists other MD files that are connected to this research
- `tags` are free-form keywords for retrieval

## Section Structure

### Summary (required, always first)
2-5 sentences. What is known, with what confidence, as of the document date. Written to be read in isolation — a future LLM or human should understand the conclusion without reading the rest.

### Findings
One `####` sub-heading per distinct finding. Each finding block:

```markdown
#### Finding: <short label>
**Confidence:** high | medium | low
**Source:** <source name or URL>

<1-3 sentences describing the finding. State what is known, not what might be.>
```

### Open Questions
Bulleted list of unresolved questions that further research should address. Honest gaps, not rhetorical questions.

### Hypotheses (optional)
Clearly labelled as unverified. Format:

```markdown
- **Hypothesis:** <statement> — *unverified, basis: <why you think this>*
```

### Sources Consulted
List all sources with a one-line description of what each contributed.

## Prose Style

- Short declarative sentences — state what is known, not what might be
- Qualify uncertainty explicitly: "likely", "unconfirmed", "no evidence found"
- No literary openers or narrative padding
- No `\newpage` markers
- Confidence markers on every finding — never imply certainty that does not exist

## What This Format Is NOT For

- Business/executive documents — use `/md-book-format`
- Technical build specifications — use tagged technical spec format (`[RULE]`, `[ML]`, `[ONTOLOGY]` etc.)
