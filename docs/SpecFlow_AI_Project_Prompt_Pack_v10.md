# SpecFlow AI - Project Prompt Pack v10

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current local branch baseline for this document: `main`
> Current GitHub commit baseline: `c249139`
> Current local working-tree changes not yet pushed: `Surya OCR fallback integration`

---

# Project Anchor

```text
SpecFlow AI parses engineering documents into structured deliverables for
Equipment, I/O Lists, and Sequences of Operation, then exports those outputs
as CSV, JSON, and Markdown.
```

Core rule:

```text
Known vocabulary is not the same as detected vocabulary.
The source document must support every output item.
```

Current product framing:

```text
Input: PDF, Word, Excel, CSV, pasted text
Output: equipment.*, io_list.*, soo.*
Formats: .csv, .json, .md
```

---

# Build Status

| Area | Status | Notes |
|---|---|---|
| ~~Repo scaffold~~ | Done | Flattened Python app repo in place |
| ~~Knowledge base (BMS / PLC / ICS / power / data center / HVAC terms)~~ | Done | Expanded HVAC/BMS vocabulary and normalized equipment types |
| ~~Confidence rules / filter rules / template rules~~ | Done | Weighted scoring, suppression, template thresholds live |
| ~~Markdown and term normalizers~~ | Done | Normalization layer in place |
| ~~PDF parser~~ | Done | Firecrawl pdf-inspector + OCR fallback path |
| ~~DOCX parser~~ | Done | `python-docx` parser wired |
| ~~DOC (legacy) parser~~ | Done | `antiword` subprocess parser |
| ~~Excel parser~~ | Done | `openpyxl` parser wired |
| ~~CSV parser~~ | Done | Direct CSV ingestion routed through tabular parser |
| ~~Upload UX simplification~~ | Done | One uploader for PDF / Word / Excel / CSV + paste mode |
| ~~Vocabulary schema~~ | Done | `VocabularyTerm` model + KB validation |
| ~~Master HVAC/BMS equipment type list~~ | Done | Core equipment families expanded and normalized |
| ~~Equipment schema~~ | Done | `EquipmentRecord` with nested industry-grounded attributes |
| ~~Point schema~~ | Done | `PointRecord` with BAS/BACnet-style typing |
| ~~Child component schemas~~ | Done | `ValveRecord`, `DamperRecord`, `ActuatorRecord`, `SensorRecord` |
| ~~SOO schema~~ | Done | `SOORecord` with mode, step, setpoint, safety-critical fields |
| ~~Equipment extractor~~ | Done | Table-driven structured extraction from normalized Markdown |
| ~~Points extractor~~ | Done | Table-driven points extraction and row typing |
| ~~SOO extractor~~ | Done | Prose-based extractor with mode grouping |
| ~~Equipment-tag detection and grouping~~ | Done | Shared grouping/mapping logic |
| ~~Source labels~~ | Done | `source_extracted`, `template_default`, `template_only`, `inferred` |
| ~~Confidence / review flags per row~~ | Done | Confidence bands + review-required reasoning on records |
| ~~Template fallback merge logic~~ | Done | Source rows primary; template rows backfill gaps |
| ~~Template fallback gating~~ | Done | Below threshold -> `template_only`; excluded from exports |
| ~~JSON export for Equipment / I/O / SOO~~ | Done | Structured exports for all three deliverables |
| ~~CSV export for Equipment / I/O / SOO~~ | Done | Flat CSV exports for all three deliverables |
| ~~Markdown export for Equipment / I/O / SOO~~ | Done | Human-readable markdown exports for all three deliverables |
| ~~OCR quality gate~~ | Done | `ok` / `warn` / `blocked` export gating |
| ~~UI tabs for Equipment / I/O List / SOO~~ | Done | Dedicated top-level tabs |
| ~~UI tab cleanup~~ | Done | Upload / Inspection / Raw Markdown / Equipment / I/O List / SOO / Exports / About |
| ~~Detection Matrix demoted~~ | Done | No longer exported from primary surface |
| ~~Filtering Summary demoted~~ | Done | No longer exported from primary surface |
| ~~Workflow Output demoted~~ | Done | No longer exported from primary surface |
| ~~Primary export surface trimmed to CSV / JSON / Markdown only~~ | Done | Workbook and debug downloads removed |
| ~~Extraction / grouping / fallback tests~~ | Done | End-to-end structured pipeline coverage added |
| ~~All document type smoke tests~~ | Done | PDF, DOCX, DOC, XLSX, CSV, pasted text covered |
| ~~Tesseract installed in Docker path~~ | Done | `tesseract-ocr` now installed in `Dockerfile` |
| Surya OCR fallback before Tesseract | Local only | Implemented locally, not pushed yet |
| Shared OCR usability helper between parser and OCR gate | Local only | Implemented locally, not pushed yet |
| Real CT 211 Surya validation | Not done | Needs `pip install -r requirements.txt` and scanned PDF smoke run |
| Sample demo documents | Not done | `samples/` still needs curated project inputs |
| Auto-start service in live CT | Not done | App still needs clean `systemd` service |
| Structured valve / damper schedule extraction | Not done | Schemas are ready; extractor/output path still pending |
| Formula helper layer (Cv / face velocity) | Not done | Defer until schedule extraction exists |

---

# Current App Shape

## Tabs

```text
Upload | Inspection | Raw Markdown | Equipment | I/O List | SOO | Exports | About
```

## Supported inputs

```text
PDF
Word (.docx / .doc)
Excel (.xlsx / .xls)
CSV
Pasted text / Markdown
```

## Primary exports

```text
equipment.csv
equipment.json
equipment.md

io_list.csv
io_list.json
io_list.md

soo.csv
soo.json
soo.md
```

## What is no longer part of the primary export surface

```text
specflow_all.xlsx
detection_matrix.json
detection_matrix.md
filtering_summary.md
workflow_items.json
workflow_report.md
```

---

# What Changed Since v9

## 1. GitHub main moved forward again

Current local/GitHub baseline now includes:

- `c249139` `fix: add tesseract-ocr to Dockerfile — OCR fallback was coded but not installed`

This means the repository now explicitly installs:

- `tesseract-ocr`

in the Docker build path, so OCR fallback is not just coded, but also provisioned for container deployments.

## 2. Surya OCR fallback was implemented locally

Local working tree now includes Surya integration in:

- `app/parsers/pdf_inspector_parser.py`
- `app/parsers/ocr_gate.py`
- `requirements.txt`
- `tests/test_pdf_inspector_parser.py`
- `tests/test_ocr_gate.py`

Behavior:

```text
pdf-inspector / Firecrawl
-> if usable markdown exists, stop
-> if scanned or image-heavy and no usable markdown:
   try Surya OCR
-> if Surya unavailable, fails, or returns weak OCR text:
   try Tesseract OCR
-> if both fail:
   keep current blocked / ocr_required behavior
```

Important safety rule now enforced:

```text
Do not invoke Surya or Tesseract when pdf-inspector already returns usable
markdown for a text PDF or mixed PDF.
```

## 3. OCR gate thresholds are now shared with the parser

Local changes added:

- `ocr_text_is_usable(...)`

This removes split logic between:

- OCR quality gate
- parser fallback selection

Effects:

- weak Surya output falls through to Tesseract
- Tesseract output must also clear the same minimum OCR thresholds
- parser and export gate now evaluate OCR usefulness with the same rules

## 4. Surya-specific smoke validation was added locally

Local smoke validation confirmed:

- text PDFs bypass OCR
- Surya succeeds first when it returns usable OCR text
- weak Surya output falls back to Tesseract

Local smoke summary:

```text
TEXT_BYPASS -> success, no OCR engine invoked
SURYA_SUCCESS -> success, ocr_engine=surya
SURYA_WEAK_TESSERACT -> success, ocr_engine=tesseract
```

This smoke used the real subprocess/parser path with a fake `surya_ocr` CLI shim,
because Surya is not installed in the current local Windows environment.

---

# Current Key Files

## Parsers

```text
app/parsers/pdf_inspector_parser.py
app/parsers/docx_parser.py
app/parsers/doc_parser.py
app/parsers/excel_parser.py
app/parsers/ocr_gate.py
```

## Structured schemas

```text
app/schemas/vocabulary.py
app/schemas/equipment.py
app/schemas/points.py
app/schemas/soo.py
app/schemas/components.py
app/schemas/review.py
```

## Extractors

```text
app/extractors/equipment_extractor.py
app/extractors/points_list_extractor.py
app/extractors/soo_extractor.py
app/extractors/grouping.py
app/extractors/template_fallback_merge.py
app/extractors/source_labels.py
```

## Exporters

```text
app/exporters/csv_exporter.py
app/exporters/markdown_exporter.py
app/exporters/__init__.py
```

## UI

```text
app/ui/streamlit_app.py
```

---

# Test Coverage

Current local branch passes:

```text
python -m unittest discover -s tests

Ran 136 tests
OK
```

Increment since v9:

- Surya/Tesseract fallback behavior tests
- text-PDF OCR bypass tests
- shared OCR usability helper tests

Coverage now includes:

- parser tests
- OCR gate tests
- schema tests
- equipment extractor tests
- points extractor tests
- SOO extractor tests
- grouping tests
- source-label tests
- template fallback tests
- markdown-table parsing tests
- document type end-to-end smoke tests

Document-type smoke coverage includes:

- PDF
- DOCX
- DOC
- XLSX
- CSV
- pasted text

---

# Current Demo Positioning

The current build is best described as:

```text
A working prototype that parses engineering documents into three structured
deliverables: Equipment, I/O List, and SOO, with export-ready CSV, JSON,
and Markdown outputs.
```

What it does well:

- multi-format ingestion
- structured extraction
- export-ready outputs
- OCR recovery path for scanned PDFs
- guarded exports when OCR quality is too weak
- automated test coverage

What is still demo/prototype-grade:

- Surya fallback has not yet been validated on CT 211 with a real installed binary
- poor scanned PDFs can still degrade extraction quality
- valve/damper schedule extraction is not yet first-class
- auto-start/service packaging is not finished

---

# Remaining Build Order

1. Push Surya OCR fallback changes to GitHub
2. Install `surya-ocr` on CT 211 via `pip install -r requirements.txt`
3. Run a real scanned-PDF smoke test on CT 211
4. Add curated sample/demo documents to `samples/`
5. Add clean `systemd` auto-start in the live container
6. Build structured valve / damper schedule extraction
7. Add linked extraction for valves / dampers / actuators / sensors
8. Add formula helper layer after schedule extraction exists

---

# Final Focus Sentence

```text
SpecFlow AI v10 reflects the current narrowed product direction:
parse PDF / Word / Excel / CSV documents into three primary deliverables
(Equipment / I/O List / SOO) and export only CSV, JSON, and Markdown.

GitHub baseline is c249139.
Local branch adds Surya OCR fallback before Tesseract and passes 136 tests,
but that OCR upgrade is not pushed yet.
```
