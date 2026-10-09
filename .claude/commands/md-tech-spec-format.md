---
name: md-tech-spec-format
description: Format a Markdown file as a technical implementation specification — LLM-retrievable and human-scannable
---

Apply the following structure to a Markdown technical specification document. This format is for build workplans, implementation specs, ontology designs, ML model specs, and Mendix application designs — not for business ebooks (use /md-book-format) and not for research notes (use /md-research-format).

## YAML Frontmatter (required)

```yaml
---
title: "..."
document_type: technical-implementation
project: "..."
status: draft | in-progress | complete
version: "0.1"
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "..."
related_document: "..."
scope: "one sentence describing what this spec covers"
audience: "solution architects, data engineers, developers"
---
```

## Section Tags (required on every section heading)

Every `##` or `###` heading must be prefixed with a type tag in square brackets. Tags tell both LLMs and humans exactly what kind of content follows without reading it.

| Tag | Use for |
|---|---|
| `[DATA]` | Dataset definitions, field specs, sample records |
| `[ONTOLOGY]` | Classes, properties, namespaces, TTL fragments |
| `[ETL]` | Ingestion steps, transformation pipelines, load order |
| `[RULE]` | Business rules, detection rules, workflow rules |
| `[ML]` | Model objective, features, algorithm, evaluation, deployment |
| `[MENDIX]` | Domain model, pages, workflow stages, security model |
| `[INTEGRATION]` | Component maps, API specs, SPARQL queries used by apps |
| `[TESTING]` | Test cases, validation criteria, acceptance conditions |
| `[SPARQL]` | Standalone SPARQL query definitions |
| `[API]` | REST endpoint specs, request/response payloads |

Example heading: `### [RULE] 5.2 Detection Rules`

## Code Blocks (required for all code and data)

Always use fenced code blocks with a language tag:

```
```turtle     — OWL/RDF ontology
```sparql     — SPARQL queries
```json       — data samples, API payloads, config
```python     — Python scripts
```bash       — shell commands
```sql        — SQL queries
```xml        — XML / RMP process files
```

## Tables for Rules and Specs

Business rules, test cases, field definitions, and feature sets must be in Markdown tables — not prose, not bullets. Tables are the most LLM-parseable and human-scannable format for structured specifications.

Rule table columns: `Rule ID | Name | Condition | Threshold/Value | Action/Output`
Test case columns: `Test ID | Description | Expected Result`
Field spec columns: `Field | Type | Values / Format | Notes`

## Status Markers

Mark completion state on every section or item:

- `*(defined)*` — fully specified, ready to build
- `*(in-progress)*` — partially complete
- `*(pending)*` — not yet started
- `*(validated)*` — built and tested

## Prose Style

- Short declarative sentences — one idea per sentence
- No narrative openers, no literary prose, no padding
- State what the system does, not why it is interesting
- Use active voice: "The Mendix workflow routes the alert" not "Alerts are routed"
- No `\newpage` markers

## Document Structure (recommended)

```
Part 1: Problem Definition and Scope
Part 2: Data Sources and Synthetic Datasets   [DATA]
Part 3: Ontology Design                       [ONTOLOGY]
Part 4: ETL Pipeline Design                   [ETL]
Part 5: Business Rules                        [RULE]
Part 6: ML Model Specification                [ML]
Part 7: Application Design                    [MENDIX] or [APP]
Part 8: Integration Architecture              [INTEGRATION]
Part 9: Testing and Validation                [TESTING]
Appendix A: Open Items
Appendix B: Reference Links
```

Omit parts that are not relevant to the specific build. Do not add parts not listed here without good reason.

## What This Format Is NOT For

- Business/executive documents — use `/md-book-format`
- Research notes and findings — use `/md-research-format`
