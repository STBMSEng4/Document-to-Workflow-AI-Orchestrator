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

from app.exporters import (
    equipment_records_to_markdown,
    flatten_records,
    point_records_to_markdown,
    rows_to_csv_bytes,
    rows_to_dataframe,
    soo_records_to_markdown,
    tables_to_xlsx_bytes,
)
from app.extractors.equipment_extractor import extract_equipment_records
from app.extractors.points_list_extractor import extract_point_records
from app.extractors.soo_extractor import extract_soo_records
from app.extractors.template_fallback_merge import (
    export_point_records,
    merge_point_records_with_template_defaults,
)
from app.extractors.workflow_extractor import extract_workflow_items
from app.normalizers.markdown_normalizer import normalize_text
from app.normalizers.term_normalizer import get_term_list
from app.parsers.doc_parser import parse_doc_to_markdown
from app.parsers.docx_parser import parse_docx_to_markdown
from app.parsers.excel_parser import parse_tabular_to_markdown
from app.parsers.ocr_gate import ocr_quality
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
        "Upload",
        "Inspection",
        "Raw Markdown",
        "Equipment",
        "I/O List",
        "SOO",
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
    "soo_records": [],
    "matrix_mode": "workflow",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with tabs[0]:
    st.header("Upload")

    input_mode = st.radio(
        "Input mode",
        ["Upload document", "Paste text / Markdown"],
        horizontal=True,
    )

    uploaded_file = None
    pasted_text = ""

    if input_mode == "Upload document":
        uploaded_file = st.file_uploader(
            "Upload PDF, Word (.docx / .doc), Excel, or CSV",
            type=["pdf", "docx", "doc", "xlsx", "xls", "csv"],
            help="SpecFlow supports PDF, Word (.docx and legacy .doc), Excel (.xlsx/.xls), and CSV. Legacy .doc requires antiword in the runtime environment.",
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
                elif suffix == ".doc":
                    result = parse_doc_to_markdown(tmp_path)
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
            soo_records = extract_soo_records(normalized)

            st.session_state.equipment_records = equipment_records
            st.session_state.point_records = point_records
            st.session_state.merged_point_records = merged_point_records
            st.session_state.soo_records = soo_records

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
    st.header("Document Inspection")
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
    st.header("Equipment")
    _ocr_level, _ocr_msg = ocr_quality(st.session_state.parse_result)
    if _ocr_level == "blocked":
        st.error(f"⛔ Extraction blocked — {_ocr_msg}")
    elif _ocr_level == "warn":
        st.warning(f"⚠️ OCR applied — {_ocr_msg}")
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


with tabs[4]:
    st.header("I/O List")
    _ocr_level, _ocr_msg = ocr_quality(st.session_state.parse_result)
    if _ocr_level == "blocked":
        st.error(f"⛔ Extraction blocked — {_ocr_msg}")
    elif _ocr_level == "warn":
        st.warning(f"⚠️ OCR applied — {_ocr_msg}")
    point_records = st.session_state.point_records
    merged_point_records = st.session_state.merged_point_records
    if point_records or merged_point_records:
        extracted_rows = flatten_records(point_records)
        merged_rows = flatten_records(merged_point_records)
        source_counter = Counter(record.source_type for record in merged_point_records)
        template_backfill_count = sum(
            1 for r in merged_point_records if r.source_type == "template_default"
        )
        template_only_count = sum(
            1 for r in merged_point_records if r.source_type == "template_only"
        )
        review_counter = sum(1 for record in merged_point_records if record.review_required)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Extracted Points", len(point_records))
        col2.metric("Template Backfill", template_backfill_count)
        col3.metric("Unconfirmed (excluded)", template_only_count)
        col4.metric("Review Required", review_counter)

        st.caption(f"Source mix: {_counter_markdown(source_counter)}")
        if template_only_count:
            st.info(
                f"{template_only_count} template row(s) are shown below but marked "
                f"**template_only** — their equipment type was not source-confirmed at ≥ 0.70 "
                "and they are excluded from primary exports."
            )

        if point_records:
            with st.expander(f"Source Points ({len(point_records)})", expanded=False):
                st.dataframe(rows_to_dataframe(extracted_rows), width="stretch")

        with st.expander(f"Final Points ({len(merged_point_records)})", expanded=True):
            st.dataframe(rows_to_dataframe(merged_rows), width="stretch")
    else:
        st.info("No structured points were extracted from the current document.")


with tabs[5]:
    st.header("SOO")
    _ocr_level, _ocr_msg = ocr_quality(st.session_state.parse_result)
    if _ocr_level == "blocked":
        st.error(f"⛔ Extraction blocked — {_ocr_msg}")
    elif _ocr_level == "warn":
        st.warning(f"⚠️ OCR applied — {_ocr_msg}")
    soo_records = st.session_state.soo_records
    if soo_records:
        mode_counter = Counter(record.mode for record in soo_records)
        safety_count = sum(1 for record in soo_records if record.safety_critical)
        review_count = sum(1 for record in soo_records if record.review_required)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("SOO Steps", len(soo_records))
        col2.metric("Modes", len(mode_counter))
        col3.metric("Safety Critical", safety_count)
        col4.metric("Review Required", review_count)

        st.caption(f"Mode mix: {_counter_markdown(mode_counter)}")
        soo_df_rows = flatten_records(soo_records)
        st.dataframe(rows_to_dataframe(soo_df_rows), use_container_width=True)
    else:
        st.info("No sequence of operations content was extracted from the current document.")


with tabs[6]:
    st.header("Exports")
    if not st.session_state.scored_terms:
        st.info("Run SpecFlow AI on the Upload tab first.")
    else:
        _ocr_level, _ocr_msg = ocr_quality(st.session_state.parse_result)
        _exports_blocked = _ocr_level == "blocked"
        if _exports_blocked:
            st.error(f"⛔ Exports blocked — {_ocr_msg}")
        elif _ocr_level == "warn":
            st.warning(f"⚠️ OCR applied — downloads are available but review all outputs before use. {_ocr_msg}")

        equipment_records = st.session_state.equipment_records
        merged_point_records = st.session_state.merged_point_records
        soo_records = st.session_state.soo_records
        point_records = st.session_state.point_records

        equipment_rows = flatten_records(equipment_records)
        # template_only rows are visible in the I/O List tab but excluded here
        io_export_records = export_point_records(merged_point_records)
        io_rows = flatten_records(io_export_records)
        soo_rows = flatten_records(soo_records)
        source_point_rows = flatten_records(point_records)

        # ── Primary deliverables ─────────────────────────────────────────────
        st.subheader("Primary Deliverables")
        st.caption("Equipment schedule, I/O list, and sequence of operations — the three core outputs.")

        col_eq, col_io, col_soo = st.columns(3)

        with col_eq:
            st.markdown("**Equipment**")
            st.download_button(
                "equipment.csv",
                data=rows_to_csv_bytes(equipment_rows),
                file_name="equipment.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=_exports_blocked,
            )
            st.download_button(
                "equipment.json",
                data=json.dumps(_record_dicts(equipment_records), indent=2),
                file_name="equipment.json",
                mime="application/json",
                use_container_width=True,
                disabled=_exports_blocked,
            )
            st.download_button(
                "equipment.md",
                data=equipment_records_to_markdown(equipment_records),
                file_name="equipment.md",
                mime="text/markdown",
                use_container_width=True,
                disabled=_exports_blocked,
            )

        with col_io:
            st.markdown("**I/O List**")
            st.download_button(
                "io_list.csv",
                data=rows_to_csv_bytes(io_rows),
                file_name="io_list.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=_exports_blocked,
            )
            st.download_button(
                "io_list.json",
                data=json.dumps(_record_dicts(io_export_records), indent=2),
                file_name="io_list.json",
                mime="application/json",
                use_container_width=True,
                disabled=_exports_blocked,
            )
            st.download_button(
                "io_list.md",
                data=point_records_to_markdown(merged_point_records),
                file_name="io_list.md",
                mime="text/markdown",
                use_container_width=True,
                disabled=_exports_blocked,
            )

        with col_soo:
            st.markdown("**Sequence of Operations**")
            if soo_records:
                st.download_button(
                    "soo.csv",
                    data=rows_to_csv_bytes(soo_rows),
                    file_name="soo.csv",
                    mime="text/csv",
                    use_container_width=True,
                    disabled=_exports_blocked,
                )
                st.download_button(
                    "soo.json",
                    data=json.dumps(_record_dicts(soo_records), indent=2),
                    file_name="soo.json",
                    mime="application/json",
                    use_container_width=True,
                    disabled=_exports_blocked,
                )
                st.download_button(
                    "soo.md",
                    data=soo_records_to_markdown(soo_records),
                    file_name="soo.md",
                    mime="text/markdown",
                    use_container_width=True,
                    disabled=_exports_blocked,
                )
            else:
                st.caption("No SOO content detected in this document.")

        st.divider()

        # ── Combined workbook ────────────────────────────────────────────────
        st.subheader("Combined Workbook")
        workbook_sheets: dict[str, list] = {"Equipment": equipment_rows, "IO_List": io_rows}
        if soo_rows:
            workbook_sheets["SOO"] = soo_rows
        if source_point_rows:
            workbook_sheets["IO_Source"] = source_point_rows

        st.download_button(
            "specflow_all.xlsx  (Equipment + I/O List + SOO)",
            data=tables_to_xlsx_bytes(workbook_sheets),
            file_name="specflow_all.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            disabled=_exports_blocked,
        )

        st.divider()

        # ── Debug / Advanced ────────────────────────────────────────────────
        with st.expander("Debug / Advanced"):
            st.caption("Detection matrix, filtering summary, and workflow bundle — for internal review and troubleshooting.")

            # Detection Matrix display + downloads
            st.markdown("### Detection Matrix")
            if st.session_state.scored_terms:
                _dm_mode = st.session_state.get("matrix_mode", "workflow")
                _confirmed = [t for t in st.session_state.scored_terms if t.source_confirmed]
                _not_detected = [t for t in st.session_state.scored_terms if not t.source_confirmed]
                _dm_c1, _dm_c2, _dm_c3 = st.columns(3)
                _dm_c1.metric("Total KB Terms", len(st.session_state.scored_terms))
                _dm_c2.metric("Source Confirmed", len(_confirmed))
                _dm_c3.metric("Not Detected (0.00)", len(_not_detected))
                st.markdown(build_markdown_matrix(st.session_state.scored_terms, mode=_dm_mode))
                col_dm1, col_dm2 = st.columns(2)
                col_dm1.download_button(
                    "detection_matrix.json",
                    data=json.dumps(build_json_matrix(st.session_state.scored_terms), indent=2),
                    file_name="detection_matrix.json",
                    mime="application/json",
                )
                col_dm2.download_button(
                    "detection_matrix.md",
                    data=build_markdown_matrix(st.session_state.scored_terms, mode="workflow"),
                    file_name="detection_matrix.md",
                    mime="text/markdown",
                )
            else:
                st.caption("No scored terms — run SpecFlow AI first.")

            st.divider()

            # Filtering Summary display + download
            st.markdown("### Filtering Summary")
            if st.session_state.filter_results:
                _fr = st.session_state.filter_results
                _td = st.session_state.template_decisions
                _fs_c1, _fs_c2, _fs_c3, _fs_c4 = st.columns(4)
                _fs_c1.metric("Allowed", len(_fr.get("allowed", [])))
                _fs_c2.metric("Low Confidence", len(_fr.get("low_confidence", [])))
                _fs_c3.metric("Suppressed", len(_fr.get("suppressed", [])))
                _fs_c4.metric("Not Detected", len(_fr.get("not_detected", [])))
                st.markdown(build_filter_markdown(_fr, _td))
                st.download_button(
                    "filtering_summary.md",
                    data=build_filter_markdown(_fr, _td),
                    file_name="filtering_summary.md",
                    mime="text/markdown",
                )
            else:
                st.caption("No filter results — run SpecFlow AI first.")

            st.divider()

            # Workflow Output display + downloads
            st.markdown("### Workflow Output")
            _wf = st.session_state.workflow_items
            if _wf:
                st.caption(_wf.get("summary", ""))
                _triggered = _wf.get("triggered_templates", [])
                if _triggered:
                    st.success(f"Triggered templates: {', '.join(_triggered)}")

                _wf_c1, _wf_c2, _wf_c3, _wf_c4, _wf_c5 = st.columns(5)
                _wf_c1.metric("Equipment", len(_wf.get("source_equipment", [])))
                _wf_c2.metric("Points", len(_wf.get("points", [])))
                _wf_c3.metric("RFIs", len(_wf.get("rfis", [])))
                _wf_c4.metric("Field Checks", len(_wf.get("field_verifications", [])))
                _wf_c5.metric("Cx Tests", len(_wf.get("cx_items", [])))

                if _wf.get("rfis"):
                    with st.expander(f"RFI Items ({len(_wf['rfis'])})"):
                        for _priority in ("High", "Medium", "Low"):
                            _pitems = [i for i in _wf["rfis"] if i["priority"] == _priority]
                            if _pitems:
                                st.markdown(f"**{_priority} Priority**")
                                for _item in _pitems:
                                    st.markdown(f"- **{_item['rfi_number']}** — {_item['question']}")

                if _wf.get("field_verifications"):
                    with st.expander(f"Field Verification ({len(_wf['field_verifications'])})"):
                        for _cat in sorted({i["category"] for i in _wf["field_verifications"]}):
                            st.markdown(f"**{_cat}**")
                            for _item in _wf["field_verifications"]:
                                if _item["category"] == _cat:
                                    st.markdown(f"- [ ] {_item['task']}")

                if _wf.get("cx_items"):
                    with st.expander(f"Commissioning Checklist ({len(_wf['cx_items'])})"):
                        st.dataframe(_wf["cx_items"], use_container_width=True)

                if _wf.get("cad_tasks"):
                    with st.expander(f"CAD Tasks ({len(_wf['cad_tasks'])})"):
                        for _task in _wf["cad_tasks"]:
                            st.markdown(f"- {_task}")

                if _wf.get("submittal_items"):
                    with st.expander(f"Submittal Items ({len(_wf['submittal_items'])})"):
                        for _item in _wf["submittal_items"]:
                            st.markdown(f"- {_item}")

                st.markdown("**Downloads**")
                col_wb1, col_wb2 = st.columns(2)
                col_wb1.download_button(
                    "workflow_items.json",
                    data=json.dumps(_wf, indent=2),
                    file_name="workflow_items.json",
                    mime="application/json",
                )
                col_wb2.download_button(
                    "workflow_report.md",
                    data=_workflow_report_markdown(_wf),
                    file_name="workflow_report.md",
                    mime="text/markdown",
                )
            else:
                st.caption("No workflow items generated.")


with tabs[7]:
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
| DOC (legacy) | antiword | Word 97-2003 binary format; requires antiword in runtime |
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
