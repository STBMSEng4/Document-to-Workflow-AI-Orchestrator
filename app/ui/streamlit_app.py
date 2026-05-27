"""SpecFlow AI — Streamlit MVP UI."""

import sys
import json
import tempfile
from pathlib import Path

import streamlit as st

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parents[2]))

from app.parsers.pdf_inspector_parser import inspect_pdf
from app.normalizers.markdown_normalizer import normalize_text, build_frontmatter
from app.normalizers.term_normalizer import get_term_list
from app.scoring.confidence_scorer import score_all_terms
from app.scoring.detection_matrix import build_markdown_matrix, build_json_matrix
from app.scoring.filter_engine import apply_filters, evaluate_template_triggers, build_filter_markdown
from app.exporters.markdown_exporter import export_markdown_report
from app.exporters.json_exporter import export_to_json

st.set_page_config(page_title="SpecFlow AI", layout="wide")

st.title("SpecFlow AI")
st.caption("Document-to-Workflow AI Orchestrator for BMS / HVAC Controls / ICS")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Upload / Ingest",
    "PDF Inspection",
    "Raw Markdown",
    "Detection Matrix",
    "Filtering Summary",
    "Workflow Output",
    "Exports",
    "About",
])

# ── Session state ─────────────────────────────────────────────────────────────
if "parse_result" not in st.session_state:
    st.session_state.parse_result = None
if "source_text" not in st.session_state:
    st.session_state.source_text = ""
if "scored_terms" not in st.session_state:
    st.session_state.scored_terms = []
if "filter_results" not in st.session_state:
    st.session_state.filter_results = {}
if "template_decisions" not in st.session_state:
    st.session_state.template_decisions = []

# ── Tab 0: Upload / Ingest ────────────────────────────────────────────────────
with tabs[0]:
    st.header("Upload / Ingest")

    input_mode = st.radio("Input mode", ["Upload PDF", "Paste text / Markdown"], horizontal=True)

    uploaded_file = None
    pasted_text = ""

    if input_mode == "Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
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
            if input_mode == "Upload PDF" and uploaded_file:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                result = inspect_pdf(tmp_path)
                st.session_state.parse_result = result
                raw_md = result.get("raw_markdown", "")
            else:
                raw_md = pasted_text
                st.session_state.parse_result = {
                    "source_file": "pasted_text",
                    "pdf_classification": "text_input",
                    "raw_markdown": raw_md,
                    "ocr_required": False,
                    "status": "success",
                    "errors": [],
                    "metadata": {},
                }

            normalized = normalize_text(raw_md)
            st.session_state.source_text = normalized

            kb_terms = get_term_list()
            scored = score_all_terms(kb_terms, normalized)
            st.session_state.scored_terms = scored

            filter_results = apply_filters(scored)
            st.session_state.filter_results = filter_results

            template_decisions = evaluate_template_triggers(scored)
            st.session_state.template_decisions = template_decisions

        st.success("Done. Use the tabs above to explore results.")

# ── Tab 1: PDF Inspection ─────────────────────────────────────────────────────
with tabs[1]:
    st.header("PDF Inspection Results")
    r = st.session_state.parse_result
    if r:
        col1, col2, col3 = st.columns(3)
        col1.metric("Classification", r.get("pdf_classification", "—"))
        col2.metric("Status", r.get("status", "—"))
        col3.metric("OCR Required", str(r.get("ocr_required", False)))

        if r.get("errors"):
            st.error("Errors: " + " | ".join(r["errors"]))

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
    if st.session_state.template_decisions:
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

        st.divider()
        st.subheader("Allowed Workflow Items")
        allowed = st.session_state.filter_results.get("allowed", [])
        if allowed:
            rows = [{"Term": t.term, "Category": t.category, "Confidence": t.confidence, "Status": t.status} for t in allowed]
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No items passed the workflow threshold.")
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 6: Exports ────────────────────────────────────────────────────────────
with tabs[6]:
    st.header("Exports")
    if st.session_state.scored_terms:
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
    else:
        st.info("Run SpecFlow AI on the Upload tab first.")

# ── Tab 7: About ──────────────────────────────────────────────────────────────
with tabs[7]:
    st.header("About SpecFlow AI")
    st.markdown("""
**SpecFlow AI** converts messy engineering documents into clean AI-agent-ready Markdown,
then uses a BMS/ICS/PLC knowledge base and source-confirmed confidence scoring to generate
RFIs, tasks, points-list candidates, CAD actions, field verification items, and commissioning checklists.

**Core rule:**
> Known vocabulary is not the same as detected vocabulary.
> The source document must support every output item.

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

**Stack:** Python · Streamlit · pymupdf4llm · Source-confirmed filtering
""")
