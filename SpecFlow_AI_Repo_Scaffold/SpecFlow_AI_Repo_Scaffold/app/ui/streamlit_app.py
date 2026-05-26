"""Streamlit UI scaffold for SpecFlow AI."""

import streamlit as st

st.set_page_config(page_title="SpecFlow AI", layout="wide")
st.title("SpecFlow AI")
st.subheader("Document-to-Workflow AI Orchestrator")

st.write("Upload a project document or paste a URL, then generate RFIs, tasks, equipment, and points-list drafts.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
url = st.text_input("Or paste webpage URL")

if st.button("Generate Workflow"):
    st.info("MVP placeholder: parser and AI extraction will be connected here.")

    st.markdown("## Example Outputs")
    st.markdown("### RFIs")
    st.dataframe([
        {"RFI #": 1, "Question": "Who owns FA shutdown wiring?", "Priority": "High"},
        {"RFI #": 2, "Question": "Are existing controllers reused or replaced?", "Priority": "High"},
    ])

    st.markdown("### CAD Tasks")
    st.dataframe([
        {"Task": "Add BAS network riser", "Owner": "CAD/Engineer"},
        {"Task": "Add VAV controller tags", "Owner": "CAD"},
    ])
