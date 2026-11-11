# Transylvanian Folk & Rap Dual-Mode Creative Agent

Agent that turns prompts into Transylvanian folk poetry or rap, using a fine-tuned SLM, RAG and an MCP tool server.

## Structure
- `docs/` RFC and project documents
- `data/` datasets (includes the provisional Week 7 sample)
- `src/` ingestion, RAG, agent, fine-tuning code
- `mcp_server/` MCP tools (syllable counter, rhyme checker, ...)
- `eval/` evaluation scripts and test prompts
- `notebooks/` experiments

## Setup
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt


## Week 7 RAG prototype

- [Windows setup and execution](docs/week7-rag-setup.md)
- [Retrieval notebook](notebooks/week7_rag_retrieval.ipynb)
- [Exploratory embedding comparison](docs/week7-rag-report.md)

The prototype uses 60 provisional corpus fragments. Relevance labels and
Precision@5 results are preliminary and pending team review.
