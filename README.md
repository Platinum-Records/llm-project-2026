# Transylvanian Folk & Rap Dual-Mode Creative Agent

Agent that turns prompts into Transylvanian folk poetry or rap, using a fine-tuned SLM, RAG and an MCP tool server.

## Structure
- `docs/` RFC, architecture, timeline and weekly role documentation (e.g. `docs/week7-data-lead/`)
- `data/raw/` provisional source samples (folk transcriptions, rap drafts)
- `data/processed/chunks.jsonl` cleaned and deduplicated records used for retrieval
- `data/eval/` Golden Dataset for evaluation (see `data/eval/README.md`)
- `sources.csv` source inventory with provenance and licensing status
- `src/` ingestion, RAG, agent, fine-tuning code
- `mcp_server/` MCP tools (syllable counter, rhyme checker, ...)
- `eval/` evaluation scripts
- `notebooks/` experiments

> All data in `data/raw/` and `data/processed/` is a **provisional Week 7 sample** (`provisional_unapproved`): for local prototyping and evaluation only, not approved for training or public deployment.

## Setup
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

## Usage

Rebuild the processed dataset from the raw files:

    python src/ingestion/clean.py

Check that the Golden Dataset is well-formed and that its chunk references exist:

    python eval/validate_golden.py
