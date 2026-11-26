# Week 8 RAG

The baseline indexes the full processed corpus with dense BGE-M3 embeddings and cosine similarity in Qdrant. The collection name contains a digest of the input JSONL. Repeated ingestion of the same snapshot uses the same point IDs. After updating the corpus, ingest it before retrieving from that snapshot.

## Run the baseline

From the repository root, with Qdrant listening on port 6333 and the project Python environment active:

```powershell
python -m src.rag.baseline ingest
python -m src.rag.baseline search "dor și dragoste" --mode folk
```

Run `search` without `--mode` for unfiltered results. The model loads from the local cache when available.

## MCP integration

Instantiate the retriever once per server process and share it across tool calls.

```python
from src.rag.baseline import BaselineRetriever

retriever = BaselineRetriever()
hits = retriever.retrieve("dor și dragoste", mode="folk", limit=5)
```

Pass the tool's query, requested mode (`folk`, `rap` or `None`) and result limit to `retrieve`. The return value is a list of ranked chunk payloads with a cosine `score` added to each item. The payload includes `id`, `text`, `mode` and the corpus metadata. An empty list means that the query returned no hits for the supplied filter. Ingest the corpus before serving queries.

## E2 chunking experiment

```powershell
python -m src.rag.evaluate_chunking --output eval/week8/e2_chunking.json
```

The experiment compares the existing corpus fragments (including intact verse excerpts) with nonoverlapping windows of 16 whitespace-delimited words cut within each original fragment. The 16-word size is an experimental choice. Both variants use the same source text, BGE-M3 revision and unfiltered queries. Only validated development examples with expected chunk IDs contribute to the scores.

Gold labels refer to original corpus IDs. Window results are mapped to their original IDs and deduplicated in score order before taking the top five. Hit rate measures the fraction of queries with at least one expected ID, recall measures the fraction of expected IDs found, and MRR averages the reciprocal rank of the first expected ID. The comparison measures retrieval at the original-fragment level. It leaves wider document boundaries and human assessment of individual window quality for follow-up with Data Lead.

| Variant | Indexed chunks | Hit rate@5 | Recall@5 | MRR@5 |
| --- | ---: | ---: | ---: | ---: |
| Existing verse excerpts | 66 | 88.9% | 73.1% | 0.587 |
| Fixed 16-word windows | 158 | 88.9% | 83.3% | 0.704 |

Both variants found a relevant fragment for eight of the nine labeled development queries. Fixed windows found more expected fragments in the top five and ranked the first relevant fragment higher on average. All nine queries are dialect QA, so these results describe dialect retrieval on the provisional corpus. Keep existing fragments as the Week 8 baseline pending review with Data Lead and evaluation on additional development queries.

Per-query rankings and corpus fingerprints are in [e2_chunking.json](../eval/week8/e2_chunking.json).

## E2 rerun on the retrieval examples (2026-11-26)

The first run above used only 9 dialect questions: the Golden Dataset retrieval examples were still marked `draft`, and the script scores only `validated` items. After the retrieval labels were validated (all except g-021, which waits for `rap-original-021` to be approved), E2 was rerun on **21 dev queries**: 9 dialect questions and 12 retrieval queries (7 folk, 5 rap). g-002 is excluded because it has no expected chunks. Same model revision and corpus; results in [e2_chunking.json](../eval/week8/e2_chunking.json), including MRR@10 and a `by_group` breakdown.

| Group | Queries | Variant | Hit rate@5 | **Recall@5** | MRR@5 | MRR@10 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Retrieval (primary) | 12 | Existing excerpts | 66.7% | **45.8%** | 0.569 | 0.583 |
| | | Fixed 16-word windows | 66.7% | **43.8%** | 0.549 | 0.581 |
| – folk | 7 | Existing excerpts | 71.4% | 40.5% | 0.548 | 0.548 |
| | | Fixed 16-word windows | 71.4% | 41.7% | 0.607 | 0.628 |
| – rap | 5 | Existing excerpts | 60.0% | 53.3% | 0.600 | 0.633 |
| | | Fixed 16-word windows | 60.0% | 46.7% | 0.467 | 0.515 |
| Dialect questions | 9 | Existing excerpts | 88.9% | 73.1% | 0.587 | 0.587 |
| | | Fixed 16-word windows | 88.9% | 83.3% | 0.704 | 0.720 |
| All | 21 | Existing excerpts | 76.2% | 57.5% | 0.577 | 0.585 |
| | | Fixed 16-word windows | 76.2% | 60.7% | 0.615 | 0.640 |

The dialect results are identical to the first run, so the two runs are consistent.

**Interpretation.**

- On the retrieval queries (the primary metric, Recall@5), existing excerpts score slightly higher than fixed windows (45.8% vs 43.8%); the difference is under one expected chunk across 12 queries, so neither variant wins on thematic retrieval.
- Fixed windows help dialect questions (Recall@5 83.3% vs 73.1%): a short window around a rare word matches a one-word question better than a whole excerpt.
- Four retrieval queries fail with both variants: g-016 (family and home), g-019 (AABB rhyme scheme), g-022 (returning home) and g-092 (poem structured as a dialogue). g-019 and g-092 ask about **form** rather than content, which dense embeddings do not capture; the corpus now has `rhyme_scheme` metadata, so a metadata filter could address g-019 in E3.
- With 12 retrieval queries, one query changes Recall@5 by about 8 points, so these differences are indicative only.

**Decision for Week 8:** keep the existing excerpts as the baseline. Consider fixed windows (or a hybrid index) for dialect lookups, and test metadata filters and hybrid search in E3 (Week 9).
