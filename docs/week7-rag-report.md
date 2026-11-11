# Week 7 — RAG Lead Report

## Objective

Set up local Qdrant, configure BGE-M3, create the initial
collection and demonstrate retrieval in a notebook.
Run an exploratory comparison with multilingual-e5.

## Implementation

- Qdrant runs locally in Docker.
- API and dashboard: http://localhost:6333
- Persistent Docker volume: llm-qdrant-storage
- Notebook: notebooks/week7_rag_retrieval.ipynb
- Dataset: data/processed/chunks.jsonl
- Corpus: 60 provisional fragments, 40 folk and 20 rap.
- Metadata, including source and approval status, is preserved.
- Inference runs on CPU.

## Embedding configurations

| Model | Dimensions | Collection |
|---|---:|---|
| BAAI/bge-m3 | 1024 | week7_bge_m3 |
| intfloat/multilingual-e5-base | 768 | week7_multilingual_e5_base |

Both models use normalized dense embeddings and cosine similarity.
E5 uses the required "passage: " and "query: " prefixes.
Both collections contain the same 60 fragments.
Stable UUIDs allow repeated upserts without duplicating records.

## Experiment E1

Both models were tested on the same 5 exploratory queries.
The top 5 results were inspected for each query.
Query-specific relevance criteria and proposed relevant IDs
are recorded in eval/week7/relevance_review.json.

| Query | BGE-M3 P@5 | E5-base P@5 |
|---|---:|---:|
| suferință din iubire și dor | 40% | 80% |
| mama și familia | 20% | 20% |
| viața la sat și munca | 60% | 40% |
| muzică, scenă și emoțiile artistului | 40% | 40% |
| dragoste care nu mă lasă să dorm | 40% | 40% |
| Mean | 40% | 44% |

## Interpretation

E5 retrieved one additional relevant result across the 25
evaluated positions. BGE-M3 ranked both explicitly relevant
sleeplessness fragments in the first two positions.

The difference is insufficient to establish an overall winner.
BGE-M3 remains the planned primary candidate pending broader evaluation.

## Limitations

- Only 5 queries were tested; two concern related romantic themes.
- Relevance labels were proposed after inspecting
  results and require team review.
- Labels cover inspected results, not exhaustive corpus relevance.
- The corpus is small and provisional, with historical spelling.
- Model similarity scores are not directly comparable across models.
- No controlled latency or memory benchmark was performed.
- This experiment tests dense retrieval only.

## Saved artifacts

- eval/week7/bge_m3_results.json
- eval/week7/e5_base_results.json
- eval/week7/relevance_review.json
- eval/week7/metrics.json

## Technical issues

Model downloads encountered network timeouts.
BGE-M3 loaded successfully with Xet disabled.
E5 was downloaded with snapshot_download using one worker,
then loaded from the local snapshot.
Both models successfully generated embeddings and supported retrieval.

## Next steps

Obtain team review of relevance labels, expand the query set
and continue the Week 8 baseline retrieval and chunking work.
## Local verification
All 23 notebook code cells were executed sequentially in a fresh Python
process using the existing local model cache with Hugging Face offline mode.
The check completed in approximately 254 seconds. Both collections contained
60 records, and mean Precision@5 remained 40% for BGE-M3 and 44% for E5-base.
This verifies sequential Python execution, not the VS Code/Jupyter UI or
first-time downloads on another machine.

Evidence: eval/week7/validation.json and eval/week7/environment.json.
The notebook includes the actual outputs from this verification run.
