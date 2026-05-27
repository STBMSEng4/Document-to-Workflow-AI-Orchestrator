# SpecFlow AI - Project Prompt Pack v6

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current live target: Proxmox LXC `CT 211` (`specflow-ai`), published privately over Tailscale and publicly over Funnel.

---

# Project Anchor

```text
SpecFlow AI converts messy engineering documents into clean AI-agent-ready Markdown,
then uses a BMS / HVAC / ICS / PLC knowledge base plus source-confirmed confidence
scoring to generate workflow-ready engineering outputs.
```

Core rule:

```text
Known vocabulary is not the same as detected vocabulary.
The source document must support every output item.
```

---

# Build Status

| Area | Status | Notes |
|---|---|---|
| ~~Repo scaffold~~ | Done | Flattened Python app repo in place |
| ~~Knowledge base (BMS / PLC / ICS / power / data center terms)~~ | Done | Expanded equipment + power distribution vocabulary is live |
| ~~confidence_rules.json~~ | Done | Weighted scoring model |
| ~~filtering_rules.json~~ | Done | Suppression + threshold gating |
| ~~template_rules.json~~ | Done | Template trigger thresholds live |
| ~~app/scoring/~~ | Done | Confidence scorer, detection matrix, filter engine |
| ~~app/normalizers/~~ | Done | Markdown and term normalizers |
| ~~app/exporters/~~ | Done | Markdown, JSON, CSV exporters |
| ~~Streamlit UI~~ | Done | Upload -> inspect -> score -> filter -> workflow -> export |
| ~~Firecrawl PDF parser integration~~ | Done | Local `@firecrawl/pdf-inspector` via Node helper |
| ~~DOCX parser~~ | Done | `python-docx` parser wired into the UI |
| ~~Excel parser~~ | Done | `openpyxl` parser wired into the UI |
| ~~Workflow extractor~~ | Done | Stub replaced with real points / RFI / field / cx / CAD / submittal outputs |
| ~~Container repo sync to GitHub~~ | Done | Live container synced to commit `0df9b3d` on `Cryptocrack4011` |
| ~~Scanned PDF detection fix~~ | Done | Scanned/image-heavy PDFs now stay `ocr_required` instead of degrading to generic failed parse |
| ~~Parser regression test for scanned PDFs~~ | Done | Added unit coverage for scanned vs text PDF status handling |
| ~~Tailscale access~~ | Done | Tailnet access working |
| ~~Tailscale Funnel~~ | Done | Public HTTPS endpoint enabled |
| Tests beyond parser status | Partial | Basic parser regression coverage added; scorer/filter/workflow tests still missing |
| Sample demo documents | Not done | `samples/` still needs curated inputs |
| Auto-start service in live CT | Not done | App still needs clean `systemd` service |
| Verified Dockerized runtime from repo | Not done | Docker assets exist; live deployment still uses `.venv` |
| Structured valve / damper schedule extraction | Not done | Schema + extractor layer still pending |
| Formula helper layer (Cv / face velocity) | Not done | Defer until structured extraction exists |

---

# What Changed In v6

- ~~Corrected the live container repo drift~~
  - The app container had been running an older checkout with newer local parser patches.
  - The repo in `CT 211` is now cleanly synced to GitHub commit `0df9b3d`.

- ~~Confirmed DOCX and Excel ingestion are fully present in the current repo~~
  - `app/parsers/docx_parser.py`
  - `app/parsers/excel_parser.py`
  - `app/ui/streamlit_app.py` routes uploads to both parsers

- ~~Fixed scanned PDF status handling~~
  - Firecrawl already detected scanned PDFs correctly.
  - The Python wrapper was incorrectly collapsing empty scanned output into `empty_or_failed_parse`.
  - The wrapper now preserves `scanned_pdf` / OCR-required status and surfaces a clear warning.

- ~~Added parser regression coverage~~
  - Scanned PDF -> `ocr_required`
  - Text PDF -> `success`

- ~~Published the app through Tailscale Funnel~~
  - Public URL:

```text
https://specflow-ai.tail4c526a.ts.net/
```

---

# Smoke Test Findings

Known-good text PDF:

```text
status: success
pdf_classification: text_pdf
ocr_required: false
```

Real uploaded PDFs that previously showed "failed parse":

```text
Firecrawl result:
  pdfType: Scanned
  confidence: 0.95
  pagesNeedingOcr: [1]
```

Meaning:

- The parser stack itself is working.
- Those documents are scanned/image-only PDFs.
- They need OCR before SpecFlow can produce useful source-confirmed workflow output.

---

# Live Access

Tailnet:

```text
http://100.121.124.113:8501
http://specflow-ai.tail4c526a.ts.net:8501
```

Public Funnel:

```text
https://specflow-ai.tail4c526a.ts.net/
```

LAN:

```text
http://192.168.50.198:8501
```

---

# Remaining Build Order

1. Add `systemd` auto-start service in `CT 211`
2. Add scorer / filter / workflow extractor tests
3. Add curated sample documents
4. Build structured valve schedule schema + extractor
5. Build structured damper schedule schema + extractor
6. Add dedicated schedule exports / UI tabs
7. Add formula helper layer after source extraction exists
8. Validate Dockerized runtime end to end from repo

---

# Final Focus Sentence

```text
SpecFlow AI now has clean multi-format ingestion, a synced live container,
clear scanned-PDF / OCR-required reporting, and a public browser-access path.
The next milestone is structured engineering schedule extraction.
```
