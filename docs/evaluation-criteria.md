# Evaluation Criteria — Golden Dataset v1

**Owner:** Evaluation & Documentation Lead
**Status:** Week 8 evaluation rules documented in PR #8. Team approval is pending.
**Applies to:** `data/eval/golden_v1.jsonl`

This document defines how every system configuration (A: commercial baseline, B: untuned SLM, C: fine-tuned SLM) and every experiment (E2–E7) is scored on the Golden Dataset, so that results are comparable across weeks and team members.

---

## 1. Dataset and splits

| Task | Mode | Items | dev | test |
|---|---|---:|---:|---:|
| `dialect_qa` | – | 20 | 14 | 6 |
| `retrieval` | folk | 11 | 8 | 3 |
| `retrieval` | rap | 9 | 6 | 3 |
| `generation` | folk | 30 | 21 | 9 |
| `generation` | rap | 30 | 21 | 9 |
| **Total** | | **100** | **70** | **30** |

- The split is stratified by task, mode, Week 7/Week 8 dialect items and meaning-preservation items, using a fixed seed (2026).
- **`dev`** is used for all development: prompt changes, retrieval parameters, chunking choices, checkpoint selection and the revision loop.
- **`test`** is locked. It is run only for the final system comparisons (E5 in Week 11 and the final evaluation in Week 13). Nobody tunes anything after looking at test outputs.
- Items used outside evaluation are kept in `dev`. Currently: g-001, g-003, g-004 (Week 7 fine-tuning smoke tests). `eval/validate_golden.py` enforces this.
- **Leakage rule:** no golden prompt, expected answer or reference may appear in fine-tuning instruction pairs. Before each training run, the Data Lead checks instruction pairs against `golden_v1.jsonl` (exact and near-duplicate prompts).

---

## 2. Generation (`task = generation`, 60 items)

Give the system the Romanian prompt and the item constraints for generation. Every generated output is scored on the dimensions below. Structural checks are automatic; quality checks are judged.

| Dimension | How it is measured | Tool / judge | Score |
|---|---|---|---|
| Line count | Number of non-empty lines = `constraints.lines` | script | 0/1 |
| Syllable accuracy | Share of lines whose syllable count is within `constraints.syllables` (`min`–`max`) | MCP `syllable_counter` | 0–1 |
| Rhyme scheme | Rhyme scheme of the output matches `constraints.scheme` | MCP `rhyme_checker` (Week 8) | 0/1 |
| Regional vocabulary | Number of distinct regional terms ≥ `constraints.dialect_terms_min`; a term counts only if it is in the validated dialect list (see §5) | MCP `dialect_lookup` (Week 11); manual until then | 0/1, plus count |
| Invented regional terms | Words presented as regional that are not real regional words (e.g. explanations invented by the model) | human / judge | count (lower is better) |
| Theme adherence | Output addresses `constraints.theme` and the prompt | LLM judge, 1–5 | 1–5 |
| Meaning preservation | For items with `constraints.source_text`: output keeps the meaning of the source sentence | LLM judge, 1–5; MCP `meaning_check` (Week 11) | 1–5 |
| Dialect authenticity | Sounds like genuine Transylvanian folk / regional rap | 2 native speakers, 1–5 (E7) | 1–5 |
| Toxicity | Output flagged by the toxicity filter | MCP toxicity filter (Week 10) | 0/1 (lower is better) |

**Structural pass:** an item passes only when all four conditions hold. The line count is correct, syllable accuracy is at least 0.75 (at least 3 of 4 lines are within range), the rhyme scheme matches, and the regional-term minimum is met.

**Reported per system and mode:** structural pass rate, mean syllable accuracy, rhyme match rate, regional-term pass rate, mean invented terms per item, mean theme / meaning scores, toxicity rate.

Syllable targets are taken from the corpus: folk lines 7–8 syllables (traditional trochaic line), rap lines 12–16 syllables (corpus median 15).

---

## 3. Dialect questions (`task = dialect_qa`, 20 items)

| Measure | How it is measured | Score |
|---|---|---|
| Correctness | Answer compared with `expected_answer` by an LLM judge; all test items and ≥ 20% of dev items are also checked by a human | 1 correct, 0.5 partially correct, 0 incorrect |
| Grounding (systems with RAG) | For items with `expected_chunks`: at least one expected chunk is in the retrieved context, and the answer does not contradict it | 0/1 |
| Hallucination | The answer invents a meaning, origin or usage that is not supported | 0/1 (lower is better) |

**Reported:** mean correctness, grounding rate (only for items with `expected_chunks`), hallucination rate.

Only dialect items with `status = validated` count in reported results. Items g-005 through g-012 are eligible for correctness scoring and excluded from grounding scores because they have no eligible corpus references. The provisional rap-original-021 provides no dialect evidence. Items still `pending_dialect_validation` are reported separately until they are validated.

---

## 4. Retrieval (`task = retrieval`, 20 items)

The query is `prompt`; relevant results are `expected_chunks`, defined **before** running any retrieval system (unlike the Week 7 E1 labels, which were assigned after inspecting results).

| Metric | Definition |
|---|---|
| Recall@5 | Share of `expected_chunks` found in the top 5 results |
| MRR@10 | 1 / rank of the first relevant result in the top 10 (0 if none) |
| Precision@5 | Share of the top 5 results that are in `expected_chunks` (kept for comparability with E1) |

- Mode filtering (E3) uses the item's `mode`.
- Exclude items with empty `expected_chunks` from scoring. The current exclusions are g-002 (no directly relevant folk excerpt about homesickness) and g-021 (its reference, rap-original-021, is pending approval and must be included in the retrieval index before scoring). Excluded items receive no score.
- If chunk IDs change (e.g. stanza-based chunking in E2), `expected_chunks` must be remapped before comparing runs; runs on different chunkings are compared on Recall@5 and MRR@10 only.

**Primary metric: Recall@5.** Average the per-item Recall@5 scores over eligible items. Use the same eligible set for all systems in a comparison. Report results by split and mode, including the number of eligible items scored and the IDs of excluded items.

---

## 5. Validated dialect list

Regional-term counting and dialect correctness use one shared list: the terms of all `dialect_qa` items with `status = validated`, plus the Data Lead's dialect glossary once it is approved. A term outside this list is not counted as regional, even if a model claims it is.

---

## 6. Human evaluation (E7)

- Two native Transylvanian Romanian speakers rate generation outputs of the **test** split for systems A, B and C (randomised order, system names hidden).
- Scale for dialect authenticity and overall quality: 1 = not at all, 3 = partly convincing, 5 = fully convincing.
- Agreement is reported as the share of items where the two ratings differ by at most 1 point.
- Reviewer names and dates are recorded in the results file.

---

## 7. Experiment protocol

The dataset validator checks data structure and reference IDs. Model runs and team approval are separate.

| Experiment | Week | Split | Tasks / metrics used |
|---|---|---|---|
| E2 Stanza vs fixed-size chunking | 8 | dev | Retrieval: Recall@5, MRR@10 |
| E3 Mode filtering, hybrid search, re-ranking | 9 | dev | Retrieval: Recall@5, MRR@10, P@5; dialect grounding |
| E4 First QLoRA vs base SLM | 10 | dev | Generation and dialect metrics (§2, §3) |
| E5 Systems A vs B vs C | 11 | **test** | All tasks |
| E6 Agent with vs without revision loop | 12 | dev | Generation structural metrics, theme / meaning |
| E7 Human dialect authenticity | 13 | **test** | §6 |

Rules for every run:
- Use the same generation settings for all systems in a comparison within each task and record them (decoding, temperature, effective output token limit, model revision, date, GPU). For `dialect_qa` comparisons, cap each response at 300 newly generated tokens (`max_new_tokens=300` or the equivalent setting) and record the effective cap for each system. For `generation`, set and record a separate common cap before running the comparison. Retrieval scored on returned chunk IDs uses no generation token cap.
- Save per-item outputs and scores, not only averages, under `eval/results/<experiment>/<system>.jsonl`, plus a `summary.json`.
- Report results separately per task and mode, and always say which split was used.
