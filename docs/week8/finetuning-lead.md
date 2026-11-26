# Week 8 — Fine-Tuning Lead: Model Comparison

**Task (timeline, Week 8):** compare the selected SLM candidates on the same prompts, with and without retrieved context, and record their performance and limitations.
**Status:** Complete. Full run on the dev split on 2026-11-26 (Colab, Tesla T4); results in `eval/week8/model_comparison/`.
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

Open `notebooks/week8_model_comparison.ipynb` in Google Colab with a GPU runtime and run the cells in order: smoke test (2 items per task), full run (about 45–60 minutes), then download the results zip and commit it to `eval/week8/model_comparison/`.

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

Run on 2026-11-26 on a Tesla T4 (torch 2.14.1, transformers 5.22.1). Model revisions: Qwen `cdbee75f`, Gemma `093f9f38`. 56 dev items per model and condition. Golden and corpus checksums in `summary.json` match the committed files.

### Generation (21 folk and 21 rap items per row)

| Model | Condition | Mode | Structural pass | Line count OK | Syllable acc. | Rhyme match | Regional OK | Mean regional terms |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3-4B | no_rag | folk | 0% | 100% | 6% | 5% | 0% | 0.00 |
| Qwen3-4B | rag | folk | 0% | 90% | 17% | 0% | 5% | 0.38 |
| Gemma 3 4B | no_rag | folk | 0% | 90% | 13% | 0% | 0% | 0.05 |
| Gemma 3 4B | rag | folk | 0% | 95% | 22% | 5% | 0% | 0.10 |
| Qwen3-4B | no_rag | rap | 0% | 100% | 60% | 5% | 5% | 0.05 |
| Qwen3-4B | rag | rap | 0% | 100% | 64% | 0% | 24% | 0.52 |
| Gemma 3 4B | no_rag | rap | 0% | 100% | 63% | 5% | 5% | 0.05 |
| Gemma 3 4B | rag | rap | 0% | 100% | 76% | 0% | 14% | 0.14 |

### Dialect questions (14 items per row)

| Model | Condition | Correct (preliminary) | Grounding hit | Token-F1 (proxy) | Hit token limit |
|---|---|---:|---:|---:|---:|
| Qwen3-4B | no_rag | 2 / 14 | – | 9% | 0 |
| Qwen3-4B | rag | 3 / 14 | 67% | 9% | 0 |
| Gemma 3 4B | no_rag | 4.5 / 14 | – | 9% | 0 |
| Gemma 3 4B | rag | 4 / 14 | 67% | 8% | 2 |

*Correct (preliminary)*: one reviewer's reading against the reference answers (1 = correct, 0.5 = partly correct, 0 = wrong), not yet confirmed by two native speakers as the criteria require. Grounding hit: share of items with `expected_chunks` where at least one expected chunk was among the 3 retrieved (6 of 9 items; identical for both models because they receive the same context).

Mean generation time per item: 5.6–7.2 s for verses, 6.2–11.0 s for dialect answers (longer with context).

### Findings

1. **Neither model meets the structural constraints.** No output passes the structural check. Both models almost always write 4 lines, but rhymes are practically absent (0–5%), and folk lines are far too long (typically 10–13 syllables instead of 7–8). Rap lines fit the 12–16 range more often (60–76%).
2. **Retrieved context helps a little, mainly with regional vocabulary.** With context, rap outputs use more validated regional words (Qwen 5% → 24% meeting the minimum, Gemma 5% → 14%) and folk syllable accuracy rises slightly (Qwen 6% → 17%, Gemma 13% → 22%). Context does not improve rhyme.
3. **Dialect answers are mostly wrong, and confidently so.** Both models invent meanings (e.g. *curechi* as "ears", *ibovnic* as "someone pretending to be sick", *rujă* as a cosmetic). Only *fain* is answered correctly by all four runs. Gemma is slightly better without context (4.5 vs 2 of 14).
4. **Retrieving the right verse is not enough for dialect meaning.** In 6 of 9 grounded items the expected folk excerpt was in the context, yet the answers stayed wrong (e.g. *ibovnic*, *rujă*, *șurț*): a verse uses the word but does not define it. Dictionary or glossary entries would be needed, which the corpus does not have yet.
5. **The unapproved draft `rap-original-021` is retrieved often** (in the context of 14 of 56 items), because it packs many regional words into one verse. The one clear gain from context on dialect questions (*a se hodini*, answered correctly by both models with context) came from this draft. The criteria say it must not count as dialect evidence, so it should be excluded from the retrieval index until it is approved.
6. **Models sometimes ignore the task.** Gemma once answered a dialect question with an unrelated greeting, and hit the token limit in 3 outputs; Qwen invents non-words presented as regional (e.g. *pădurește*), as already seen in Week 7.

### Recommendation for Week 10

- Keep **Qwen3-4B-Instruct-2507** as the first QLoRA candidate. Gemma is not clearly better here (slightly better on dialect answers and rap syllables, equally failing on structure), while Qwen remains the practical choice from Week 7 (Apache-2.0 license, lower memory: about 7.5 vs 8 GB in BF16). Keep Gemma as the comparison model.
- Fine-tuning data should target **meter and rhyme** (the largest gap) and **correct dialect explanations**.
- Pass retrieved context in the agent, but do not rely on it for dialect meanings until glossary entries are added; use the MCP `syllable_counter` and `rhyme_checker` in the revision loop to enforce structure.
- Before E4, exclude unapproved records such as `rap-original-021` from retrieval and have two native speakers confirm the dialect correctness scores.

## Limitations

- 4B models in BF16 on a T4; results may differ with quantisation or other hardware.
- Rhyme and syllable checks are spelling heuristics; borderline cases need human review.
- The corpus is small (66 records) and provisional, so the `rag` condition can only help as far as the corpus covers a theme or word.
- Dialect items g-005 – g-012 have no corpus chunks, so retrieval cannot ground them.
