# Week 8 — Fine-Tuning Lead: Model Comparison

**Task (timeline, Week 8):** compare the selected SLM candidates on the same prompts, with and without retrieved context, and record their performance and limitations.
**Status:** Code, tests and Colab notebook are ready. **The GPU run is still pending**: the results section below is filled in after running the notebook on Colab.
**Prepared by:** Evaluation & Documentation Lead (Luiza), on behalf of the Fine-Tuning Lead, on 2026-11-26.

## Setup

| Item | Value |
|---|---|
| Models | `Qwen/Qwen3-4B-Instruct-2507` (primary candidate), `google/gemma-3-4b-it` (alternative) |
| Not included | `OpenLLM-Ro/RoLlama-3.2-1B`: access to its base model was still pending in Week 7, and it is a 1B base model rather than a 4B instruction model |
| Conditions | `no_rag`: prompt only. `rag`: the same prompt plus the top-3 chunks from the Week 8 BGE-M3 baseline (`src/rag/baseline.py`, in-memory Qdrant); generation items are filtered by their mode |
| Items | All validated **dev** items of `data/eval/golden_v1.jsonl`: 42 generation (21 folk, 21 rap) and 14 dialect questions. The test split is not used |
| Decoding | Greedy (`do_sample=False`), BF16 on a Colab T4 |
| Token caps | `dialect_qa`: 300 new tokens (fixed by the evaluation criteria); `generation`: 200 new tokens for every model |
| Prompt | Identical text for both models: a short Romanian instruction, the corpus chunks (rag only), then the golden prompt with its constraints (lines, syllables, rhyme scheme, minimum regional words) |
| Model revisions | Resolved and recorded automatically in `summary.json` |

Retrieval runs once per item before the models are loaded, so both models see exactly the same context. The retrieved chunks are saved in `contexts.json`.

## How to run

Open `notebooks/week8_model_comparison.ipynb` in Google Colab with a GPU runtime and run the cells in order: smoke test (2 items per task), full run (about 45–60 minutes), then download the results zip and commit it to `eval/results/week8_model_comparison/`.

Without a GPU, the pipeline can be checked with stand-in models:

    python -m src.finetune.compare_models --dry-run --output /tmp/dry
    python -m pytest -q tests/test_compare_models.py

## Automatic scores

Computed by `src/finetune/compare_models.py` with the MCP tools, following `docs/evaluation-criteria.md`:

| Task | Score | How |
|---|---|---|
| generation | Line count, syllable accuracy, rhyme match, regional words, structural pass | `syllable_counter`, `rhyme_checker`, and the validated dialect list (§5 of the criteria); a structural pass needs all four, with syllable accuracy ≥ 0.75 |
| dialect_qa | Token-F1 with the reference answer | Word overlap only: a **proxy**, not a correctness score |
| dialect_qa (rag) | Grounding hit | At least one `expected_chunks` ID among the retrieved chunks |
| all | Token-limit hits, generation time | Recorded per item |

Not automatic: dialect **correctness**, theme adherence and meaning preservation need the LLM judge or a human (criteria §2–3). The per-item files keep every output with `"correctness": null` for that review. Regional words are counted with fixed word patterns per validated term, an approximation until the `dialect_lookup` tool exists.

## Results

*Pending the Colab run.* Paste `eval/results/week8_model_comparison/summary.md` here and add:

- which model is better per task, and whether retrieved context helps or hurts each model;
- typical errors (e.g. invented regional words, ignored constraints, token-limit hits), with example item IDs;
- the recommendation for the first QLoRA run (Week 10).

## Limitations

- 4B models in BF16 on a T4; results may differ with quantisation or other hardware.
- Rhyme and syllable checks are spelling heuristics; borderline cases need human review.
- The corpus is small (66 records) and provisional, so the `rag` condition can only help as far as the corpus covers a theme or word.
- Dialect items g-005 – g-012 have no corpus chunks, so retrieval cannot ground them.
