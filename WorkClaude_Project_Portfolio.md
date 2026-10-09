# WorkClaude Project Portfolio

*Generated: 2026-09-19*

---

## 1. AEPpartner_June2026

**What:** Partner-facing PowerPoint deck for an AEP (Altair/AGS) partner event, June 2026. Includes a TAM (Technical Account Manager) slides build plan and SRT video transcript integration.

**Tech:** python-pptx, custom `build_deck.py`, `deck_style.json` styling config, Siemens Template PPTX

**Impact:** Full deck produced (`.pptx` + `.pdf`), multiple saved versions — used in a live partner event

---

## 2. AWS_Siemens

**What:** Multi-chapter AWS integration manual for Siemens Graph Studio deployments. Structured as modular markdown chapters.

**Tech:** Markdown, 6-chapter manual structure

**Impact:** Reference documentation for AWS-hosted AGS deployments

---

## 3. BFSI

**What:** 30-chapter ebook on Banking/Financial Services/Insurance AI use cases + a companion SMR technical build spec. Also contains a Tax Evasion / Grey Economy detection sub-project with its own ontology and data pipeline.

**Tech:** OWL ontology, SPARQL, Graph Studio MCP, synthetic data generation, Pandoc/Eisvogel for PDF output

**Impact:** Full workplan authored for 30-chapter ebook; TaxEvasion ontology and dataset pipeline scoped

---

## 4. CRISP-MD

**What:** Application of the CRISP-DM data science methodology to the Titanic dataset — a methodology framework demo with an intent document.

**Tech:** CRISP-DM, Titanic CSV/XLS dataset, Markdown intent doc

**Impact:** Proof-of-concept methodology walkthrough; useful as a training example

---

## 5. GraphViz_AGS

**What:** A web app to visualize AGS (Altair Graph Studio) knowledge graphs inside a Mendix iframe. Includes a live polling server and authentication layer.

**Tech:** Python Flask/Streamlit (`app.py`), `ags_client.py`, `poll_server.py`, JSON config, Mendix iframe embedding

**Impact:** Enables embedded graph visualization in low-code Mendix apps — bridges two enterprise platforms

---

## 6. Industrial_Enterprise_Optimization

**What:** PowerPoint deck on industrial enterprise optimization use cases, likely for a customer/partner presentation.

**Tech:** python-pptx, `build_deck.py`, `deck_style.json`, workplan-driven slide generation

**Impact:** Deck generated and archived; part of the reusable deck-generation framework

---

## 7. Northwind

**What:** Full procurement knowledge graph built on the Northwind sample database. Ingested into Altair Graph Studio via 7-phase pipeline. ~111K RDF triples.

**Tech:** OWL ontology, Turtle (TTL), SPARQL, Python batch loader, AGS Graph Studio (Path E), PostgreSQL source

**Impact:** 111,000 triples loaded; complete procurement KG with supplier/order/product relationships queryable via SPARQL

---

## 8. Notes_LLMwiki

**What:** Personal LLM knowledge base — a structured wiki of AI/LLM concepts, ingested articles, QA notes, and research workplans.

**Tech:** Markdown wiki, `wiki/index.md` catalog, `wiki/log.md` activity log, pdfplumber for PDF ingestion, Pandoc for export

**Impact:** Ongoing knowledge accumulation; referenced in sessions for AI architecture, model setup, and competitive analysis

---

## 9. OrionBeltGraph

**What:** Streamlit-based ontology builder and viewer — a standalone tool for creating and exploring OWL ontologies visually.

**Tech:** Python, Streamlit, `ontology_manager.py`, separate git repo

**Impact:** Reusable open-source-style ontology tooling; `pyproject.toml` suggests packaging intent

---

## 10. RMGS_Tech

**What:** Technical reference for AGS (RMGS = RDF/Multi-Graph Studio), including a support bot and setup workplan for v2609 deployment.

**Tech:** Markdown guides, data ingestion pipelines, AGS v2609, support bot scaffold

**Impact:** Accelerates AGS onboarding; support bot provides self-service troubleshooting

---

## 11. STEP_Format

**What:** Research into STEP (ISO 10303) format semantics — likely for mapping industrial product data into RDF/ontology representations.

**Tech:** STEP/ISO 10303 format analysis, Markdown documentation

**Impact:** Foundation for industrial CAD/PLM data integration into knowledge graphs

---

## 12. TollHoldings

**What:** Pre-sales engagement documentation for Toll Holdings — reference emails and meeting materials for an Altair RapidMiner AI Studio pitch.

**Tech:** Markdown, email reference doc

**Impact:** Meeting held 2026-05-27; pre-sales collateral prepared

---

## 13. VoiceAI

**What:** Text-to-speech experiments — accent testing, voice embedding, and audio output scripts using edge-tts.

**Tech:** Python, `edge-tts`, multiple TTS scripts (`speak.py`, `accents.py`, `embed_voice.py`, `listen.py`)

**Impact:** Prototype TTS capability; accent variety tested; groundwork for voice-enabled AI interfaces

---

## 14. ai-enablement

**What:** AI enablement kit for the ICX Tiger Team — presales + technical enablement materials for Altair Graph Studio. Covers GTM agent KB, customer experience playbooks, industry demos, cost estimators, and training.

**Tech:** HTML presentations, Markdown guides, structured folder system per enablement area

**Impact:** 6 enablement domains covered; kit deployed to `code.siemens.com/tigerteam` repo

---

## 15. myGraphCRM

**What:** A graph-native CRM system — customers, partners, and ontology modeled as RDF graphs rather than relational tables.

**Tech:** OWL ontology, Turtle TTL, SPARQL, Markdown intent doc, graph-first schema design

**Impact:** Working ontology drafted; customer/partner entities and relationships defined; early-stage but architecturally complete

---

## 16. rapidminer

**What:** RapidMiner AI Studio process XML files — Decision Tree samples, a modernization agent loop workplan, and v2026 compatibility work.

**Tech:** RapidMiner `.rmp` XML, 8 operator categories (Learner, Preprocessing, Validation, etc.), v2026.1.1 API

**Impact:** 122 sample processes catalogued; custom processes built; CLI testing documented

---

## 17. vtt

**What:** Video transcript extraction workspace — VTT/SRT files from AI-related video sessions (Hermes Agent Skills, Claude Code Mendix build session, Ed Donner AI Harness talk).

**Tech:** VTT/SRT format, `video_vtt_extract` skill

**Impact:** Transcripts extracted and ready for ingestion into the LLM wiki or notes

---

## Summary

| # | Project | Domain | Primary Stack |
|---|---------|--------|---------------|
| 1 | AEPpartner_June2026 | Presentations | python-pptx |
| 2 | AWS_Siemens | Documentation | Markdown |
| 3 | BFSI | Ebook + KG | OWL, SPARQL, Pandoc |
| 4 | CRISP-MD | Data Science | CRISP-DM, Python |
| 5 | GraphViz_AGS | Web App | Python, Streamlit, Mendix |
| 6 | Industrial_Enterprise_Optimization | Presentations | python-pptx |
| 7 | Northwind | Knowledge Graph | OWL, SPARQL, AGS, PostgreSQL |
| 8 | Notes_LLMwiki | Knowledge Base | Markdown, Pandoc |
| 9 | OrionBeltGraph | Ontology Tooling | Python, Streamlit |
| 10 | RMGS_Tech | AGS Reference | Markdown, AGS v2609 |
| 11 | STEP_Format | Industrial Data | STEP/ISO 10303 |
| 12 | TollHoldings | Pre-Sales | Markdown |
| 13 | VoiceAI | TTS / Voice | Python, edge-tts |
| 14 | ai-enablement | Enablement Kit | HTML, Markdown |
| 15 | myGraphCRM | CRM / Graph | OWL, SPARQL, TTL |
| 16 | rapidminer | ML Workflows | RapidMiner XML (.rmp) |
| 17 | vtt | Transcripts | VTT/SRT |

**17 active projects** spanning knowledge graphs, PowerPoint automation, TTS, CRM, pre-sales enablement, ontology tooling, and AI methodology. Dominant stack: **Python + OWL/SPARQL + Altair Graph Studio**, with **python-pptx** and **Markdown-driven automation** as recurring themes.
