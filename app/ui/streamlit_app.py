"""SpecFlow AI Streamlit UI."""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

import streamlit as st

# Allow imports from project root.
sys.path.insert(0, str(Path(__file__).parents[2]))

from app.exporters import flatten_records, rows_to_csv_bytes, rows_to_dataframe, tables_to_xlsx_bytes
from app.extractors.equipment_extractor import extract_equipment_records
from app.extractors.points_list_extractor import extract_point_records
from app.extractors.template_fallback_merge import merge_point_records_with_template_defaults
from app.extractors.workflow_extractor import extract_workflow_items
from app.normalizers.markdown_normalizer import normalize_text
from app.normalizers.term_normalizer import get_term_list
from app.parsers.docx_parser import parse_docx_to_markdown
from app.parsers.excel_parser import parse_tabular_to_markdown
from app.parsers.pdf_inspector_parser import inspect_pdf
from app.scoring.confidence_scorer import score_all_terms
from app.scoring.detection_matrix import build_json_matrix, build_markdown_matrix
from app.scoring.filter_engine import apply_filters, build_filter_markdown, evaluate_template_triggers


st.set_page_config(page_title="SpecFlow AI", layout="wide")

st.title("SpecFlow AI")
st.caption("Document-to-Workflow AI Orchestrator for BMS / HVAC Controls / ICS / PLC")


def _record_dicts(records: list[object]) -> list[dict]:
    return [
        record.model_dump(mode="json") if hasattr(record, "model_dump") else record
        for record in records
    ]


def _counter_markdown(counter: Counter[str]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in sorted(counter.items())) if counter else "None"


def _workflow_report_markdown(workflow_items: dict) -> str:
    lines = ["# SpecFlow AI - Workflow Report", ""]
    lines.append(f"**Summary:** {workflow_items.get('summary', '')}")
    lines.append("")

    if workflow_items.get("points"):
        lines.extend(
            [
                "## Points List Candidates",
                "",
                "| Equipment | Point Name | Abbr | I/O | Unit | Description |",
                "|---|---|---|---|---|---|",
            ]
        )
        for point in workflow_items["points"]:
            lines.append(
                f"| {point['equipment']} | {point['point_name']} | {point['abbreviation']} "
                f"| {point['io_type']} | {point['engineering_unit']} | {point['description']} |"
            )
        lines.append("")

    if workflow_items.get("rfis"):
        lines.extend(["## RFI Items", ""])
        for item in workflow_items["rfis"]:
            lines.append(f"- **{item['rfi_number']}** [{item['priority']}] {item['question']}")
        lines.append("")

    if workflow_items.get("field_verifications"):
        lines.extend(["## Field Verification Checklist", ""])
        for item in workflow_items["field_verifications"]:
            lines.append(f"- [ ] [{item['category']}] {item['task']}")
        lines.append("")

    if workflow_items.get("cx_items"):
        lines.extend(["## Commissioning Checklist", ""])
        for item in workflow_items["cx_items"]:
            lines.append(f"- **{item['test_name']}** ({item['category']}): {item['description']}")
        lines.append("")

    if workflow_items.get("cad_tasks"):
        lines.extend(["## CAD Tasks", ""])
        for item in workflow_items["cad_tasks"]:
            lines.append(f"- {item}")
        lines.append("")

    if workflow_items.get("submittal_items"):
        lines.extend(["## Submittal Items", ""])
        for item in workflow_items["submittal_items"]:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


tabs = st.tabs(
    [
        "Upload / Ingest",
        "Document Inspection",
        "Raw Markdown",
        "Detection Matrix",
        "Filtering Summary",
        "Equipment",
        "I/O List",
        "Workflow Output",
        "Exports",
        "About",
    ]
)


for key, default in {
    "parse_result": None,
    "source_text": "",
    "scored_terms": [],
    "filter_results": {},
    "template_decisions": [],
    "workflow_items": {},
    "equipment_records": [],
    "point_records": [],
    "merged_point_records": [],
    "matrix_mode": "workflow",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with tabs[0]:
    st.header("Upload / Ingest")

    input_mode = st.radio(
        "Input mode",
        ["Upload document", "Paste text / Markdown"],
        horizontal=True,
    )

    uploaded_file = None
    pasted_text = ""

    if input_mode == "Upload document":
        uploaded_file = st.file_uploader(
            "Upload PDF, Word (.docx), Excel, or CSV",
            type=["pdf", "docx", "xlsx", "xls", "csv"],
            help="SpecFlow currently supports PDF, Word (.docx), Excel (.xlsx/.xls), and CSV inputs.",
        )
    else:
        pasted_text = st.text_area(
            "Paste raw text or Markdown",
            height=300,
            placeholder="Paste specification text, controls narrative, or cut sheet content here.",
        )

    matrix_mode = st.radio(
        "Detection matrix mode",
        ["Workflow Output (source-confirmed only)", "Raw Detection Matrix (all KB terms)"],
        horizontal=True,
    )
    st.session_state.matrix_mode = "raw" if "Raw" in matrix_mode else "workflow"

    if st.button("Run SpecFlow AI", type="primary"):
        with st.spinner("Ingesting, extracting, and scoring..."):
            if input_mode == "Upload document" and not uploaded_file:
                result = {
                    "source_file": "",
                    "pdf_classification": "empty_or_failed_parse",
                    "raw_markdown": "",
                    "ocr_required": False,
                    "status": "failed",
                    "errors": ["Upload a PDF, Word, Excel, or CSV file before running SpecFlow AI."],
                    "metadata": {},
                    "ingestion_engine": "none",
                    "source_type": "none",
                }
            elif input_mode == "Upload document" and uploaded_file:
                suffix = Path(uploaded_file.name).suffix.lower()
                with tempfile.NamedTemporaryFile(suffix=suffix or ".tmp", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                if suffix == ".pdf":
                    result = inspect_pdf(tmp_path)
                elif suffix == ".docx":
                    result = parse_docx_to_markdown(tmp_path)
                elif suffix in {".xlsx", ".xls", ".csv"}:
                    result = parse_tabular_to_markdown(tmp_path)
                else:
                    result = {
                        "source_file": uploaded_file.name,
                        "pdf_classification": "empty_or_failed_parse",
                        "raw_markdown": "",
                        "ocr_required": False,
                        "status": "failed",
                        "errors": [f"Unsupported file type: {suffix or 'unknown'}"],
                        "metadata": {},
                        "ingestion_engine": "none",
                        "source_type": "none",
                    }
            else:
                result = {
                    "source_file": "pasted_text",
                    "pdf_classification": "text_input",
                    "raw_markdown": pasted_text,
                    "ocr_required": False,
                    "status": "success",
                    "errors": [],
                    "metadata": {},
                    "ingestion_engine": "text_paste",
                    "source_type": "text",
                }

            st.session_state.parse_result = result
            raw_markdown = result.get("raw_markdown", "")

            normalized = normalize_text(raw_markdown)
            st.session_state.source_text = normalized

            kb_terms = get_term_list()
            scored_terms = score_all_terms(kb_terms, normalized)
            st.session_state.scored_terms = scored_terms

            filter_results = apply_filters(scored_terms)
            st.session_state.filter_results = filter_results

            template_decisions = evaluate_template_triggers(scored_terms)
            st.session_state.template_decisions = template_decisions

            equipment_records = extract_equipment_records(normalized)
            point_records = extract_point_records(normalized, equipment_records=equipment_records)
            merged_point_records = merge_point_records_with_template_defaults(point_records, equipment_records)

            st.session_state.equipment_records = equipment_records
            st.session_state.point_records = point_records
            st.session_state.merged_point_records = merged_point_records

            workflow_items = extract_workflow_items(
                normalized,
                scored_terms=scored_terms,
                template_decisions=template_decisions,
            )
            st.session_state.workflow_items = workflow_items

        if result.get("ocr_applied"):
            st.info(
                "Scanned or image-heavy PDF was OCR-processed automatically. Review extracted text carefully before trusting downstream outputs."
            )
        elif result.get("status") == "ocr_required":
            st.warning(
                "Document parsed as scanned or image-heavy. OCR text is required before workflow extraction can continue."
            )
        elif result.get("status") == "failed":
            st.error("Parse failed. Check the inspection tab and parser warnings for details.")
        else:
            st.success("Done. Explore structured Equipment and Points tabs alongside the workflow outputs.")

        if result.get("errors"):
            for error in result["errors"]:
                st.warning(error)


with tabs[1]:
    st.header("Document Inspection Results")
    result = st.session_state.parse_result
    if result:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Source Type", str(result.get("source_type", "-")).upper())
        col2.metric("Classification", result.get("pdf_classification", "-"))
        col3.metric("Status", result.get("status", "-"))
        col4.metric("OCR Required", str(result.get("ocr_required", False)))

        if result.get("errors"):
            for error in result["errors"]:
                st.warning(error)

        if result.get("ocr_applied"):
            st.success("OCR fallback was applied to recover text from this scanned or image-heavy PDF.")
        elif result.get("status") == "ocr_required":
            st.info("This document looks scanned or image-heavy. SpecFlow still needs OCR text to build strong workflow outputs.")
            pages_needing_ocr = (result.get("metadata") or {}).get("pages_needing_ocr", [])
            if pages_needing_ocr:
                st.markdown(f"**Pages needing OCR:** {', '.join(str(page) for page in pages_needing_ocr)}")
        elif result.get("status") == "failed":
            st.error("SpecFlow could not extract usable Markdown from this file.")

        metadata = result.get("metadata", {})
        if metadata:
            st.subheader("File Metadata")
            st.json(metadata)
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[2]:
    st.header("Raw / Normalized Markdown")
    if st.session_state.source_text:
        st.markdown(f"**Character count:** {len(st.session_state.source_text):,}")
        st.text_area("Normalized Markdown", st.session_state.source_text, height=500)
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[3]:
    st.header("Detection Matrix")
    if st.session_state.scored_terms:
        mode = st.session_state.get("matrix_mode", "workflow")
        st.markdown(build_markdown_matrix(st.session_state.scored_terms, mode=mode))

        confirmed = [term for term in st.session_state.scored_terms if term.source_confirmed]
        not_detected = [term for term in st.session_state.scored_terms if not term.source_confirmed]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total KB Terms", len(st.session_state.scored_terms))
        col2.metric("Source Confirmed", len(confirmed))
        col3.metric("Not Detected (0.00)", len(not_detected))
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[4]:
    st.header("Filtering Summary")
    if st.session_state.filter_results:
        filter_results = st.session_state.filter_results
        template_decisions = st.session_state.template_decisions

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Allowed", len(filter_results.get("allowed", [])))
        col2.metric("Low Confidence", len(filter_results.get("low_confidence", [])))
        col3.metric("Suppressed", len(filter_results.get("suppressed", [])))
        col4.metric("Not Detected", len(filter_results.get("not_detected", [])))

        st.markdown(build_filter_markdown(filter_results, template_decisions))
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[5]:
    st.header("Equipment")
    equipment_records = st.session_state.equipment_records
    if equipment_records:
        equipment_rows = flatten_records(equipment_records)
        equipment_df = rows_to_dataframe(equipment_rows)

        type_counter = Counter(record.equipment_type for record in equipment_records)
        review_counter = sum(1 for record in equipment_records if record.review_required)

        col1, col2, col3 = st.columns(3)
        col1.metric("Equipment Rows", len(equipment_records))
        col2.metric("Equipment Types", len(type_counter))
        col3.metric("Review Required", review_counter)

        st.caption(f"Type mix: {_counter_markdown(type_counter)}")
        st.dataframe(equipment_df, width="stretch")
    else:
        st.info("No structured equipment records were extracted from the current document.")


with tabs[6]:
    st.header("Points")
    point_records = st.session_state.point_records
    merged_point_records = st.session_state.merged_point_records
    if point_records or merged_point_records:
        extracted_rows = flatten_records(point_records)
        merged_rows = flatten_records(merged_point_records)
        source_counter = Counter(record.source_type for record in merged_point_records)
        template_backfill_count = max(0, len(merged_point_records) - len(point_records))
        review_counter = sum(1 for record in merged_point_records if record.review_required)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Extracted Points", len(point_records))
        col2.metric("Final Points", len(merged_point_records))
        col3.metric("Template Backfill", template_backfill_count)
        col4.metric("Review Required", review_counter)

        st.caption(f"Source mix: {_counter_markdown(source_counter)}")

        if point_records:
            with st.expander(f"Source Points ({len(point_records)})", expanded=False):
                st.dataframe(rows_to_dataframe(extracted_rows), width="stretch")

        with st.expander(f"Final Points ({len(merged_point_records)})", expanded=True):
            st.dataframe(rows_to_dataframe(merged_rows), width="stretch")
    else:
        st.info("No structured points were extracted from the current document.")


with tabs[7]:
    st.header("Workflow Output")
    workflow_items = st.session_state.workflow_items
    parse_result = st.session_state.parse_result

    if parse_result and parse_result.get("status") == "ocr_required":
        st.info("Workflow output is intentionally limited because this upload needs OCR before source-confirmed extraction can proceed.")
    elif workflow_items:
        st.info(workflow_items.get("summary", ""))

        triggered_templates = workflow_items.get("triggered_templates", [])
        if triggered_templates:
            st.success(f"Triggered templates: {', '.join(triggered_templates)}")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Equipment Detected", len(workflow_items.get("source_equipment", [])))
        col2.metric("Points Generated", len(workflow_items.get("points", [])))
        col3.metric("RFI Items", len(workflow_items.get("rfis", [])))
        col4.metric("Field Verification", len(workflow_items.get("field_verifications", [])))
        col5.metric("Cx Tests", len(workflow_items.get("cx_items", [])))

        if workflow_items.get("points"):
            with st.expander(f"Points List Candidates ({len(workflow_items['points'])})", expanded=True):
                st.dataframe(workflow_items["points"], width="stretch")

        if workflow_items.get("rfis"):
            with st.expander(f"RFI Items ({len(workflow_items['rfis'])})"):
                for priority in ("High", "Medium", "Low"):
                    items = [item for item in workflow_items["rfis"] if item["priority"] == priority]
                    if items:
                        st.markdown(f"**{priority} Priority**")
                        for item in items:
                            st.markdown(f"- **{item['rfi_number']}** - {item['question']}")

        if workflow_items.get("field_verifications"):
            with st.expander(f"Field Verification Checklist ({len(workflow_items['field_verifications'])})"):
                categories = sorted({item["category"] for item in workflow_items["field_verifications"]})
                for category in categories:
                    st.markdown(f"**{category}**")
                    for item in workflow_items["field_verifications"]:
                        if item["category"] == category:
                            st.markdown(f"- [ ] {item['task']}")

        if workflow_items.get("cx_items"):
            with st.expander(f"Commissioning Checklist ({len(workflow_items['cx_items'])})"):
                st.dataframe(workflow_items["cx_items"], width="stretch")

        if workflow_items.get("cad_tasks"):
            with st.expander(f"CAD Tasks ({len(workflow_items['cad_tasks'])})"):
                for task in workflow_items["cad_tasks"]:
                    st.markdown(f"- {task}")

        if workflow_items.get("submittal_items"):
            with st.expander(f"Submittal Items ({len(workflow_items['submittal_items'])})"):
                for item in workflow_items["submittal_items"]:
                    st.markdown(f"- {item}")

        st.divider()
        st.subheader("Source-Confirmed Allowed Items")
        allowed = st.session_state.filter_results.get("allowed", [])
        if allowed:
            rows = [
                {
                    "Term": term.term,
                    "Category": term.category,
                    "Confidence": term.confidence,
                    "Status": term.status,
                }
                for term in allowed
            ]
            st.dataframe(rows, width="stretch")
        else:
            st.info("No items passed the workflow threshold.")
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[8]:
    st.header("Exports")
    if st.session_state.scored_terms:
        equipment_records = st.session_state.equipment_records
        point_records = st.session_state.point_records
        merged_point_records = st.session_state.merged_point_records

        equipment_rows = flatten_records(equipment_records)
        point_rows = flatten_records(merged_point_records)
        source_point_rows = flatten_records(point_records)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Structured JSON")
            st.download_button(
                label="Download Equipment (JSON)",
                data=json.dumps(_record_dicts(equipment_records), indent=2),
                file_name="specflow_equipment.json",
                mime="application/json",
            )
            st.download_button(
                label="Download Points (JSON)",
                data=json.dumps(_record_dicts(merged_point_records), indent=2),
                file_name="specflow_points.json",
                mime="application/json",
            )

        with col2:
            st.subheader("Structured CSV")
            st.download_button(
                label="Download Equipment (CSV)",
                data=rows_to_csv_bytes(equipment_rows),
                file_name="specflow_equipment.csv",
                mime="text/csv",
            )
            st.download_button(
                label="Download Points (CSV)",
                data=rows_to_csv_bytes(point_rows),
                file_name="specflow_points.csv",
                mime="text/csv",
            )

        with col3:
            st.subheader("Workbook")
            workbook_bytes = tables_to_xlsx_bytes(
                {
                    "Equipment": equipment_rows,
                    "Points": point_rows,
                    "SourcePoints": source_point_rows,
                }
            )
            st.download_button(
                label="Download Equipment + Points (XLSX)",
                data=workbook_bytes,
                file_name="specflow_equipment_points.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.divider()

        col4, col5 = st.columns(2)
        with col4:
            st.subheader("Detection Matrix")
            matrix_json = json.dumps(build_json_matrix(st.session_state.scored_terms), indent=2)
            st.download_button(
                label="Download Detection Matrix (JSON)",
                data=matrix_json,
                file_name="specflow_detection_matrix.json",
                mime="application/json",
            )
            st.download_button(
                label="Download Detection Matrix (Markdown)",
                data=build_markdown_matrix(st.session_state.scored_terms, mode="workflow"),
                file_name="specflow_detection_matrix.md",
                mime="text/markdown",
            )
            st.download_button(
                label="Download Filtering Summary (Markdown)",
                data=build_filter_markdown(
                    st.session_state.filter_results,
                    st.session_state.template_decisions,
                ),
                file_name="specflow_filtering_summary.md",
                mime="text/markdown",
            )

        with col5:
            st.subheader("Workflow Items")
            workflow_items = st.session_state.workflow_items
            if workflow_items:
                st.download_button(
                    label="Download Workflow Items (JSON)",
                    data=json.dumps(workflow_items, indent=2),
                    file_name="specflow_workflow_items.json",
                    mime="application/json",
                )
                st.download_button(
                    label="Download Workflow Report (Markdown)",
                    data=_workflow_report_markdown(workflow_items),
                    file_name="specflow_workflow_report.md",
                    mime="text/markdown",
                )
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")


with tabs[9]:
    st.header("About SpecFlow AI")
    st.markdown(
        """
**SpecFlow AI** converts engineering documents into clean AI-agent-ready Markdown,
then uses a BMS/ICS/PLC knowledge base and source-confirmed confidence scoring to generate
structured equipment records, points lists, RFIs, field verification checklists, CAD tasks,
submittal items, and commissioning checklists.

**Core rule:**
> Known vocabulary is not the same as detected vocabulary.
> The source document must support every output item.

---

**Confidence thresholds**

| Output Type | Minimum Confidence |
|---|---:|
| Equipment template | 0.70 |
| Points list | 0.70 |
| RFI candidate | 0.60 |
| Field verification | 0.50 |
| CAD task | 0.60 |
| Submittal item | 0.60 |
| Commissioning item | 0.65 |

---

**Supported document types**

| Format | Parser | Notes |
|---|---|---|
| PDF (text-based) | Firecrawl pdf-inspector (Node.js) | Rust-powered, fast |
| PDF (scanned) | OCR fallback | OCR text is reviewed separately |
| DOCX | python-docx | Headings, tables, lists |
| Excel (.xlsx) | openpyxl | Sheet-per-table Markdown |
| Pasted text | Direct input | Any plain text or Markdown |

---

**Structured outputs**

- Equipment records with nested HVAC/BMS attributes
- Extracted source points mapped to equipment tags
- Final points list with template fallback rows clearly labeled
- Confidence bands and review-required flags per row

**Stack:** Python · Streamlit · Firecrawl pdf-inspector · python-docx · openpyxl · Pydantic

**Knowledge base:** `knowledge_base/bms_ics_plc_terms.md`

**Version:** v0.5.0
"""
    )
