# MCP server

The stdio MCP server exposes three read-only tools: `syllable_counter` (Week 7), `rhyme_checker` and `retrieve_context` (Week 8).

## Install, test and run

From the repository root (Python 3.12):

```sh
python -m pip install "mcp>=2.2,<3" qdrant-client pytest
python -m pytest -q
```

Configure an MCP client to launch `python -m mcp_server.server` from the repository root using stdio.

Tests cover all three tools, stdio discovery/calls/errors and the retrieval adapter against the real baseline with in-memory Qdrant and deterministic test vectors. They do not measure live BGE-M3 semantic retrieval quality.

## `syllable_counter`

Takes a `text` string and returns one record per line, including blank lines. For example, `{"text":"Pomi\nUn râu"}` returns counts of 1 and 2, with each line's original text and 1-based line number. Digits and punctuation do not contribute syllables.

The counter estimates standard Romanian pronunciation using spelling rules and a small set of exceptions. The same written vowel sequence can represent a diphthong or hiatus ([DOOM 3 pronunciation guidance](https://doom.lingv.ro/studiu_introductiv/reguli_scriere_pronuntare)), so dialect, loanwords, and poetic or performed elisions may need manual review.

## `rhyme_checker`

Accepts `text` and an optional `expected_scheme` such as `ABAB`. It reports the observed scheme, line numbers, final words and endings, an optional scheme match, and a quality label (`estimated_rhyme`, `repeated_end_word`, or `no_rhyme`). Blank lines are skipped; letters in the expected scheme correspond to nonblank lines. Equivalent labelings such as `CCDD` and `AABB` are treated alike.

This is a spelling heuristic using an approximation of final/penultimate stress, not a phonetic rhyme assessment. Irregular stress, vowel groups, dialect and performed rap require human review.

## `retrieve_context`

Accepts `query`, optional `mode` (`folk`, `rap`, or omitted), and `limit` (1–20, default 5). It calls the Week 8 `BaselineRetriever` and returns `{"chunks": [...]}` with ranked payloads, provenance and scores. An empty list means no matches; backend failures are MCP tool errors. One retriever is created lazily and reused for the server process.

Follow the [Week 8 RAG setup](week8/rag.md) to install the embedding dependencies, start Qdrant and ingest the corpus before retrieving. The tool never ingests. Optional environment variables `QDRANT_URL` and `RAG_DATA_PATH` select the server and corpus snapshot; ingest that same snapshot using the baseline CLI's `--url` and `--data` options. Restart the MCP server after changing the corpus or config.
