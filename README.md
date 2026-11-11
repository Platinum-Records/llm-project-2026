# Transylvanian Folk & Rap Dual-Mode Creative Agent

Agent that turns prompts into Transylvanian folk poetry or rap, using a fine-tuned SLM, RAG and an MCP tool server.

## Structure
- `docs/` RFC, architecture, timeline and weekly role documentation (e.g. `docs/week7-data-lead/`, `docs/week7-rag-report.md`)
- `data/raw/` provisional source samples (folk transcriptions, rap drafts)
- `data/processed/chunks.jsonl` cleaned and deduplicated records used for retrieval
- `data/eval/` Golden Dataset for evaluation (see `data/eval/README.md`)
- `sources.csv` source inventory with provenance and licensing status
- `src/` ingestion, RAG, agent, fine-tuning code
- `mcp_server/` MCP tools (syllable counter, rhyme checker, ...)
- `eval/` evaluation scripts and experiment results (e.g. `eval/week7/`)
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

## Week 7 RAG prototype

- [Windows setup and execution](docs/week7-rag-setup.md)
- [Retrieval notebook](notebooks/week7_rag_retrieval.ipynb)
- [Exploratory embedding comparison](docs/week7-rag-report.md)

The prototype was run on the original 60 provisional corpus fragments (the corpus now has 61). Relevance labels and Precision@5 results are preliminary and pending team review.