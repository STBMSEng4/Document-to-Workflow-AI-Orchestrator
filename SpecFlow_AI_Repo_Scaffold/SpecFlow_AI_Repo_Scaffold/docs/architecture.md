# Architecture

## MVP Flow

```text
PDF / URL
  -> Parser
  -> Markdown
  -> AI Extractor
  -> Structured JSON
  -> Streamlit UI
  -> CSV / Markdown exports
```

## Components

- `app/parsers`: PDF and web ingestion
- `app/extractors`: AI extraction logic
- `app/exporters`: CSV and Markdown output
- `app/ui`: Streamlit UI
- `prompts`: Reusable AI prompts
