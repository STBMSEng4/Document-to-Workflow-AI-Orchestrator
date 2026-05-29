# SpecFlow AI - Project Prompt Pack v9

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current GitHub branch baseline for this document: `main`
> Current GitHub commit baseline: `61c4d5f`

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
| Sample demo documents | Not done | `samples/` still needs curated project inputs |
| Auto-start service in live CT | Not done | App still needs clean `systemd` service |
| Structured valve / damper schedule extraction | Not done | Schemas are ready; extractor/output path still pending |
| Formula helper layer (Cv / face velocity) | Not done | Defer until schedule extraction exists |

---

# Current App Shape (GitHub Main)

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

# What Changed Since v8

## 1. SOO became a first-class deliverable

GitHub now includes:

- `app/schemas/soo.py`
- `app/extractors/soo_extractor.py`
- `tests/test_soo_extractor.py`

This means SpecFlow no longer stops at Equipment + I/O. It now extracts a real
Sequence of Operations output and exposes it as:

- `soo.csv`
- `soo.json`
- `soo.md`

The UI also has a dedicated `SOO` tab with:

- step count
- mode count
- safety-critical count
- review-required count

## 2. Upload flow was simplified

The older multi-mode upload experience was replaced with:

- one uploader for PDF / Word / Excel / CSV
- one paste-text mode
- a clean error when the user clicks Run without selecting a file

Current uploader label:

```text
Upload PDF, Word (.docx / .doc), Excel, or CSV
```

## 3. CSV became a first-class input

GitHub now includes direct CSV parsing in:

- `app/parsers/excel_parser.py`

Routing behavior:

- `.xlsx` / `.xls` -> workbook parser
- `.csv` -> direct CSV parser

This was added so schedules and I/O lists exported from engineering tools can be
ingested directly, without forcing users through Excel workbooks.

## 4. Legacy `.doc` support was added

GitHub now includes:

- `app/parsers/doc_parser.py`

Parser behavior:

- uses `antiword`
- converts recovered text into minimal Markdown
- integrates with the same OCR gate / extraction / export pipeline

This keeps older controls specs and schedule docs usable in the same app flow.

## 5. OCR gating is now part of the export contract

GitHub now includes:

- `app/parsers/ocr_gate.py`
- `tests/test_ocr_gate.py`

Three states are supported:

- `ok`
- `warn`
- `blocked`

Effects:

- blocked documents disable exports
- warn documents allow exports but show a review warning
- OCR-recovered text can still flow into extraction when quality is acceptable

## 6. Smoke-test reliability fixes landed

Recent GitHub fixes include:

- `42cdbf8` `fix: three smoke-test bugs — equipment false positives, points header aliases, SOO degF+multiline`
- `dd41fe5` `fix: reduce pdf ocr false positives in scoring`
- `2f9d6b5` `fix: harden pdf structured smoke parsing`

These corrected:

- equipment false positives in structured smoke tests
- points-table header alias mismatches
- SOO parsing edge cases around `degF` and multiline text
- false positives from OCR garbage for short terms
- PDF inline table / heading parsing problems

## 7. Exports were narrowed to the real product

This is the latest GitHub change in:

- `61c4d5f` `refactor: trim exports to primary deliverables only`

Meaning:

- workbook download removed
- debug/download bundles removed
- export surface now exactly matches the narrowed product ask:
  - Equipment
  - I/O List
  - SOO
  - CSV / JSON / Markdown only

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

Current GitHub main passes:

```text
python -m unittest discover -s tests

Ran 131 tests
OK
```

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

The current GitHub build is best described as:

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

- poor scanned PDFs can still degrade extraction quality
- valve/damper schedule extraction is not yet first-class
- auto-start/service packaging is not finished
- workflow/RFI/Cx logic still exists in code, but is no longer part of the primary product surface

---

# Remaining Build Order

1. Add curated sample/demo documents to `samples/`
2. Add clean `systemd` auto-start in the live container
3. Build structured valve / damper schedule extraction
4. Add linked extraction for valves / dampers / actuators / sensors
5. Add formula helper layer after schedule extraction exists
6. Continue improving OCR handling for poor-quality scanned BMS documents

---

# Final Focus Sentence

```text
SpecFlow AI v9 reflects the current GitHub product direction:
parse PDF / Word / Excel / CSV documents into three primary deliverables
(Equipment / I/O List / SOO) and export only CSV, JSON, and Markdown.
GitHub main is at 61c4d5f with 131 tests passing.
```
