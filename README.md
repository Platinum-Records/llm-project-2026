# Transylvanian Folk & Rap Dual-Mode Creative Agent

Agent that turns prompts into Transylvanian folk poetry or rap, using a fine-tuned SLM, RAG and an MCP tool server.

## Structure
- `docs/` RFC and project documents
- `data/` datasets (raw files are not committed)
- `src/` ingestion, RAG, agent, fine-tuning code
- `mcp_server/` MCP tools (syllable counter, rhyme checker, ...)
- `eval/` evaluation scripts and test prompts
- `notebooks/` experiments

## Setup
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

