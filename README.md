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

## Week 7 MCP syllable counter

From the repository root, install the MCP and test dependencies and run the tests:

```sh
python -m pip install "mcp>=2.2,<3" pytest
python -m pytest -q
```

Configure an MCP client to launch `python -m mcp_server.server` from the
repository root using stdio. The read-only `syllable_counter` tool takes a
`text` string and returns one record per line, including blank lines. For
example, `{"text":"Pomi\nUn râu"}` returns counts of 1 and 2, with each
line's original text and 1-based line number. Digits and punctuation do not
contribute syllables.

The counter estimates standard Romanian pronunciation using spelling rules and
a small set of exceptions. The same written vowel sequence can represent a
diphthong or hiatus ([DOOM 3 pronunciation guidance](https://doom.lingv.ro/studiu_introductiv/reguli_scriere_pronuntare)),
so dialect, loanwords, and poetic or performed elisions may need manual review.

## Week 8 MCP tools

The stdio server now exposes `syllable_counter`, `rhyme_checker` and
`retrieve_context`. Install `qdrant-client` as well as the MCP/pytest dependencies
above for the full test suite (`python -m pytest -q`).

`rhyme_checker` accepts `text` and an optional `expected_scheme` such as `ABAB`.
It reports the observed scheme, line numbers, final words and endings, an
optional scheme match, and a quality label (`estimated_rhyme`,
`repeated_end_word`, or `no_rhyme`). Blank lines are skipped; letters in the
expected scheme correspond to nonblank lines. Equivalent labelings such as
`CCDD` and `AABB` are treated alike. This is a spelling heuristic using an
approximation of final/penultimate stress, not a phonetic rhyme assessment.
Irregular stress, vowel groups, dialect and performed rap require human review.

`retrieve_context` accepts `query`, optional `mode` (`folk`, `rap`, or omitted),
and `limit` (1–20, default 5). It calls the existing Week 8 `BaselineRetriever`
and returns `{"chunks": [...]}` with ranked payloads, provenance and scores.
An empty list means no matches; backend failures are MCP tool errors.
One retriever is created lazily and reused for the server process.

Follow [Week 8 RAG setup](docs/week8-rag.md) to install the embedding dependencies,
start Qdrant and ingest the corpus before retrieving. The tool never ingests.
Optional environment variables `QDRANT_URL` and `RAG_DATA_PATH` select the server
and corpus snapshot; ingest that same snapshot using the baseline CLI's `--url`
and `--data` options. Restart the MCP server after changing the corpus or config.
Launch from the repository root with `python -m mcp_server.server`.

Tests cover all three tools, stdio discovery/calls/errors and the retrieval
adapter against the real baseline with in-memory Qdrant and deterministic test
vectors. They do not measure live BGE-M3 semantic retrieval quality.

## Week 7 RAG prototype

- [Windows setup and execution](docs/week7-rag-setup.md)
- [Retrieval notebook](notebooks/week7_rag_retrieval.ipynb)
- [Exploratory embedding comparison](docs/week7-rag-report.md)

The prototype was run on the original 60 provisional corpus fragments (the corpus now has 61). Relevance labels and Precision@5 results are preliminary and pending team review.
