# SpecFlow AI — Project Prompt Pack v3

> Living build document. Strikethrough = completed. Open items = still needed.
> Deployment target: Linux container on Michael (NVDS LXC), accessible via Tailscale.

---

# Project Anchor

```text
SpecFlow AI converts messy engineering documents into clean AI-agent-ready Markdown,
then uses a BMS/ICS/PLC knowledge base and source-confirmed confidence scoring to generate
RFIs, tasks, points-list candidates, CAD actions, field verification items, and commissioning
checklists.
```

Core rule:
```text
Known vocabulary is not the same as detected vocabulary.
The source document must support every output item.
```

PDF ingestion decision:
```text
Use firecrawl/pdf-inspector (npm: @firecrawl/pdf-inspector) for PDF classification
and Markdown extraction. Runs natively on Linux x64 — no Rust build required.
Do NOT use pymupdf4llm or pdfplumber.
```

---

# Build Status

| Area | Status | Notes |
|---|---|---|
| Repo scaffold | ✅ Done | Flattened — no more double-nested folder |
| Knowledge base (BMS) | ✅ Done | Table-driven MD, 50+ BMS terms |
| Knowledge base (PLC/ICS/sensors) | ✅ Done | Added plc_hardware, industrial_sensor, panel_component |
| Knowledge base (manufacturers) | ✅ Done | 60 manufacturers — Rockwell, Siemens, ABB, Mitsubishi, etc. |
| Knowledge base (skip_terms) | ✅ Done | estimate, takeoff, invoice, PO suppress output |
| confidence_rules.json | ✅ Done | Weighted scoring model |
| filtering_rules.json | ✅ Done | Suppression, PDF quality handling |
| template_rules.json | ✅ Done | 10 templates (RTU, AHU, VAV, BACnet, Modbus, PLC, etc.) |
| app/scoring/ | ✅ Done | confidence_scorer, detection_matrix, filter_engine |
| app/normalizers/ | ✅ Done | markdown_normalizer, term_normalizer (parses MD tables) |
| app/exporters/ | ✅ Done | markdown, json, csv exporters |
| Streamlit UI (8 tabs) | ✅ Done | Upload → score → filter → templates → exports |
| prompts/ (5 prompts) | ✅ Done | normalize, score, filter, extract, generate_templates |
| .env.example / .gitignore | ✅ Done | |
| run scripts (PS1 + SH) | ✅ Done | |
| **PDF parser — firecrawl** | ❌ NOT DONE | Still using pymupdf4llm — needs firecrawl/pdf-inspector |
| Word (.docx) parser | ❌ NOT DONE | Needs mammoth or python-docx |
| Excel (.xlsx) parser | ❌ NOT DONE | Needs openpyxl or xlsx |
| Docker container | ❌ NOT DONE | Needs Dockerfile + docker-compose.yml |
| Tailscale access | ❌ NOT DONE | Container on Michael → Tailscale IP |
| Tests | ❌ NOT DONE | test_confidence_scorer, test_filter_engine, etc. |
| Sample documents | ❌ NOT DONE | Sample PDF, sample text for demo |

---

# Source-Confirmed Filtering Standard

> Unchanged from v2. Rules are live in confidence_rules.json and filtering_rules.json.

SpecFlow AI must apply strict filtering between the knowledge base and the source document.

The knowledge base defines possible terms. The source document determines whether a term is detected.

If the source document does not support a term, that term receives confidence `0.00` and must not trigger downstream workflow generation.

## Filtering Layers (all implemented)

~~**1. Ingestion Quality Filter** — text_pdf / mixed_pdf / scanned_pdf / image_heavy_pdf / empty_or_failed_parse~~

~~**2. Evidence Filter** — each detection must have a source excerpt, match_type, section~~

~~**3. Confidence Filter** — 0.00 to 1.00 using weighted scoring model~~

~~**4. Workflow Gate Filter** — thresholds per output type~~

~~**5. Suppression Filter** — KB-only terms, generic words, unsupported assumptions~~

~~**6. Output Mode Filter** — raw_detection_matrix vs workflow_output~~

---

# ~~Prompt 0 — Master Project Kickoff~~ ✅ DONE

~~Act as a senior AI systems architect...~~ *(scaffold, KB, scoring, UI, prompts all built — see Build Status above)*

---

# ~~Prompt 1 — Repo Structure~~ ✅ DONE

~~Generate the initial repo scaffold...~~

**What was built:**
```
app/
  __init__.py
  main.py
  exporters/   csv_exporter.py, json_exporter.py, markdown_exporter.py
  extractors/  workflow_extractor.py
  normalizers/ markdown_normalizer.py, term_normalizer.py
  parsers/     pdf_inspector_parser.py (pymupdf4llm — needs replacing), pdf_parser.py, web_parser.py
  scoring/     confidence_scorer.py, detection_matrix.py, filter_engine.py
  templates/   (NOT YET BUILT)
  ui/          streamlit_app.py

knowledge_base/
  bms_ics_plc_terms.md    ← TABLE-DRIVEN, 14 categories, 270+ terms
  confidence_rules.json
  filtering_rules.json
  template_rules.json

prompts/
  extract_workflow.md
  filter_detected_items.md
  generate_templates.md
  normalize_document.md
  score_detected_terms.md

docs/   architecture.md, demo_script.md, roadmap.md, team_roles.md
scripts/ run_streamlit.ps1, run_streamlit.sh
outputs/ markdown/raw, markdown/normalized, markdown/agent_ready, json, csv, reports
samples/ (empty — needs sample PDF and text)
tests/   (empty — needs test files)
.env.example
.gitignore
requirements.txt
README.md
```

---

# ~~Prompt 2 — Knowledge Base File~~ ✅ DONE (upgraded)

~~Generate knowledge_base/bms_ics_plc_terms.md...~~

**What was actually built** — table-driven format (same structure as NVDS vocabulary):

```markdown
## term_type
| Term | Weight | Scope | Variants | Notes |
```

**14 categories:**

| Category | Terms | What it covers |
|---|---:|---|
| equipment_type | 28 | AHU, RTU, VAV, FCU, VRF, DOAS, CRAC, ERV, damper, valve, actuator |
| plc_hardware | 22 | PLC, CPU module, I/O modules, racks, safety PLC, DCS, PAC, HMI panel |
| industrial_sensor | 30 | Pressure, flow, level, CO2, humidity, DP, RTD, thermocouple, freeze stat |
| panel_component | 18 | Breakers, contactors, relays, transformers, UPS, enclosures, E-stops |
| protocol | 16 | BACnet, MS/TP, Modbus, EtherNet/IP, PROFINET, PROFIBUS, OPC UA, DNP3 |
| platform | 20 | BAS, Niagara, Metasys, Studio 5000, TIA Portal, Ignition, Wonderware |
| controller_model | 20 | ECY series, JACE, ControlLogix, CompactLogix, S7-1200, S7-1500, BCM |
| manufacturer | 60 | Rockwell, Siemens, JCI, ABB, Mitsubishi, Omron, Emerson, Beckhoff |
| io_type | 6 | AI, AO, DI, DO, UI, UO |
| signal_type | 10 | 0-10V, 4-20mA, 10K Type II, NI1000, PT1000, Digital, Network |
| eng_unit | 9 | CFM, GPM, Tons, inWC, kW, psi, °F, %, kWh |
| doc_signal | 11 | point list, sequence, submittal, commissioning, setpoint, PID |
| point_name | 30 | DaTmp, SFCmd, SFSts, ZnTmp, DSP, OadPos, HVSig, CVSig |
| skip_term | 8 | estimate, takeoff, invoice, PO, warranty — suppress from output |

**To add a term:** open `knowledge_base/bms_ics_plc_terms.md`, add a row to the right section.
The parser in `app/normalizers/term_normalizer.py` loads it automatically at runtime.

---

# ~~Prompt 3 — Confidence Rules JSON~~ ✅ DONE

~~Generate knowledge_base/confidence_rules.json...~~

Live at `knowledge_base/confidence_rules.json`. Scoring model:

| Component | Weight |
|---|---:|
| Exact term match | 0.35 |
| Alias / synonym match | 0.20 |
| Nearby technical context | 0.20 |
| Source frequency / repetition | 0.10 |
| Document section relevance | 0.10 |
| Cross-reference support | 0.05 |

---

# ~~Prompt 4 — Filtering Rules JSON~~ ✅ DONE

~~Generate knowledge_base/filtering_rules.json...~~

Live at `knowledge_base/filtering_rules.json`.

---

# ~~Prompt 5 — Template Rules JSON~~ ✅ DONE

~~Generate knowledge_base/template_rules.json...~~

Live at `knowledge_base/template_rules.json`. 10 templates: rtu_controls_review, ahu_controls_review, vav_controls_review, generic_bms_controls_review, bacnet_network_review, modbus_network_review, plc_integration_review, field_verification_review, submittal_review, commissioning_review.

---

# ~~Prompt 6 — Markdown Output Standard~~ ✅ DONE

~~Generate the Markdown output standard...~~

YAML frontmatter + 19 body sections implemented in `app/normalizers/markdown_normalizer.py`.

---

# ~~Prompts 7–11 — Processing Prompts~~ ✅ DONE

All five prompts written and live in `prompts/`:
- ~~normalize_document.md~~
- ~~score_detected_terms.md~~
- ~~filter_detected_items.md~~
- ~~extract_workflow.md~~
- ~~generate_templates.md~~

---

# Prompt 12 — PDF Inspector Parser ❌ NEEDS REWORK

> **Current state:** `app/parsers/pdf_inspector_parser.py` uses `pymupdf4llm` — WRONG.
> Must be replaced with `@firecrawl/pdf-inspector` (Node.js) or firecrawl Python bindings.
> Firecrawl is the spec. pymupdf4llm is a placeholder only.

```text
Replace app/parsers/pdf_inspector_parser.py.

Use @firecrawl/pdf-inspector (npm package) for PDF classification and Markdown extraction.

The npm package supports Linux x64 natively — no Rust build needed.
This runs inside the Docker container on Michael.

Required functions:
- classifyPdf(filePath) → { type: TextBased | Scanned | Mixed | ImageBased }
- extractTextInRegions(filePath) → markdown string
- If classifyPdf returns Scanned → set ocr_required: true, suppress workflow extraction
- If classifyPdf returns Mixed → mark extraction as potentially incomplete
- If extracted text is empty → set status: failed, return parse failure

NOTE: The app/ui/streamlit_app.py is Python/Streamlit. Two options:
  Option A: Call pdf-inspector as a subprocess from Python (shell out to Node.js)
  Option B: Switch UI to Node.js/Express — cleanest integration

Decide before implementing.
```

---

# Prompt 12B — Word and Excel Parsers ❌ NOT BUILT

```text
Add parsers for Word and Excel files alongside the PDF parser.

Word (.docx):
  Use python-docx or mammoth (Python)
  File: app/parsers/docx_parser.py
  Function: parse_docx_to_markdown(file_path: str) -> dict
  Return same structure as inspect_pdf():
    { source_type, source_file, raw_markdown, metadata, status, errors }

Excel (.xlsx / .csv):
  Use openpyxl + pandas (Python)
  File: app/parsers/excel_parser.py
  Function: parse_excel_to_markdown(file_path: str) -> dict
  Convert each sheet to a Markdown table
  Flag sheets that look like points lists, equipment schedules, or IO schedules
  Return same structure as inspect_pdf()

Update Streamlit UI:
  app/ui/streamlit_app.py — add .docx and .xlsx to file_uploader accepted types
  Route uploaded file to correct parser based on extension
  Show parser results in PDF Inspection tab (rename to "Document Inspection")

Update requirements.txt:
  Add: python-docx, mammoth, openpyxl
```

---

# ~~Prompt 13 — Streamlit UI~~ ✅ DONE (wired to real pipeline)

~~Design the Streamlit MVP UI...~~

**What was built** — `app/ui/streamlit_app.py`, 8 tabs:

| Tab | Status | What it does |
|---|---|---|
| Upload / Ingest | ✅ Live | PDF upload or text paste, mode selector, runs pipeline |
| PDF Inspection | ✅ Live | Shows classification, status, OCR flag, file metadata |
| Raw Markdown | ✅ Live | Shows normalized source text |
| Detection Matrix | ✅ Live | Scored term table, confirmed vs not-detected counts |
| Filtering Summary | ✅ Live | Allowed / low-conf / suppressed / not-detected buckets |
| Workflow Output | ✅ Live | Triggered templates + allowed items dataframe |
| Exports | ✅ Live | Download JSON, Markdown, Filtering Summary |
| About | ✅ Live | Project description and threshold table |

**Still needed in UI:**
- Word/Excel file support (add to uploader)
- Rename "PDF Inspection" → "Document Inspection"
- Sample document loader for demo

---

# ~~Prompt 14 — Hackathon Build Plan~~ ✅ SUPERSEDED

~~Create a 3-day hackathon build plan...~~

**Actual remaining build order:**
1. Docker container (see Prompt 15 below)
2. Tailscale access (see Prompt 16 below)
3. Replace PDF parser with firecrawl (Prompt 12)
4. Add Word/Excel parsers (Prompt 12B)
5. Add sample documents to `samples/`
6. Write basic tests in `tests/`
7. Update `docs/demo_script.md` with final flow

---

# ~~Prompt 15 — README~~ ✅ DONE (basic)

~~Generate the initial README.md...~~

Basic README exists. Needs updating once container and parsers are finalized.

---

# Prompt 15 — Docker Container Setup ❌ NOT BUILT

```text
Create Docker container configuration for SpecFlow AI.

Deployment target: Michael LXC (Linux x64) on BAAL-PRXMX Proxmox host.
Access: via Tailscale IP from team browsers.

Files to create:

1. Dockerfile
   Base image: python:3.11-slim
   Install system packages: nodejs, npm (for @firecrawl/pdf-inspector)
   Install Python packages: pip install -r requirements.txt
   Copy app source
   Expose port 8501 (Streamlit default)
   CMD: streamlit run app/ui/streamlit_app.py --server.address=0.0.0.0

2. docker-compose.yml
   Service: specflow-ai
   Build: .
   Ports: 8501:8501
   Volumes:
     - ./outputs:/app/outputs   (persist exports)
     - ./samples:/app/samples   (sample docs)
   Environment:
     - OPENAI_API_KEY (from .env)
   Restart: unless-stopped

3. .dockerignore
   Exclude: __pycache__, .git, outputs/, .env, *.pyc

Deploy steps:
   git clone https://github.com/STBMSEng4/Document-to-Workflow-AI-Orchestrator
   cd Document-to-Workflow-AI-Orchestrator
   cp .env.example .env   (fill in API key)
   docker compose up -d
   docker compose logs -f

Access:
   http://<michael-tailscale-ip>:8501

Notes:
   - Michael is already running Linux (LXC on BAAL-PRXMX)
   - Docker must be installed in the Michael container
   - Port 8501 must be open in the LXC firewall
   - Tailscale must be running on Michael (already configured per infrastructure notes)
```

---

# Prompt 16 — Tailscale Team Access ❌ NOT CONFIGURED

```text
Give team members browser access to SpecFlow AI via Tailscale.

Setup steps:

1. Confirm Tailscale is running on Michael (NVDS LXC):
   ssh root@michael
   tailscale status
   → Should show michael's Tailscale IP (e.g. 100.x.x.x)

2. Share Michael with team via Tailscale admin console:
   https://login.tailscale.com/admin/machines
   → Find Michael → Share with team members' Tailscale accounts
   → Or use Tailscale ACL to grant access to specific users

3. Team member setup (each person):
   - Install Tailscale: https://tailscale.com/download
   - Sign in with Tailscale account
   - Confirm they can see Michael in their Tailscale network
   - Open browser → http://<michael-tailscale-ip>:8501

4. Optional — Tailscale MagicDNS:
   Enable MagicDNS in Tailscale admin
   Team can then use: http://michael:8501 instead of IP address

No ports need to be opened on the firewall.
No VPN client configuration needed beyond Tailscale install.
Works on any OS (Windows enterprise, Mac, Linux).
```

---

# Demo Script (updated)

```text
1. Open browser → http://<michael-tailscale-ip>:8501

2. Explain:
   "SpecFlow AI converts controls and OT documents into source-confirmed
   AI-agent-ready workflow packages. The knowledge base knows 270+ terms
   across BMS, PLC, ICS, sensors, protocols, and manufacturers.
   But only what's in the document gets detected."

3. Upload a sample controls PDF or paste sample text.

4. Show Document Inspection tab:
   - PDF classification (TextBased / Scanned / Mixed)
   - Character count, file metadata

5. Show Detection Matrix tab:
   - Terms found vs. terms not found
   - Demonstrate: RTU = 0.95, AHU = 0.00 if not in source

6. Explain source-confirmed filtering:
   "Rockwell Allen-Bradley is in the KB.
    But if the document only mentions Siemens S7-1200, only Siemens fires.
    No Rockwell outputs. No PLC outputs unless PLC is in the source."

7. Show Filtering Summary tab:
   - Allowed / suppressed / not-detected buckets
   - Template trigger decisions

8. Show Workflow Output tab:
   - Triggered templates only
   - Allowed items table

9. Download JSON export.

10. Close:
    "Source-confirmed workflow generation. Nothing invented.
     Everything traced back to the document."
```

---

# Sample Source Text for Demo

```text
The existing Siemens S7-1200 PLC shall be replaced with a new ControlLogix L83E.
Communication to the SCADA system shall use EtherNet/IP.
The contractor shall provide a complete I/O schedule, sequence of operations,
and functional test procedure prior to commissioning.
Field verification of all analog inputs and digital outputs shall be completed
by the controls contractor before startup.
```

Expected behavior:
```text
Siemens: 0.90          ← manufacturer detected
S7-1200: 0.90          ← controller_model detected
ControlLogix: 0.90     ← controller_model detected
PLC: 0.95              ← plc_hardware detected
SCADA: 0.80            ← platform detected
EtherNet/IP: 0.90      ← protocol detected
I/O schedule: 0.85     ← doc_signal detected
sequence: 0.90         ← doc_signal detected
commissioning: 0.90    ← doc_signal detected
field verification: 0.85 ← doc_signal detected
analog input: 0.85     ← io_type detected
digital output: 0.85   ← io_type detected

BACnet: 0.00           ← not in source
Modbus: 0.00           ← not in source
AHU: 0.00              ← not in source
RTU: 0.00              ← not in source
```

---

# Project Guardrails

Do build:
```text
✅ Streamlit local/containerized web app
✅ PDF upload → firecrawl/pdf-inspector
   Word/Excel upload → docx + openpyxl parsers
✅ Table-driven knowledge base (add row = new term)
✅ Confidence scoring + source-confirmed filtering
✅ Detection matrix (raw and workflow modes)
✅ Template trigger decisions
✅ Agent-ready Markdown export
✅ JSON export
   Docker container on Michael
   Tailscale team access
   Sample documents
```

Do not build yet:
```text
Database
Authentication
Cloud storage
Vector DB / RAG pipeline
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
SpecFlow AI proves that engineering documents can be converted into
AI-agent-ready workflow packages without hallucinating unsupported
equipment, points, protocols, or scope — deployable by any team member
via a browser and a Tailscale connection.
```
