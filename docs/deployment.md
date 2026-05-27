# Deployment Guide

This project is intended to run as a Dockerized Streamlit app on a Linux container and be accessed over Tailscale.

## Prerequisites

- Docker Engine with Compose support installed on the target container
- Tailscale installed and connected on the target container
- Git installed on the target container

## Build And Run

```bash
git clone https://github.com/STBMSEng4/Document-to-Workflow-AI-Orchestrator.git
cd Document-to-Workflow-AI-Orchestrator
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` if you plan to use a live model-backed flow.

Start the app:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
docker compose logs -f specflow-ai
```

## Access URLs

Use one of these from a Tailscale-connected browser:

- `http://<tailscale-ip>:8501`
- `http://<machine-name>:8501` if MagicDNS is enabled

## Tailscale Checks

On the target container:

```bash
tailscale status
tailscale ip -4
```

Make sure teammates can see the Michael node in Tailscale before testing the browser URL.

## Health Check

The container exposes a Streamlit health endpoint:

```bash
curl http://127.0.0.1:8501/_stcore/health
```

Expected response:

```text
ok
```

## Persistent Data

These folders are mounted out of the container:

- `./outputs` -> `/app/outputs`
- `./samples` -> `/app/samples`

That keeps exports and sample documents available across rebuilds.

## Notes

- The image installs Node.js and `@firecrawl/pdf-inspector`.
- The repo now includes a Firecrawl-based PDF parser plus a `pymupdf4llm` fallback path.
- Port `8501` must be reachable inside the target container environment.
