# SpecFlow AI — Project Prompt Pack v2

> Document-to-Workflow AI Orchestrator startup prompts for BMS/BAS, HVAC controls, ICS/PLC, SCADA, commissioning, controls drawings, RFIs, OT cybersecurity, PDF Inspector ingestion, source-confirmed filtering, confidence scoring, template routing, and 3-day hackathon planning.

---

# Project Anchor

Use this sentence everywhere:

```text
SpecFlow AI converts messy engineering documents into clean AI-agent-ready Markdown, then uses a BMS/ICS/PLC knowledge base and source-confirmed confidence scoring to generate RFIs, tasks, points-list candidates, CAD actions, field verification items, and commissioning checklists.
```

Core rule:

```text
Known vocabulary is not the same as detected vocabulary. The source document must support every output item.
```

Current ingestion decision:

```text
Use firecrawl/pdf-inspector for local PDF inspection and Markdown extraction.
Do not use the Firecrawl web crawler/API for the MVP.
```

---

# Source-Confirmed Filtering Standard

SpecFlow AI must apply strict filtering between the knowledge base and the source document.

The knowledge base may define that terms such as AHU, RTU, VAV, BACnet/IP, Modbus, PLC, SCADA, VLAN, firewall, and field verification exist.

However, the source document determines whether a term is detected.

If the source document does not support a term, that term must receive confidence `0.00` and must not trigger downstream workflow generation.

## Filtering Layers

### 1. Ingestion Quality Filter

Before extraction, classify the source quality:

- `text_pdf`: extract Markdown normally.
- `mixed_pdf`: extract Markdown where available and flag pages that may need OCR.
- `scanned_pdf`: do not hallucinate; mark as OCR required.
- `image_heavy_pdf`: extract available text only; flag low confidence.
- `empty_or_failed_parse`: stop workflow extraction and request better source.

### 2. Evidence Filter

A detected item must have at least one source-supported evidence record.

Each evidence record should include:

```json
{
  "excerpt": "short source quote or extracted phrase",
  "page": null,
  "section": "",
  "match_type": "exact | alias | inferred | cross_reference",
  "source_reference": ""
}
```

### 3. Confidence Filter

Every term, equipment item, protocol, task, RFI, point, CAD item, submittal item, and commissioning item must carry a confidence score from `0.00` to `1.00`.

### 4. Workflow Gate Filter

Only generate downstream workflow items when the item exceeds its threshold.

Default thresholds:

| Output Type | Minimum Confidence |
|---|---:|
| Equipment template trigger | 0.70 |
| Points-list generation | 0.70 |
| RFI candidate | 0.60 |
| Field verification item | 0.50 |
| CAD task | 0.60 |
| Submittal item | 0.60 |
| Commissioning item | 0.65 |
| Ignore below | 0.40 unless raw detection matrix is requested |

### 5. Suppression Filter

Suppress generated outputs when:

- Required source term is absent.
- Confidence is below threshold.
- Evidence is only from the knowledge base.
- The source uses generic words without a technical qualifier.
- The detected item depends on an unsupported assumption.

Examples:

```text
If RTU is 0.95 and AHU is 0.00, generate RTU workflows only.
If BACnet/IP is 0.90 and Modbus is 0.00, generate BACnet/IP network review only.
If “controller” appears but PLC does not, do not assume PLC.
If “network” appears but BACnet/IP does not, do not assume BACnet/IP.
If “serial” appears but Modbus does not, do not assume Modbus.
```

### 6. Output Mode Filter

SpecFlow AI supports two output modes:

#### Raw Detection Matrix Mode

Shows all knowledge base terms, including `0.00` terms.

Use this to prove what was not detected.

#### Workflow Output Mode

Only includes source-supported terms above the applicable threshold.

Use this for the final engineering workflow package.

---

# Prompt 0 — Master Project Kickoff

```text
Act as a senior AI systems architect, BMS/BAS engineer, OT/ICS cybersecurity engineer, PLC controls engineer, and 3-day hackathon technical lead.

We are starting a new hackathon project called:

SpecFlow AI
Document-to-Workflow AI Orchestrator

The goal is to build a practical AI tool that ingests PDFs, specs, cut sheets, submittals, standards, technical references, controls narratives, points lists, and field documentation, then converts them into clean AI-agent-ready Markdown.

Important ingestion decision:

Use firecrawl/pdf-inspector for local PDF inspection, classification, and Markdown extraction.
Do not use Firecrawl web crawling/API for the MVP.
Do not build URL ingestion unless the PDF pipeline and demo are already working.

The tool is focused on:

- BMS
- BAS
- HVAC controls
- Retrofits
- PLC systems
- ICS / OT systems
- SCADA
- Commissioning
- Controls drawings
- Points lists
- RFIs
- Field verification
- Submittals
- OT cybersecurity

Core workflow:

Source PDF / source text
→ PDF Inspector classification
→ Raw Markdown extraction
→ Markdown cleanup and normalization
→ BMS/ICS/PLC knowledge-base enrichment
→ Source-confirmed term detection
→ Confidence-weighted scoring
→ Filtering and threshold gating
→ Workflow extraction
→ AI-agent-ready Markdown
→ Optional JSON metadata
→ RFIs / tasks / points-list candidates / CAD tasks / commissioning items

Important concept:

The agent must distinguish between:

1. Known vocabulary from the knowledge base
2. Source-confirmed vocabulary from the actual document

The knowledge base may help classify and normalize terms, but it must not invent systems, equipment, protocols, or workflow items that are not supported by the source document.

Example:

The knowledge base knows AHU, RTU, VAV, BACnet, Modbus, PLC, and SCADA exist.

But if the source document only mentions RTU, BACnet/IP, and BAS, the output must show:

- RTU: high confidence
- BACnet/IP: high confidence
- BAS: high confidence
- AHU: 0.00 confidence
- PLC: 0.00 confidence
- Modbus: 0.00 confidence

Do not generate AHU templates just because AHU exists in the knowledge base.

Every detected term, equipment type, protocol, task, RFI, point, or template trigger must include a confidence score from 0.00 to 1.00.

Confidence scale:

- 1.00 = explicit, repeated, and contextually confirmed
- 0.90 = explicit and strongly supported
- 0.75 = explicit but limited context
- 0.60 = inferred from nearby context
- 0.40 = weak inference
- 0.20 = possible but poorly supported
- 0.00 = not found or not supported

Default threshold rules:

- Equipment template trigger: >= 0.70
- Points-list generation: >= 0.70
- RFI candidate: >= 0.60
- Field verification item: >= 0.50
- CAD task: >= 0.60
- Submittal item: >= 0.60
- Commissioning item: >= 0.65
- Ignore below: 0.40 unless producing a raw detection matrix

Confidence weighting model:

Entity Confidence Score =
Exact Term Match:              0.35
Alias / Synonym Match:          0.20
Nearby Technical Context:       0.20
Source Frequency / Repetition:  0.10
Document Section Relevance:     0.10
Cross-reference Support:        0.05

Total possible score: 1.00

Filtering requirements:

- Knowledge-base-only terms must not trigger outputs.
- Unsupported terms must score 0.00.
- Low-confidence terms must be separated from workflow output.
- All inferred items must be labeled inferred.
- Every generated workflow item must include evidence and confidence.
- Do not assume every HVAC document contains AHUs, RTUs, VAVs, chillers, boilers, or PLCs.
- Do not assume every controller is a PLC.
- Do not assume every network mention means BACnet/IP.
- Do not assume every serial mention means Modbus.

Keep the project simple and hackathon-realistic.

Use:

- Python
- Streamlit for MVP UI
- firecrawl/pdf-inspector for PDF inspection and Markdown extraction
- Markdown as the primary output
- JSON as secondary structured output
- CSV export if time allows
- Local folders for storage
- No database unless absolutely needed
- Clean repo structure
- Small working demo over complex architecture

First, generate the complete repo structure and explain each folder.
Then generate the initial README.
Then generate the knowledge base file design.
Then generate the prompts.
Then generate starter code.
Then generate the 3-day hackathon plan.

Do not overbuild.
Prioritize a working demo.
```

---

# Prompt 1 — Repo Structure

```text
Generate the initial repo scaffold for SpecFlow AI.

Repo name:

Document-to-Workflow-AI-Orchestrator

Tool name:

SpecFlow AI

Create a clean folder structure for a Python + Streamlit hackathon MVP.

Required folders:

app/
  main.py
  config.py

app/parsers/
  pdf_inspector_parser.py
  text_parser.py

app/normalizers/
  markdown_normalizer.py
  term_normalizer.py
  section_parser.py

app/scoring/
  confidence_scorer.py
  detection_matrix.py
  filter_engine.py

app/extractors/
  workflow_extractor.py
  equipment_extractor.py
  points_extractor.py
  rfi_extractor.py
  cad_task_extractor.py
  commissioning_extractor.py

app/templates/
  template_router.py
  rtu_template.py
  ahu_template.py
  vav_template.py
  generic_controls_template.py
  bacnet_template.py
  modbus_template.py
  plc_template.py

app/exporters/
  markdown_exporter.py
  json_exporter.py
  csv_exporter.py

app/ui/
  streamlit_app.py

knowledge_base/
  bms_ics_plc_terms.md
  template_rules.json
  confidence_rules.json
  filtering_rules.json

prompts/
  normalize_document.md
  enrich_with_terms.md
  score_detected_terms.md
  filter_detected_items.md
  extract_workflow.md
  generate_templates.md

samples/
  sample_spec.pdf
  sample_cut_sheet.pdf
  sample_raw_markdown.md
  sample_detection_matrix.json

outputs/
  markdown/
    raw/
    normalized/
    agent_ready/
  json/
  csv/
  reports/

docs/
  architecture.md
  demo_script.md
  team_roles.md
  roadmap.md
  data_flow.md
  scoring_model.md
  filtering_model.md
  pdf_inspector_notes.md

tests/
  test_confidence_scorer.py
  test_term_detection.py
  test_filter_engine.py
  test_markdown_export.py

scripts/
  run_streamlit.ps1
  run_streamlit.sh
  setup_pdf_inspector.md

README.md
requirements.txt
.env.example
.gitignore

For each folder and file, explain:

- Purpose
- Owner role
- Whether it is required for MVP or future expansion

Keep the structure simple enough for a 3-day hackathon team.

Important:

Do not include Firecrawl web crawling files in the MVP repo.
Use pdf_inspector_parser.py for PDF ingestion.
```

---

# Prompt 2 — Knowledge Base File

```text
Generate the first version of:

knowledge_base/bms_ics_plc_terms.md

This Markdown file will be used by AI agents to understand BMS, BAS, HVAC controls, PLC, ICS, SCADA, commissioning, retrofits, and OT cybersecurity terminology.

Each term must use this format:

## Term Name

**Category:**  
**Definition:**  
**Common aliases:**  
**Related terms:**  
**BMS/ICS relevance:**  
**Agent interpretation rules:**  
**Source-confirmed filtering rules:**  
**Confidence triggers:**  
**Template trigger threshold:**  
**Example usage:**  

The confidence triggers must follow this scoring model:

- Exact term match: +0.35
- Alias / synonym match: +0.20
- Nearby technical context: +0.20
- Source frequency / repetition: +0.10
- Document section relevance: +0.10
- Cross-reference support: +0.05

Total maximum confidence: 1.00

Include at least 100 terms across these categories:

1. BMS / BAS
2. HVAC equipment
3. Controllers
4. PLC / ICS
5. SCADA / HMI
6. Communication protocols
7. I/O types
8. Sensors
9. Actuators
10. Electrical/control panel terms
11. Retrofit terms
12. Commissioning terms
13. Documentation terms
14. OT cybersecurity terms
15. Network terms

Required terms include:

- BMS
- BAS
- DDC controller
- PLC
- SCADA
- HMI
- BACnet/IP
- BACnet MS/TP
- Modbus TCP
- Modbus RTU
- OPC UA
- MQTT
- AI
- AO
- BI
- BO
- UI
- UO
- RTU
- AHU
- VAV
- FCU
- exhaust fan
- pump
- chiller
- boiler
- VFD
- damper
- valve
- relay
- transformer
- sensor
- actuator
- thermostat
- space temperature sensor
- supply air temperature
- return air temperature
- mixed air temperature
- duct static pressure
- sequence of operation
- points list
- trend log
- alarm
- network trunk
- controller replacement
- retrofit
- commissioning
- functional test
- field verification
- RFI
- submittal
- as-built
- OT network
- Purdue Model
- segmentation
- VLAN
- firewall
- remote access
- service account
- least privilege

Important rules:

The knowledge base defines possible terms, but the agent must only mark terms as detected when the source document supports them.

If a term is not present or supported by the source, it must receive confidence 0.00.

If a term exists only in the knowledge base, it must not trigger templates, points lists, RFIs, CAD tasks, submittal items, or commissioning items.
```

---

# Prompt 3 — Confidence Rules JSON

```text
Generate:

knowledge_base/confidence_rules.json

This JSON file should define the confidence scoring model for detected terms, equipment, protocols, points, tasks, RFIs, and template triggers.

Include:

1. Score components
2. Score meanings
3. Thresholds
4. Template trigger rules
5. Status labels
6. Filtering rules
7. Example scoring cases

Use this model:

score_components:

- exact_term_match: 0.35
- alias_synonym_match: 0.20
- nearby_technical_context: 0.20
- source_frequency_repetition: 0.10
- document_section_relevance: 0.10
- cross_reference_support: 0.05

thresholds:

- confirmed: >= 0.90
- high_confidence: >= 0.75
- medium_confidence: >= 0.60
- low_confidence: >= 0.40
- weak: >= 0.20
- not_detected: 0.00

template_thresholds:

- equipment_template: 0.70
- points_list: 0.70
- rfi_candidate: 0.60
- field_verification: 0.50
- cad_task: 0.60
- submittal_item: 0.60
- commissioning_item: 0.65
- ignore_below: 0.40

Include example:

Input text:
"RTU-1 shall be provided with BACnet/IP communication to the BAS."

Expected scores:

- RTU: 0.95
- BACnet/IP: 0.90
- BAS: 0.90
- AHU: 0.00
- Modbus: 0.00
- PLC: 0.00

Rules:

- Confidence can never be above 0.00 without source evidence.
- Knowledge base presence alone contributes 0.00.
- Evidence is required for any nonzero score.
- Inferred scores must be clearly marked.
- Cross-reference support can boost but cannot create a detection by itself.

Return valid JSON only.
```

---

# Prompt 4 — Filtering Rules JSON

```text
Generate:

knowledge_base/filtering_rules.json

This JSON file defines how SpecFlow AI filters known vocabulary, detected vocabulary, low-confidence detections, and generated workflow items.

Include:

1. detection_modes
2. source_confirmation_rules
3. suppression_rules
4. workflow_thresholds
5. output_visibility_rules
6. unsupported_term_handling
7. inferred_item_handling
8. pdf_quality_handling
9. examples

Required detection modes:

- raw_detection_matrix
- workflow_output
- template_generation

Rules:

raw_detection_matrix:
- May show all knowledge base terms.
- Terms not found in the source must show confidence 0.00.
- Terms with 0.00 must show Source Confirmed = false.
- Terms with 0.00 must show Template Triggered = false.

workflow_output:
- Show only source-supported items above threshold.
- Put weak or low-confidence items into Low-Confidence Items.
- Do not include not-detected terms unless explicitly requested.

template_generation:
- Required terms must exceed minimum confidence.
- Optional boost terms may increase confidence only if source-supported.
- Suppress templates when required terms are absent.
- Never generate templates from knowledge-base-only vocabulary.

Suppression examples:

- AHU exists in KB but not in source: suppress AHU template.
- PLC exists in KB but source only says DDC controller: suppress PLC integration review.
- Modbus exists in KB but source only says serial: suppress Modbus review.
- BACnet/IP exists in KB but source only says network: suppress BACnet/IP review.
- Points list exists in KB but source has no points, I/O, signals, sensors, commands, statuses, or alarms: suppress points-list generation.

PDF quality handling:

- If PDF Inspector reports text-based PDF: allow normal extraction.
- If mixed PDF: allow extraction but mark potentially incomplete.
- If scanned/image-only PDF: mark OCR required and suppress workflow extraction.
- If extracted Markdown is empty: stop and return parse failure message.

Return valid JSON only.
```

---

# Prompt 5 — Template Rules JSON

```text
Generate:

knowledge_base/template_rules.json

This file defines when workflow templates should trigger based on confidence scores.

Templates needed for MVP:

1. rtu_controls_review
2. ahu_controls_review
3. vav_controls_review
4. generic_bms_controls_review
5. bacnet_network_review
6. modbus_network_review
7. plc_integration_review
8. field_verification_review
9. submittal_review
10. commissioning_review

Each template rule must include:

- template_name
- description
- required_terms
- optional_boost_terms
- minimum_confidence
- output_sections
- generated_items
- suppress_if_terms_absent
- human_review_required

Example:

{
  "template_name": "rtu_controls_review",
  "required_terms": ["RTU"],
  "minimum_confidence": 0.70,
  "optional_boost_terms": ["BACnet/IP", "economizer", "supply fan", "heating stage", "cooling stage"],
  "output_sections": [
    "RTU Points List Candidates",
    "RTU Field Verification Items",
    "RTU RFIs",
    "RTU CAD Tasks",
    "RTU Submittal Items",
    "RTU Commissioning Checklist"
  ],
  "suppress_if_terms_absent": true,
  "human_review_required": false
}

Important:

Do not trigger a template only because a term exists in the knowledge base.

Only trigger templates from source-confirmed terms above threshold.

Optional boost terms may improve a triggered template, but optional boost terms cannot replace required terms.

Return valid JSON only.
```

---

# Prompt 6 — Markdown Output Standard

```text
Generate the Markdown output standard for SpecFlow AI.

The system must convert every ingested document into clean AI-agent-ready Markdown.

Each output Markdown file must include YAML frontmatter:

---
title:
source_type:
source_url:
source_file:
ingested_at:
processed_by:
ingestion_engine: pdf-inspector
document_domain:
document_type:
pdf_classification:
ocr_required:
confidence:
tags:
related_terms:
template_triggers:
filtering_mode:
---

Then include these body sections:

# Document Summary

# Source Metadata

# PDF Inspection Results

# Detection Matrix

# Normalized Technical Terms

# Extracted Equipment

# Extracted Controls Requirements

# Extracted Network Requirements

# Potential Points List

# RFIs / Clarifications

# Risks / Gaps

# Field Verification Items

# CAD / Drawing Tasks

# Submittal Items

# Commissioning / Checkout Items

# Template Triggers

# Low-Confidence Items

# Excluded / Not Detected Terms

# Agent Notes

The Detection Matrix must use this format:

| Term | Normalized Term | Category | Confidence | Status | Evidence | Source Confirmed | Template Triggered |
|---|---|---|---:|---|---|---|---|

Status values:

- Confirmed
- High Confidence
- Medium Confidence
- Low Confidence
- Weak
- Not Detected

Rules:

- Main workflow sections only include items above threshold.
- Low-confidence items go in the Low-Confidence section.
- Not-detected terms may appear only in the detection matrix if raw detection matrix mode is requested.
- Inferred items must be marked as inferred.
- Source excerpts must be short and tied to the evidence.
- Do not hallucinate.
- Do not invent equipment, points, protocols, or tasks.
- Do not generate workflow items from KB-only vocabulary.
- Do not trigger templates below threshold.
```

---

# Prompt 7 — Normalize Document Prompt

```text
Generate the file:

prompts/normalize_document.md

This prompt will take raw Markdown from PDF Inspector or a text parser and convert it into clean AI-agent-ready Markdown.

The prompt must instruct the AI to:

1. Preserve the original meaning.
2. Remove repeated headers, repeated footers, page artifacts, and unrelated boilerplate.
3. Preserve useful tables.
4. Preserve section headings.
5. Preserve equipment tags.
6. Preserve point names.
7. Preserve protocol names.
8. Preserve units.
9. Preserve source references when available.
10. Normalize BMS/ICS/PLC terminology using the knowledge base.
11. Distinguish known vocabulary from source-confirmed vocabulary.
12. Add a detection matrix with confidence scores.
13. Add YAML frontmatter.
14. Mark inferred items clearly.
15. Never invent requirements.
16. Never invent equipment.
17. Never invent points.
18. Never invent protocols.
19. Never trigger templates below threshold.
20. Produce Markdown suitable for chunking, RAG, and AI agents.

The output must follow the Markdown output standard.

Include explicit instructions for confidence scoring:

- exact term match
- alias match
- nearby context
- frequency
- section relevance
- cross-reference support

Filtering instructions:

- If a term exists in the knowledge base but is not supported by the source, score it 0.00.
- If a detected item has weak evidence, place it in Low-Confidence Items.
- If a generated workflow item does not meet threshold, suppress it.
- If a PDF appears incomplete or OCR is required, mark output as incomplete and avoid workflow generation.

Output only the finished prompt content.
```

---

# Prompt 8 — Score Detected Terms Prompt

```text
Generate the file:

prompts/score_detected_terms.md

This prompt will take normalized Markdown and the BMS/ICS/PLC knowledge base, then produce a confidence-scored detection matrix.

The prompt must:

1. Identify source-confirmed terms.
2. Score each term from 0.00 to 1.00.
3. Use the defined weighted scoring model.
4. Return evidence for each score.
5. Return source references when available.
6. Mark terms not found as 0.00 only when a full detection matrix is requested.
7. Avoid creating workflow items.
8. Focus only on detection and scoring.

Required output:

Markdown table:

| Term | Normalized Term | Category | Confidence | Status | Evidence | Source Reference | Source Confirmed |
|---|---|---|---:|---|---|---|---|

And JSON:

{
  "detected_terms": [
    {
      "term": "",
      "normalized_term": "",
      "category": "",
      "confidence": 0.0,
      "status": "",
      "evidence": [],
      "source_references": [],
      "source_confirmed": false,
      "inferred": false
    }
  ]
}

Rules:

- The knowledge base helps classify terms.
- The source document determines whether the term is detected.
- If the source does not support a term, confidence must be 0.00.
- Do not confuse RTU with AHU unless the source supports both.
- Do not confuse PLC with DDC controller unless the source supports both.
- Do not assume BACnet when only “network” is mentioned.
- Do not assume Modbus when only “serial” is mentioned.
- Do not assume points unless the source mentions points, signals, I/O, sensors, commands, statuses, or alarms.
- Do not assign nonzero confidence without source evidence.
```

---

# Prompt 9 — Filter Detected Items Prompt

```text
Generate the file:

prompts/filter_detected_items.md

This prompt takes a confidence-scored detection matrix and applies SpecFlow AI filtering rules before workflow extraction.

Inputs:

1. Normalized Markdown
2. Detection matrix
3. confidence_rules.json
4. filtering_rules.json
5. template_rules.json

The prompt must produce:

1. Allowed workflow items
2. Suppressed items
3. Low-confidence items
4. Not-detected terms
5. Template trigger decisions
6. Human review flags

Required Markdown output:

# Filtering Summary

| Item | Category | Confidence | Filter Result | Reason | Evidence |
|---|---|---:|---|---|---|

# Allowed Items

# Suppressed Items

# Low-Confidence Items

# Not Detected Terms

# Template Trigger Decisions

Required JSON output:

{
  "allowed_items": [],
  "suppressed_items": [],
  "low_confidence_items": [],
  "not_detected_terms": [],
  "template_decisions": []
}

Rules:

- Items below the relevant threshold are suppressed from workflow output.
- Suppressed does not mean deleted; suppressed items should remain auditable.
- Not-detected terms must not appear in workflow output.
- Low-confidence items may appear only in a low-confidence section.
- Human review is required for medium-confidence inferred items.
- Templates require source-confirmed required terms.
```

---

# Prompt 10 — Workflow Extraction Prompt

```text
Generate the file:

prompts/extract_workflow.md

This prompt takes normalized Markdown plus a filtered confidence-scored detection matrix and extracts actionable engineering workflow items.

The output is optimized for BMS retrofit projects.

Required workflow categories:

- project_summary
- scope_items
- equipment
- control_requirements
- network_requirements
- points_list_candidates
- rfi_candidates
- risks_and_gaps
- field_verification_items
- cad_tasks
- submittal_items
- commissioning_items
- source_references
- confidence_scores

Rules:

1. Only generate workflow items from source-supported evidence.
2. Use confidence thresholds.
3. Do not generate equipment templates below 0.70 confidence.
4. Do not generate points-list candidates below 0.70 confidence.
5. RFIs require at least 0.60 confidence unless clearly marked low confidence.
6. Field verification items require at least 0.50 confidence.
7. CAD tasks require at least 0.60 confidence.
8. Submittal items require at least 0.60 confidence.
9. Commissioning items require at least 0.65 confidence.
10. Mark inferred items clearly.
11. Include evidence and source references.
12. Separate confirmed items from low-confidence items.
13. Do not hallucinate missing systems.
14. Do not assume every HVAC document contains AHUs, RTUs, VAVs, chillers, boilers, or PLCs.
15. Do not assume every network mention means BACnet/IP.
16. Do not assume every controller is a PLC.
17. Do not use suppressed items for workflow generation.

Required output:

1. Human-readable Markdown report
2. JSON-compatible structured output

For every item include:

- item_name
- category
- description
- confidence
- status
- evidence
- source_reference
- inferred
- recommended_action
- template_triggered
```

---

# Prompt 11 — Template Generation Prompt

```text
Generate the file:

prompts/generate_templates.md

This prompt uses detected terms, confidence scores, filtering decisions, and template rules to decide which workflow templates should be generated.

The prompt must:

1. Read the detection matrix.
2. Read filtering decisions.
3. Read template_rules.json.
4. Trigger templates only when required terms exceed threshold.
5. Use optional boost terms to improve confidence, but never replace required terms.
6. Suppress templates when required terms are absent.
7. Mark all generated templates with confidence.
8. Require human review for medium-confidence templates.
9. Avoid generating templates from knowledge-base-only vocabulary.

Required output:

# Template Trigger Summary

| Template | Triggered | Confidence | Reason | Human Review Required |
|---|---|---:|---|---|

# Generated Template Sections

For each triggered template, produce relevant sections.

Examples:

RTU template sections:

- RTU Points List Candidates
- RTU Field Verification Items
- RTU RFIs
- RTU CAD Tasks
- RTU Submittal Items
- RTU Commissioning Checklist

AHU template sections:

- AHU Points List Candidates
- AHU Field Verification Items
- AHU RFIs
- AHU CAD Tasks
- AHU Submittal Items
- AHU Commissioning Checklist

Important:

If RTU confidence is 0.95 and AHU confidence is 0.00, generate RTU templates only.

If AHU confidence is 0.95 and RTU confidence is 0.00, generate AHU templates only.

If both are below 0.70, generate only generic controls review if there is source-confirmed BAS/BMS/control scope.

If there is no source-confirmed controls scope, do not generate templates.
```

---

# Prompt 12 — PDF Inspector Parser Design

```text
Design the PDF Inspector ingestion module for SpecFlow AI.

File:

app/parsers/pdf_inspector_parser.py

Purpose:

Use firecrawl/pdf-inspector to inspect uploaded PDFs, classify the PDF type, extract Markdown when possible, and return source metadata for downstream SpecFlow processing.

Do not use Firecrawl web crawling/API.

Requirements:

- Accept a PDF file path
- Call pdf_inspector through a wrapper function
- Classify PDF quality/type where supported
- Return raw Markdown
- Return metadata
- Detect whether OCR is likely required
- Handle errors cleanly
- Save raw Markdown to outputs/markdown/raw/
- Keep parser replaceable
- Do not hallucinate from empty extraction

Functions needed:

- inspect_pdf(file_path: str) -> dict
- parse_pdf_to_markdown(file_path: str) -> dict
- save_raw_markdown(markdown: str, filename: str) -> str
- build_pdf_metadata(file_path: str, result: dict) -> dict
- requires_ocr(result: dict) -> bool

Return structure:

{
  "source_type": "pdf",
  "source_file": "",
  "ingestion_engine": "pdf-inspector",
  "pdf_classification": "",
  "raw_markdown": "",
  "metadata": {},
  "ocr_required": false,
  "status": "success",
  "errors": []
}

Filtering behavior:

- If raw_markdown is empty, set status to failed or ocr_required.
- If OCR is required, suppress workflow extraction.
- If PDF is mixed, mark extraction as potentially incomplete.

Generate starter Python code with comments.
Keep it hackathon simple.
```

---

# Prompt 13 — Streamlit UI Prompt

```text
Design the Streamlit MVP UI for SpecFlow AI.

File:

app/ui/streamlit_app.py

The UI should allow the user to:

1. Upload a PDF
2. Paste raw text or Markdown as fallback
3. Choose processing mode:
   - Raw Markdown only
   - Normalize Markdown
   - Detect terms
   - Apply filtering
   - Extract workflow
   - Generate templates
4. Display PDF Inspector results
5. Display raw Markdown
6. Display normalized Markdown
7. Display detection matrix
8. Display filtering summary
9. Display extracted workflow sections
10. Export Markdown
11. Export JSON
12. Export CSV if time allows

UI tabs:

- Upload / Ingest
- PDF Inspection
- Raw Markdown
- Detection Matrix
- Filtering Summary
- Workflow Output
- Template Output
- Exports
- About

Keep the UI simple and demo-friendly.

Do not require a database.

Do not require Firecrawl API keys.

Generate starter Streamlit code with placeholder function calls where needed.
```

---

# Prompt 14 — Hackathon Build Plan

```text
Create a 3-day hackathon build plan for SpecFlow AI.

Constraints:

- Team of 3–4 people
- 4 hours per day hackathon work
- Final demo on Friday
- Need working MVP
- Some team members may not have local admin rights
- Use GitHub browser editing if needed
- One teammate may run the local demo
- PDF Inspector may require local setup on the demo machine

Deliverables by day:

Day 1:
- Repo scaffold
- README
- Knowledge base starter
- PDF Inspector parser design
- PDF parser working or stubbed
- Streamlit shell
- Text-paste fallback mode

Day 2:
- Normalization prompt
- Confidence scoring
- Detection matrix
- Filtering engine
- JSON output
- Markdown output

Day 3:
- Workflow extraction
- Template routing
- CSV exports if time allows
- Sample documents
- Demo script
- Final cleanup
- Presentation talking points

Include:

- Team roles
- Branch naming
- Issue names
- MVP acceptance criteria
- Demo script
- Stretch goals
- What not to build

Important:

Prioritize:

PDF upload or text-paste input
→ Markdown display
→ detection matrix
→ filtering summary
→ agent-ready Markdown
→ JSON download

Do not overbuild.
```

---

# Prompt 15 — README Generation Prompt

```text
Generate the initial README.md for SpecFlow AI.

The README must include:

- Project name
- One-line description
- Problem statement
- MVP scope
- Core workflow
- Source-confirmed filtering rule
- Confidence scoring model
- PDF Inspector ingestion note
- Repo structure
- Local setup
- Streamlit run command
- Demo flow
- Example input
- Example output
- What not to build in MVP
- Roadmap

Critical project rules:

- Use firecrawl/pdf-inspector for PDF ingestion.
- Do not use Firecrawl web crawling/API in the MVP.
- Knowledge-base-only terms must not trigger workflows.
- Every output item must have confidence and evidence.
- Suppressed items should be auditable.
- Keep the system local-first and hackathon-simple.
```

---

# Demo Script

```text
1. Open the Streamlit webpage.

2. Explain:
   "SpecFlow AI converts messy controls and OT documents into clean AI-agent-ready Markdown."

3. Upload a sample controls PDF or paste sample text.

4. Show PDF Inspector results:
   - PDF classification
   - Markdown extracted
   - OCR required or not

5. Show raw Markdown.

6. Show detection matrix.

7. Explain:
   "The knowledge base knows many terms, but the source document controls what is actually detected."

8. Show unsupported terms:
   - AHU: 0.00 if not in source
   - PLC: 0.00 if not in source
   - Modbus: 0.00 if not in source

9. Show filtering summary.

10. Show agent-ready Markdown.

11. Show JSON export.

12. Close with:
   "This is not just document conversion. It is source-confirmed workflow generation for engineering agents."
```

---

# Sample Source Text for Demo

```text
RTU-1 shall be provided with BACnet/IP communication to the BAS.
The contractor shall provide all required points for fan status, fan command,
cooling command, heating command, discharge air temperature, and occupied mode.
The BAS contractor shall perform field verification of controller location,
network connectivity, and point-to-point checkout prior to commissioning.
```

Expected behavior:

```text
RTU: high confidence
BACnet/IP: high confidence
BAS: high confidence
field verification: medium/high confidence
commissioning: medium/high confidence
points list: high confidence
AHU: 0.00
PLC: 0.00
Modbus: 0.00
```

---

# Project Guardrails

Do build:

```text
Streamlit local web app
PDF upload
PDF Inspector integration
Text-paste fallback
Markdown cleanup
Knowledge base term matching
Confidence scoring
Filtering summary
Agent-ready Markdown export
JSON export
Small demo workflow
```

Do not build yet:

```text
Database
Authentication
Cloud storage
Vector DB
Multi-agent orchestration
Production OCR pipeline
Full CAD automation
URL crawling
Enterprise permissions
Complex project dashboard
```

---

# Final Focus Sentence

```text
SpecFlow AI proves that engineering documents can be converted into AI-agent-ready workflow packages without hallucinating unsupported equipment, points, protocols, or scope.
```
