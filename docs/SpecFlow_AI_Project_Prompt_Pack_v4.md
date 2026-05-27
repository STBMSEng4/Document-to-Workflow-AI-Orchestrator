# SpecFlow AI - Project Prompt Pack v4

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current live target: Proxmox LXC `CT 211` (`specflow-ai`), reachable over Tailscale.

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
and Markdown extraction. Runs locally on Linux x64 via Node.js.
Do not use the Firecrawl web crawler/API for the MVP.
```

---

# Build Status

| Area | Status | Notes |
|---|---|---|
| ~~Repo scaffold~~ | Done | Flattened Python app repo in place |
| ~~Knowledge base (BMS / PLC / ICS / manufacturers / skip terms)~~ | Done | Table-driven MD with 270+ terms |
| ~~confidence_rules.json~~ | Done | Weighted scoring model |
| ~~filtering_rules.json~~ | Done | Suppression + threshold gating |
| ~~template_rules.json~~ | Done | 10 template triggers |
| ~~app/scoring/~~ | Done | confidence scorer, detection matrix, filter engine |
| ~~app/normalizers/~~ | Done | markdown and term normalizers |
| ~~app/exporters/~~ | Done | markdown, json, csv exporters |
| ~~Streamlit UI~~ | Done | Upload -> score -> filter -> workflow -> export |
| ~~prompts/ (5 core prompts)~~ | Done | normalize, score, filter, extract, generate |
| ~~Firecrawl PDF parser integration~~ | Done | Python parser now shells out to local `@firecrawl/pdf-inspector` with `pymupdf4llm` fallback |
| ~~Local Node package wiring~~ | Done | `package.json` + `app/parsers/pdf_inspector_node.mjs` added |
| ~~LXC deployment~~ | Done | Live on `CT 211` as `specflow-ai` |
| ~~Tailscale access~~ | Done | Connected machine, browser reachable over tailnet |
| ~~Repo Docker assets~~ | Done | `Dockerfile`, `docker-compose.yml`, `.dockerignore`, deployment guide added |
| Word (.docx) parser | Not done | Needs `docx_parser.py` |
| Excel / CSV structured parser | Not done | Needs `excel_parser.py` / improved csv routing |
| Tests | Not done | No real parser/scoring/filter tests yet |
| Sample demo documents | Not done | `samples/` still needs curated inputs |
| Auto-start service in live CT | Not done | App currently restarted manually / via `nohup` |
| Verified Dockerized runtime from repo | Not done | Docker assets exist, but live deployment is still direct `.venv` execution |
| UI rename to "Document Inspection" | Not done | Still labeled "PDF Inspection" |

---

# What Was Completed Since v3

- ~~Replaced the placeholder PDF parser path with a Firecrawl-based local Node helper~~
- ~~Added `package.json` so the repo can resolve `@firecrawl/pdf-inspector` locally~~
- ~~Installed Node.js, npm, Docker, and Tailscale in the live LXC~~
- ~~Deployed the app live on `specflow-ai` (`CT 211`)~~
- ~~Verified the app is listening on port `8501`~~
- ~~Verified the Tailscale machine is connected~~
- ~~Added container-focused deployment files to the repo~~

Live access at time of update:

```text
Tailscale URL: http://100.121.124.113:8501
LAN URL:       http://192.168.50.198:8501
```

---

# Current PDF Parser Design

~~Prompt 12 - PDF Inspector Parser~~

Implemented approach:

```text
Python Streamlit app
  -> app/parsers/pdf_inspector_parser.py
  -> shells out to Node helper app/parsers/pdf_inspector_node.mjs
  -> imports @firecrawl/pdf-inspector
  -> returns pdfType / markdown / OCR metadata
```

Current behavior:

- Uses Firecrawl local PDF inspector first
- Maps `TextBased`, `Mixed`, `Scanned`, `ImageBased` into SpecFlow classifications
- Marks scanned/image-heavy documents as OCR-required
- Falls back to `pymupdf4llm` if Firecrawl fails so the app stays usable during MVP work

Remaining improvement:

- Remove or reduce fallback once Firecrawl parsing is considered stable enough for all demo inputs

---

# Live Deployment Notes

~~Prompt 15 - Docker Container Setup~~

Repo status:

- ~~`Dockerfile` added~~
- ~~`docker-compose.yml` added~~
- ~~`.dockerignore` added~~
- ~~`docs/deployment.md` added~~

Live runtime status:

```text
The current live app on CT 211 is not running from Docker yet.
It is running from a Python virtual environment:
  /root/Document-to-Workflow-AI-Orchestrator/.venv
```

That means:

- ~~Container host exists and is reachable~~
- ~~App is live~~
- Dockerized repo path still needs a clean end-to-end verification from the pushed repo

---

# Tailscale Status

~~Prompt 16 - Tailscale Team Access~~

Current state:

- ~~`specflow-ai` machine joined to tailnet~~
- ~~Tailnet browser access works~~

Still left:

- Share with additional teammates if needed
- Optionally enable MagicDNS naming if you want a friendly hostname

---

# Remaining Build Order

1. Add `docx` ingestion
2. Add `xlsx/csv` schedule-aware ingestion
3. Add tests for parser, scorer, filter engine
4. Add sample documents and demo fixtures
5. Add `systemd` service for auto-start in `CT 211`
6. Validate Dockerized deployment path from the pushed repo
7. Update UI labels and demo flow docs for non-PDF document support

---

# Project Guardrails

Do build:

```text
~~Streamlit web app~~
~~PDF upload and parsing~~
~~Source-confirmed detection matrix~~
~~Filtering summary~~
~~Workflow output~~
~~JSON / Markdown export~~
Word / Excel parsing
Tests
Sample docs
Systemd boot service
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
SpecFlow AI now proves the core document-to-workflow concept live in a browser:
source-confirmed workflow generation without hallucinating unsupported equipment,
points, protocols, or scope.
```
