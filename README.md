# SpecFlow AI

AI-powered document-to-workflow orchestrator for engineering teams.

## Purpose

SpecFlow AI converts project documents such as PDFs, specifications, cut sheets, and web pages into structured engineering outputs.

The tool helps extract:

- Project summaries
- Scope items
- RFIs
- Risks and gaps
- CAD tasks
- Field verification items
- Equipment lists
- Draft BMS points lists
- Submittal checklist items

## Hackathon Goal

Build a working MVP that can:

1. Upload or ingest a document.
2. Convert the document to clean Markdown.
3. Use AI to extract workflow items.
4. Display results in a simple UI.
5. Export outputs to CSV or Markdown.

## Proposed Workflow

```text
PDF / URL / Spec / Cut Sheet
        ↓
Parser
        ↓
Markdown
        ↓
AI Extractor
        ↓
Structured JSON
        ↓
RFIs / Tasks / Points / Reports
```

## Tech Stack

- Python
- Streamlit
- Firecrawl PDF Inspector
- PyMuPDF / PyMuPDF4LLM fallback
- OpenAI or approved LLM API
- Markdown / CSV export

## Folder Structure

```text
app/
docs/
prompts/
samples/
outputs/
tests/
scripts/
```

## Container Run

Run the app in Docker:

```bash
cp .env.example .env
docker compose up -d --build
```

Then open:

```text
http://<tailscale-ip>:8501
```

Deployment notes live in [docs/deployment.md](/E:/Document-to-Workflow-AI-Orchestrator/docs/deployment.md).

## Branch Strategy

- `main` = final demo-ready branch
- `dev` = integration branch
- `feature/*` = individual feature work

## MVP Outputs

- Markdown document summary
- RFI table
- Task list
- Equipment list
- Points list draft
- CSV export
