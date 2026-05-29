# SpecFlow AI - Project Prompt Pack v8

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current working branch for this build batch: `main`

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
| ~~Knowledge base (BMS / PLC / ICS / power / data center terms)~~ | Done | Expanded vocabulary, including broader HVAC equipment coverage |
| ~~Confidence rules / filter rules / template rules~~ | Done | Weighted scoring, suppression, and template thresholds live |
| ~~Markdown and term normalizers~~ | Done | Normalization layer in place |
| ~~PDF parser~~ | Done | Firecrawl pdf-inspector + OCR fallback path |
| ~~DOCX parser~~ | Done | `python-docx` parser wired |
| ~~DOC (legacy) parser~~ | Done | `antiword` subprocess parser; Dockerfile updated |
| ~~Excel parser~~ | Done | `openpyxl` parser wired |
| ~~Workflow extractor~~ | Done | Template-driven workflow outputs in debug expander |
| ~~Vocabulary schema~~ | Done | `VocabularyTerm` model + KB validation |
| ~~Master HVAC/BMS equipment type list~~ | Done | Core equipment families expanded and normalized |
| ~~Equipment schema~~ | Done | `EquipmentRecord` with nested industry-grounded attributes |
| ~~Point schema~~ | Done | `PointRecord` with BAS/BACnet-style typing |
| ~~Child component schemas~~ | Done | `ValveRecord`, `DamperRecord`, `ActuatorRecord`, `SensorRecord` |
| ~~SOO schema~~ | Done | `SOORecord` with mode, step, setpoint, safety-critical fields |
| ~~Equipment extractor~~ | Done | Table-driven structured extraction from normalized Markdown |
| ~~Points extractor~~ | Done | Table-driven points extraction and row typing |
| ~~SOO extractor~~ | Done | Prose-based extractor; mode set by section header only |
| ~~Equipment-tag detection and grouping~~ | Done | Shared grouping/mapping logic |
| ~~Source labels~~ | Done | `source_extracted`, `template_default`, `template_only`, `inferred` |
| ~~Confidence / review flags per row~~ | Done | Confidence bands + review-required reasoning on records |
| ~~Template fallback merge logic~~ | Done | Source rows primary; template rows backfill gaps; gated at 0.70 |
| ~~Template fallback gating~~ | Done | Below 0.70 confidence → `template_only`; excluded from exports |
| ~~JSON export for equipment, points, SOO~~ | Done | Structured exports for all three deliverables |
| ~~CSV / XLSX export for equipment, points, SOO~~ | Done | Flat CSV + workbook with multi-sheet export |
| ~~Markdown export for equipment, points, SOO~~ | Done | Human-readable table export for all three deliverables |
| ~~OCR quality gate~~ | Done | `ok` / `warn` / `blocked` levels; per-tab banners; export disable |
| ~~UI tabs for Equipment, I/O List, SOO~~ | Done | Dedicated tab per primary deliverable |
| ~~UI tab cleanup~~ | Done | Upload / Inspection / Raw Markdown / Equipment / I/O List / SOO / Exports / About |
| ~~Detection Matrix demoted~~ | Done | Moved into Exports → Debug / Advanced expander |
| ~~Filtering Summary demoted~~ | Done | Moved into Exports → Debug / Advanced expander |
| ~~Workflow Output demoted~~ | Done | Removed as tab; full display in Debug / Advanced expander |
| ~~Extraction / grouping / fallback tests~~ | Done | End-to-end structured pipeline coverage added |
| ~~All document type smoke tests~~ | Done | PDF, DOCX, XLSX, and pasted text all pass locally |
| Sample demo documents | Not done | `samples/` still needs curated project inputs |
| Auto-start service in live CT | Not done | App still needs clean `systemd` service |
| Structured valve / damper schedule extraction | Not done | Schemas are ready; extractor/output path still pending |
| Formula helper layer (Cv / face velocity) | Not done | Defer until schedule extraction exists |

---

# What Changed In v8

## Step 4 — OCR quality gate

- Added `app/parsers/ocr_gate.py`
  - `ocr_quality(parse_result) -> (level, message)` — three levels: `"ok"`, `"warn"`, `"blocked"`
  - Blocked: `status == "failed"`, `ocr_required and not ocr_applied`, OCR recovered < 200 chars or < 30 words
  - Warned: OCR applied with enough text, or `mixed_pdf` classification
  - `is_blocked()` and `is_warned()` convenience helpers
- Wired gate into `streamlit_app.py`
  - `⛔` error banner on Equipment, I/O List, Workflow Output, and Exports tabs when blocked
  - `⚠️` warning banner on same tabs when OCR was applied
  - All 10 primary export download buttons get `disabled=True` when blocked
- Added `tests/test_ocr_gate.py` — 21 tests covering ok / blocked / warn / edge cases

## Step 5 — Tab demotion (structural)

- Removed Detection Matrix and Filtering Summary as top-level tabs
- Moved both as live display panels (metrics + full content + downloads) into Exports → `Debug / Advanced` expander
- Demoted Workflow Output to after Exports in the tab bar
- Tab count reduced from 10 to 8 (before cleanup)

## Step 6 — UI tab wording cleanup

- Renamed `"Upload / Ingest"` → `"Upload"`, `"Document Inspection"` → `"Inspection"`
- Added dedicated `"SOO"` tab (index 5) between I/O List and Exports
  - Shows step count, mode count, safety-critical count, review-required count
  - Mode-mix caption + dataframe display
  - OCR gate banner
- Removed Workflow Output as a tab entirely
  - RFI items, field verification, commissioning, CAD, submittal displays moved to Debug / Advanced
- Final tab order: Upload | Inspection | Raw Markdown | Equipment | I/O List | SOO | Exports | About
- Updated `st.header()` labels in all affected tabs

## Step 7 — Template fallback gating

- Added `"template_only"` to `SourceType` in `app/schemas/review.py`
  - Review reason: `"equipment type not source-confirmed — template row excluded from default exports"`
- Added `EQUIPMENT_TEMPLATE_THRESHOLD = 0.70` constant in `app/extractors/template_fallback_merge.py`
- `merge_point_records_with_template_defaults` now gates on `equipment.confidence`:
  - `≥ 0.70` → `source_type = "template_default"` (included in exports)
  - `< 0.70` → `source_type = "template_only"` (visible in I/O List tab, excluded from exports)
- Added `export_point_records(records)` helper — strips `template_only` rows
- Wired into `streamlit_app.py`
  - I/O List tab shows `Unconfirmed (excluded)` metric and info banner when `template_only` rows exist
  - Exports tab calls `export_point_records()` before building `io_rows` for CSV / JSON / XLSX

## Step 8 — Legacy `.doc` support

- Added `app/parsers/doc_parser.py`
  - Calls `antiword -w 0` via subprocess
  - Converts plain-text output to minimal Markdown (ALL-CAPS / Title-Case short lines → `##` headings)
  - `shutil.which("antiword")` guard: returns `status="failed"` with actionable message if not installed
  - Same result-dict shape as all other parsers → OCR gate, extractors, exports all work unchanged
- Added `antiword` to `Dockerfile` `apt-get install` line (single-line addition, ~100 KB)
- Wired into `streamlit_app.py`
  - `.doc` added to `type=` list on file uploader
  - Parse branch: `suffix == ".doc"` → `parse_doc_to_markdown(tmp_path)`
  - About tab formats table updated with DOC row

---

# Files Added In This Batch

```text
app/parsers/doc_parser.py
app/parsers/ocr_gate.py
tests/test_doc_parser.py
tests/test_ocr_gate.py
docs/SpecFlow_AI_Project_Prompt_Pack_v8.md
```

# Files Modified In This Batch

```text
Dockerfile
app/exporters/markdown_exporter.py
app/exporters/__init__.py
app/extractors/template_fallback_merge.py
app/schemas/review.py
app/schemas/soo.py                          (added in prior session)
app/extractors/soo_extractor.py             (added in prior session)
app/schemas/__init__.py
app/ui/streamlit_app.py
tests/test_template_fallback_merge.py
```

---

# Test Coverage

```text
Ran 115 tests in 2.977s
OK

New in v8:
  test_doc_parser.py         — 20 tests (file guards, success, failure, markdown converter)
  test_ocr_gate.py           — 21 tests (ok / blocked / warn / edge cases)
  test_template_fallback_merge.py — 9 new tests (gating: 5, export filter: 4)
  Total new tests: 50  (86 → 115 + earlier session SOO tests)
```

---

# Remaining Build Order

1. Add curated real-world sample documents to `samples/`
2. Add `systemd` auto-start service in the live container
3. Sync and run this build on the real testing machine end-to-end
4. Build structured valve / damper schedule extraction
5. Add linked child-record extraction for valves / dampers / actuators / sensors
6. Add formula helper layer (Cv / face velocity) after schedule extraction exists

---

# Final Focus Sentence

```text
SpecFlow AI v8 completes the core product loop: three primary deliverables
(Equipment / I/O List / SOO), an OCR quality gate that blocks bad exports,
a clean 8-tab UI, template gating that keeps only source-confirmed backfill
in primary exports, and legacy .doc support via antiword.
115 tests, all passing.
```
