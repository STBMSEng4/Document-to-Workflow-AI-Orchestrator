# SpecFlow AI - Project Prompt Pack v7

> Living build document. Completed items use strikethrough. Open items remain plain.
> Current working branch for this build batch: `Cryptocrack4011`

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
| ~~Excel parser~~ | Done | `openpyxl` parser wired |
| ~~Workflow extractor~~ | Done | Template-driven workflow outputs still available |
| ~~Vocabulary schema~~ | Done | `VocabularyTerm` model + KB validation |
| ~~Master HVAC/BMS equipment type list~~ | Done | Core equipment families expanded and normalized |
| ~~Equipment schema~~ | Done | `EquipmentRecord` with nested industry-grounded attributes |
| ~~Point schema~~ | Done | `PointRecord` with BAS/BACnet-style typing |
| ~~Child component schemas~~ | Done | `ValveRecord`, `DamperRecord`, `ActuatorRecord`, `SensorRecord` |
| ~~Equipment extractor~~ | Done | Table-driven structured extraction from normalized Markdown |
| ~~Points extractor~~ | Done | Table-driven points extraction and row typing |
| ~~Equipment-tag detection and grouping~~ | Done | Shared grouping/mapping logic |
| ~~Source labels~~ | Done | `source_extracted`, `template_default`, `inferred` |
| ~~Confidence / review flags per row~~ | Done | Confidence bands + review-required reasoning on records |
| ~~Template fallback merge logic~~ | Done | Source rows stay primary; template rows backfill gaps |
| ~~JSON export for equipment and points~~ | Done | Structured exports available |
| ~~CSV / XLSX export for equipment and points~~ | Done | Flat CSV + workbook with multi-sheet export |
| ~~UI tabs for Equipment and Points~~ | Done | Structured records visible in Streamlit |
| ~~Extraction / grouping / fallback tests~~ | Done | End-to-end structured pipeline coverage added |
| ~~All document type smoke tests~~ | Done | PDF, DOCX, XLSX, and pasted text all pass locally |
| Sample demo documents | Not done | `samples/` still needs curated project inputs |
| Auto-start service in live CT | Not done | App still needs clean `systemd` service |
| Verified Dockerized runtime from repo | Not done | Docker assets exist; live deployment still uses `.venv` |
| Structured valve / damper schedule extraction | Not done | Schemas are ready; extractor/output path still pending |
| Formula helper layer (Cv / face velocity) | Not done | Defer until schedule extraction exists |

---

# What Changed In v7

- ~~Added typed schema layer for structured extraction~~
  - `app/schemas/vocabulary.py`
  - `app/schemas/equipment.py`
  - `app/schemas/points.py`
  - `app/schemas/components.py`
  - `app/schemas/review.py`

- ~~Expanded equipment vocabulary and normalized equipment types~~
  - Added broader HVAC/BMS coverage for:
    - `RTU`, `AHU`, `MAU`, `DOAS`, `ERU`, `HRV`, `VAV`, `CAV`, `FCU`,
      `Unit Heater`, `Cabinet Unit Heater`, `Mini Split`, `Heat Pump`,
      `WSHP`, `VRF`, `VRV`, `CRAH`, `CRAC`, `Exhaust Fan`, `Supply Fan`,
      `Return Fan`, `Relief Fan`, pumps, boilers, chillers, cooling towers,
      humidification, and related plant / terminal equipment.

- ~~Built structured extraction for equipment and points~~
  - `app/extractors/equipment_extractor.py`
  - `app/extractors/points_list_extractor.py`
  - `app/extractors/grouping.py`
  - `app/extractors/source_labels.py`
  - `app/extractors/template_fallback_merge.py`

- ~~Made point extraction equipment-aware~~
  - Points can now map to equipment by:
    - explicit equipment tag
    - contextual tag detection from sequence text / descriptions
    - grouped fallback mapping

- ~~Added row-level review logic~~
  - Source rows remain `source_extracted`
  - Context-derived rows become `inferred`
  - Template backfill rows become `template_default`
  - Confidence bands and `review_required` are now embedded in records

- ~~Added structured export helpers~~
  - Flat CSV export for records
  - Workbook export with separate sheets
  - Nested schema flattening for UI and downloads

- ~~Rebuilt the Streamlit UI around the new structured layer~~
  - Added `Equipment` tab
  - Added `Points` tab
  - Added JSON / CSV / XLSX downloads for structured records
  - Kept the old workflow output tab intact as a parallel layer

- ~~Hardened PDF table parsing for real structured extraction~~
  - Firecrawl sometimes returns inline Markdown table rows from PDFs
  - `_markdown_tables.py` now expands those rows before parsing
  - This fixed the structured PDF smoke path for equipment / points extraction

---

# Smoke Test Findings

## Structured pipeline smoke

```text
equipment_count: 2
source_point_count: 3
merged_point_count: 40
grouped_tags: ['AHU-1', 'RTU-2']
source_extracted: 2
inferred: 1
template_default: 37
```

## All document type end-to-end smoke

```text
text  -> success, equipment=2, source_points=2, final_points=39
docx  -> success, equipment=2, source_points=2, final_points=39
xlsx  -> success, equipment=2, source_points=2, final_points=39
pdf   -> success, equipment=2, source_points=2, final_points=39
```

## Full local regression status

```text
Ran 36 tests
OK
```

---

# Files Added In This Batch

```text
app/extractors/_markdown_tables.py
app/extractors/equipment_extractor.py
app/extractors/grouping.py
app/extractors/points_list_extractor.py
app/extractors/source_labels.py
app/extractors/template_fallback_merge.py
app/schemas/__init__.py
app/schemas/components.py
app/schemas/equipment.py
app/schemas/points.py
app/schemas/review.py
app/schemas/vocabulary.py
tests/test_component_schemas.py
tests/test_document_type_end_to_end_smoke.py
tests/test_equipment_extractor.py
tests/test_equipment_schema.py
tests/test_grouping_logic.py
tests/test_markdown_tables.py
tests/test_point_schema.py
tests/test_points_list_extractor.py
tests/test_source_labels.py
tests/test_structured_pipeline_smoke.py
tests/test_tabular_exporter.py
tests/test_template_fallback_merge.py
tests/test_vocabulary_schema.py
```

---

# Remaining Build Order

1. Add curated real-world sample documents
2. Add `systemd` auto-start service in the live container
3. Sync and run this structured build on the real testing machine
4. Build structured valve schedule extraction
5. Build structured damper schedule extraction
6. Add linked child-record extraction for valves / dampers / actuators / sensors
7. Add formula helper layer after schedule extraction exists
8. Validate Dockerized runtime end to end from repo

---

# Final Focus Sentence

```text
SpecFlow AI now has a real structured extraction layer for equipment and points,
with source labeling, review flags, fallback merge behavior, structured exports,
and passing end-to-end smoke tests across PDF, DOCX, XLSX, and pasted text.
The next milestone is real-world machine validation and schedule-level extraction.
```
