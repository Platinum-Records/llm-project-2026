# Transylvanian Folk & Rap Dual-Mode Creative Agent

An agent that turns ordinary prompts into **Transylvanian folk poetry** or **regional rap**, combining a small language model (SLM), retrieval-augmented generation (RAG) over a curated regional corpus, and an MCP server with text-analysis tools (syllables, rhyme, retrieval).

**Team Platinum Records:** Taisia (Data) · Roxana (RAG) · Răzvan (Fine-tuning) · Denis (MCP / Agent) · Luiza (Evaluation & Documentation)

## Progress

| Week | Milestone | Status | Reports |
|---|---|---|---|
| 6 | Architecture and planning | ✅ Done | [Architecture](docs/architecture.md) · [RFC](docs/RFC.md) |
| 7 | Data preparation and initial infrastructure | ✅ Done | [Data](docs/week7/data-lead/README.md) · [RAG](docs/week7/rag-report.md) · [Fine-tuning](docs/week7/finetuning-lead.md) · [MCP](docs/mcp-server.md) |
| 8 | Baseline RAG and dataset finalisation | ✅ Done | [RAG](docs/week8/rag.md) · [Model comparison](docs/week8/finetuning-lead.md) · [Golden Dataset](data/eval/README.md) · [Evaluation criteria](docs/evaluation-criteria.md) |
| 9 | Progress check: agent loop with RAG and three tools | ▶ Next | |
| 10 | Fine-tuning and ingestion | Planned | |
| 11 | Full toolset and model comparison | Planned | |
| 12 | GitHub progress review | Planned | |
| 13 | Final evaluation and improvements | Planned | |
| 14 | Final presentation | Planned | |

Tasks per role and week: **[docs/timeline.md](docs/timeline.md)**

## Repository structure

```text
data/
  raw/                 provisional source samples (folk transcriptions, rap drafts)
  processed/           chunks.jsonl, the cleaned retrieval corpus
  eval/                Golden Dataset v1 (100 items, dev / locked test)
docs/                  RFC, architecture, timeline, evaluation criteria, MCP server
  week7/, week8/       weekly reports per role
eval/                  dataset validator and experiment results per week
mcp_server/            MCP tools: syllable_counter, rhyme_checker, retrieve_context
notebooks/             experiment notebooks (RAG retrieval, model comparison)
src/                   ingestion, rag, finetune (agent: upcoming)
tests/                 pytest suite
sources.csv            source inventory with provenance and licensing
```

All corpus data is a provisional sample (`provisional_unapproved`): for prototyping and evaluation only, not approved for training or public deployment.

## Quick start

Python 3.12, from the repository root:

```sh
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt

python src/ingestion/clean.py     # rebuild data/processed/chunks.jsonl
python eval/validate_golden.py    # check the Golden Dataset
python -m pytest -q               # run the tests
```

Retrieval needs a running Qdrant instance: see [docs/week8/rag.md](docs/week8/rag.md). The model comparison needs a GPU: see [docs/week8/finetuning-lead.md](docs/week8/finetuning-lead.md).

## Documentation

- **Project:** [RFC](docs/RFC.md) · [Architecture](docs/architecture.md) · [Timeline](docs/timeline.md) · [Architecture presentation](docs/architecture-presentation.pdf)
- **Evaluation:** [Evaluation criteria](docs/evaluation-criteria.md) · [Golden Dataset](data/eval/README.md)
- **Components:** [MCP server](docs/mcp-server.md) · [RAG baseline](docs/week8/rag.md) · [Week 7 RAG setup (Windows)](docs/week7/rag-setup.md)
