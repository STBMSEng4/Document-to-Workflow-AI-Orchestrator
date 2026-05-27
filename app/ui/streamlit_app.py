"""SpecFlow AI — Streamlit MVP UI."""

import sys
import json
import tempfile
from pathlib import Path

import streamlit as st

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parents[2]))

from app.parsers.pdf_inspector_parser import inspect_pdf
from app.parsers.docx_parser import parse_docx_to_markdown
from app.parsers.excel_parser import parse_excel_to_markdown
from app.normalizers.markdown_normalizer import normalize_text, build_frontmatter
from app.normalizers.term_normalizer import get_term_list
from app.scoring.confidence_scorer import score_all_terms
from app.scoring.detection_matrix import build_markdown_matrix, build_json_matrix
from app.scoring.filter_engine import apply_filters, evaluate_template_triggers, build_filter_markdown
from app.extractors.workflow_extractor import extract_workflow_items
from app.exporters.markdown_exporter import export_markdown_report
from app.exporters.json_exporter import export_to_json

st.set_page_config(page_title="SpecFlow AI", layout="wide")

st.title("SpecFlow AI")
st.caption("Document-to-Workflow AI Orchestrator for BMS / HVAC Controls / ICS / PLC")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Upload / Ingest",
    "PDF / Doc Inspection",
    "Raw Markdown",
    "Detection Matrix",
    "Filtering Summary",
    "Workflow Output",
    "Exports",
    "About",
])

# ── Session state ─────────────────────────────────────────────────────────────
for key in ("parse_result", "source_text", "scored_terms", "filter_results",
            "template_decisions", "workflow_items", "matrix_mode"):
    if key not in st.session_state:
        st.session_state[key] = None if key not in ("scored_terms",) else []

if "filter_results" not in st.session_state or st.session_state.filter_results is None:
    st.session_state.filter_results = {}
if "template_decisions" not in st.session_state or st.session_state.template_decisions is None:
    st.session_state.template_decisions = []
if "workflow_items" not in st.session_state or st.session_state.workflow_items is None:
    st.session_state.workflow_items = {}

# ── Tab 0: Upload / Ingest ────────────────────────────────────────────────────
with tabs[0]:
    st.header("Upload / Ingest")

    input_mode = st.radio(
        "Input mode",
        ["Upload PDF", "Upload DOCX", "Upload Excel (.xlsx)", "Paste text / Markdown"],
        horizontal=True,
    )

    uploaded_file = None
    pasted_text = ""

    if input_mode in ("Upload PDF", "Upload DOCX", "Upload Excel (.xlsx)"):
        ext_map = {
            "Upload PDF": ["pdf"],
            "Upload DOCX": ["docx"],
            "Upload Excel (.xlsx)": ["xlsx", "xls"],
        }
        uploaded_file = st.file_uploader(
            f"Upload a {input_mode.replace('Upload ', '')} file",
            type=ext_map[input_mode],
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
        with st.spinner("Ingesting and scoring..."):

            # ── Parse ──────────────────────────────────────────────────────────
            if input_mode == "Upload PDF" and uploaded_file:
                suffix = ".pdf"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                result = inspect_pdf(tmp_path)

            elif input_mode == "Upload DOCX" and uploaded_file:
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                result = parse_docx_to_markdown(tmp_path)

            elif input_mode == "Upload Excel (.xlsx)" and uploaded_file:
                suffix = ".xlsx" if uploaded_file.name.endswith("xlsx") else ".xls"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                result = parse_excel_to_markdown(tmp_path)

            else:
                # Pasted text fallback
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
            raw_md = result.get("raw_markdown", "")

            # ── Normalise / Score / Filter ─────────────────────────────────────
            normalized = normalize_text(raw_md)
            st.session_state.source_text = normalized

            kb_terms = get_term_list()
            scored = score_all_terms(kb_terms, normalized)
            st.session_state.scored_terms = scored

            filter_results = apply_filters(scored)
            st.session_state.filter_results = filter_results

            template_decisions = evaluate_template_triggers(scored)
            st.session_state.template_decisions = template_decisions

            # ── Workflow extraction ────────────────────────────────────────────
            workflow_items = extract_workflow_items(
                normalized,
                scored_terms=scored,
                template_decisions=template_decisions,
            )
            st.session_state.workflow_items = workflow_items

        if result.get("status") == "ocr_required":
            st.warning("Document parsed as scanned/image-heavy. OCR is required before workflow extraction will be useful.")
        elif result.get("status") == "failed":
            st.error("Parse failed. Check the inspection tab and parser warnings for details.")
        else:
            st.success("Done. Use the tabs above to explore results.")

        if result.get("errors"):
            for err in result["errors"]:
                st.warning(err)

# ── Tab 1: PDF / Doc Inspection ───────────────────────────────────────────────
with tabs[1]:
    st.header("Document Inspection Results")
    r = st.session_state.parse_result
    if r:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Source Type", r.get("source_type", "—").upper())
        col2.metric("Classification", r.get("pdf_classification", "—"))
        col3.metric("Status", r.get("status", "—"))
        col4.metric("OCR Required", str(r.get("ocr_required", False)))

        if r.get("errors"):
            for e in r["errors"]:
                st.warning(e)

        if r.get("status") == "ocr_required":
            st.info(
                "This document looks scanned or image-heavy. SpecFlow did not find enough embedded text to build a useful workflow package yet."
            )
            pages_needing_ocr = (r.get("metadata") or {}).get("pages_needing_ocr", [])
            if pages_needing_ocr:
                st.markdown(f"**Pages needing OCR:** {', '.join(str(p) for p in pages_needing_ocr)}")
        elif r.get("status") == "failed":
            st.error("SpecFlow could not extract usable Markdown from this file.")

        meta = r.get("metadata", {})
        if meta:
            st.subheader("File Metadata")
            st.json(meta)
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 2: Raw Markdown ───────────────────────────────────────────────────────
with tabs[2]:
    st.header("Raw / Normalized Markdown")
    if st.session_state.source_text:
        st.markdown(f"**Character count:** {len(st.session_state.source_text):,}")
        st.text_area("Normalized Markdown", st.session_state.source_text, height=500)
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 3: Detection Matrix ───────────────────────────────────────────────────
with tabs[3]:
    st.header("Detection Matrix")
    if st.session_state.scored_terms:
        mode = st.session_state.get("matrix_mode", "workflow")
        md_matrix = build_markdown_matrix(st.session_state.scored_terms, mode=mode)
        st.markdown(md_matrix)

        confirmed = [t for t in st.session_state.scored_terms if t.source_confirmed]
        not_detected = [t for t in st.session_state.scored_terms if not t.source_confirmed]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total KB Terms", len(st.session_state.scored_terms))
        c2.metric("Source Confirmed", len(confirmed))
        c3.metric("Not Detected (0.00)", len(not_detected))
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 4: Filtering Summary ──────────────────────────────────────────────────
with tabs[4]:
    st.header("Filtering Summary")
    if st.session_state.filter_results:
        fr = st.session_state.filter_results
        td = st.session_state.template_decisions

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Allowed", len(fr.get("allowed", [])))
        col2.metric("Low Confidence", len(fr.get("low_confidence", [])))
        col3.metric("Suppressed", len(fr.get("suppressed", [])))
        col4.metric("Not Detected", len(fr.get("not_detected", [])))

        st.markdown(build_filter_markdown(fr, td))
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 5: Workflow Output ────────────────────────────────────────────────────
with tabs[5]:
    st.header("Workflow Output")
    wi = st.session_state.workflow_items
    parse_result = st.session_state.parse_result

    if parse_result and parse_result.get("status") == "ocr_required":
        st.info("Workflow output is intentionally limited because this upload needs OCR before source-confirmed extraction can proceed.")
    elif wi:
        # Summary
        st.info(wi.get("summary", ""))

        triggered_tmpls = wi.get("triggered_templates", [])
        if triggered_tmpls:
            st.success(f"Triggered templates: {', '.join(triggered_tmpls)}")

        eq_list = wi.get("source_equipment", [])
        proto_list = wi.get("source_protocols", [])
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Equipment Detected", len(eq_list))
        c2.metric("Points Generated", len(wi.get("points", [])))
        c3.metric("RFI Items", len(wi.get("rfis", [])))
        c4.metric("Field Verification", len(wi.get("field_verifications", [])))
        c5.metric("Cx Tests", len(wi.get("cx_items", [])))

        # ── Points list ───────────────────────────────────────────────────────
        if wi.get("points"):
            with st.expander(f"📋 Points List Candidates ({len(wi['points'])})", expanded=True):
                st.dataframe(wi["points"], use_container_width=True)

        # ── RFIs ─────────────────────────────────────────────────────────────
        if wi.get("rfis"):
            with st.expander(f"❓ RFI Items ({len(wi['rfis'])})"):
                high = [r for r in wi["rfis"] if r["priority"] == "High"]
                med  = [r for r in wi["rfis"] if r["priority"] == "Medium"]
                low  = [r for r in wi["rfis"] if r["priority"] == "Low"]
                for bucket, label in ((high, "🔴 High Priority"), (med, "🟡 Medium Priority"), (low, "⚪ Low Priority")):
                    if bucket:
                        st.markdown(f"**{label}**")
                        for r in bucket:
                            st.markdown(f"- **{r['rfi_number']}** — {r['question']}")

        # ── Field Verification ────────────────────────────────────────────────
        if wi.get("field_verifications"):
            with st.expander(f"🔧 Field Verification Checklist ({len(wi['field_verifications'])})"):
                categories = sorted({fv["category"] for fv in wi["field_verifications"]})
                for cat in categories:
                    items = [fv for fv in wi["field_verifications"] if fv["category"] == cat]
                    st.markdown(f"**{cat}**")
                    for fv in items:
                        st.markdown(f"- [ ] {fv['task']}")

        # ── Commissioning ─────────────────────────────────────────────────────
        if wi.get("cx_items"):
            with st.expander(f"✅ Commissioning Checklist ({len(wi['cx_items'])})"):
                st.dataframe(wi["cx_items"], use_container_width=True)

        # ── CAD Tasks ─────────────────────────────────────────────────────────
        if wi.get("cad_tasks"):
            with st.expander(f"📐 CAD Tasks ({len(wi['cad_tasks'])})"):
                for task in wi["cad_tasks"]:
                    st.markdown(f"- {task}")

        # ── Submittal Items ───────────────────────────────────────────────────
        if wi.get("submittal_items"):
            with st.expander(f"📦 Submittal Items ({len(wi['submittal_items'])})"):
                for item in wi["submittal_items"]:
                    st.markdown(f"- {item}")

        # ── Allowed workflow items (detection table) ──────────────────────────
        st.divider()
        st.subheader("Source-Confirmed Allowed Items")
        allowed = st.session_state.filter_results.get("allowed", [])
        if allowed:
            rows = [
                {"Term": t.term, "Category": t.category, "Confidence": t.confidence, "Status": t.status}
                for t in allowed
            ]
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No items passed the workflow threshold.")

    elif st.session_state.template_decisions:
        # Old path: template decisions exist but workflow_items not populated yet
        triggered = [d for d in st.session_state.template_decisions if d["triggered"]]
        if triggered:
            for tmpl in triggered:
                st.subheader(f"✅ {tmpl['template_name']} (confidence {tmpl['confidence']:.2f})")
                if tmpl.get("human_review_required"):
                    st.warning("Human review recommended for this template.")
                for section in tmpl.get("output_sections", []):
                    st.markdown(f"- {section}")
        else:
            st.info("No templates triggered. Source document may not contain confirmed equipment or controls scope above threshold.")
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 6: Exports ────────────────────────────────────────────────────────────
with tabs[6]:
    st.header("Exports")
    if st.session_state.scored_terms:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Detection Matrix")
            json_data = build_json_matrix(st.session_state.scored_terms)
            json_str = json.dumps(json_data, indent=2)
            st.download_button(
                label="Download Detection Matrix (JSON)",
                data=json_str,
                file_name="specflow_detection_matrix.json",
                mime="application/json",
            )
            md_out = build_markdown_matrix(st.session_state.scored_terms, mode="workflow")
            st.download_button(
                label="Download Detection Matrix (Markdown)",
                data=md_out,
                file_name="specflow_detection_matrix.md",
                mime="text/markdown",
            )
            filter_md = build_filter_markdown(
                st.session_state.filter_results,
                st.session_state.template_decisions,
            )
            st.download_button(
                label="Download Filtering Summary (Markdown)",
                data=filter_md,
                file_name="specflow_filtering_summary.md",
                mime="text/markdown",
            )

        with col2:
            st.subheader("Workflow Items")
            wi = st.session_state.workflow_items
            if wi:
                wi_json = json.dumps(wi, indent=2)
                st.download_button(
                    label="Download Workflow Items (JSON)",
                    data=wi_json,
                    file_name="specflow_workflow_items.json",
                    mime="application/json",
                )

                # Build a combined Markdown report
                report_lines = [f"# SpecFlow AI — Workflow Report\n"]
                report_lines.append(f"**Summary:** {wi.get('summary', '')}\n")

                if wi.get("points"):
                    report_lines.append("## Points List Candidates\n")
                    report_lines.append("| Equipment | Point Name | Abbr | I/O | Unit | Description |")
                    report_lines.append("|---|---|---|---|---|---|")
                    for p in wi["points"]:
                        report_lines.append(
                            f"| {p['equipment']} | {p['point_name']} | {p['abbreviation']} "
                            f"| {p['io_type']} | {p['engineering_unit']} | {p['description']} |"
                        )
                    report_lines.append("")

                if wi.get("rfis"):
                    report_lines.append("## RFI Items\n")
                    for r in wi["rfis"]:
                        report_lines.append(f"- **{r['rfi_number']}** [{r['priority']}] {r['question']}")
                    report_lines.append("")

                if wi.get("field_verifications"):
                    report_lines.append("## Field Verification Checklist\n")
                    for fv in wi["field_verifications"]:
                        report_lines.append(f"- [ ] [{fv['category']}] {fv['task']}")
                    report_lines.append("")

                if wi.get("cx_items"):
                    report_lines.append("## Commissioning Checklist\n")
                    for c in wi["cx_items"]:
                        report_lines.append(f"- **{c['test_name']}** ({c['category']}): {c['description']}")
                    report_lines.append("")

                if wi.get("cad_tasks"):
                    report_lines.append("## CAD Tasks\n")
                    for t in wi["cad_tasks"]:
                        report_lines.append(f"- {t}")
                    report_lines.append("")

                if wi.get("submittal_items"):
                    report_lines.append("## Submittal Items\n")
                    for s in wi["submittal_items"]:
                        report_lines.append(f"- {s}")

                report_md = "\n".join(report_lines)
                st.download_button(
                    label="Download Workflow Report (Markdown)",
                    data=report_md,
                    file_name="specflow_workflow_report.md",
                    mime="text/markdown",
                )
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 7: About ──────────────────────────────────────────────────────────────
with tabs[7]:
    st.header("About SpecFlow AI")
    st.markdown("""
**SpecFlow AI** converts engineering documents into clean AI-agent-ready Markdown,
then uses a BMS/ICS/PLC knowledge base and source-confirmed confidence scoring to generate
points-list candidates, RFIs, field verification checklists, CAD tasks, submittal items,
and commissioning checklists — outputting only what the source document actually confirms.

**Core rule:**
> Known vocabulary is not the same as detected vocabulary.
> The source document must support every output item.

---

**Confidence thresholds:**

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

**Supported document types:**

| Format | Parser | Notes |
|---|---|---|
| PDF (text-based) | Firecrawl pdf-inspector (Node.js) | Rust-powered, fast |
| PDF (scanned) | OCR required — flagged in output | |
| DOCX | python-docx | Headings, tables, lists |
| Excel (.xlsx) | openpyxl | Sheet-per-table Markdown |
| Pasted text | Direct input | Any plain text or Markdown |

---

**Stack:** Python · Streamlit · Firecrawl pdf-inspector · python-docx · openpyxl · Source-confirmed filtering

**Knowledge base:** `knowledge_base/bms_ics_plc_terms.md` — table-driven, 270+ terms, 14 categories.
Add a row to the MD table → scorer picks it up automatically. No code changes needed.

**Deployment:** Docker container on Michael LXC (BAAL-PRXMX). Team access via Tailscale browser.

**Version:** v0.4.0
""")
