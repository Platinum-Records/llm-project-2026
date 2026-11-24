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
