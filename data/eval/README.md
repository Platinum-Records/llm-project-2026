# Golden Dataset v1

**File:** `golden_v1_draft.jsonl` (100 examples, one JSON object per line). It will be renamed to `golden_v1.jsonl` when frozen.
**Owner:** Evaluation & Documentation Lead
**Status:** Week 8 — expanded to 100 examples with dev / locked-test splits. Freezing is waiting for the items listed under *Before freezing*.
**Scoring rules:** see [`docs/evaluation-criteria.md`](../../docs/evaluation-criteria.md).

> The `test` split is locked: use it only for the final system comparisons (E5, Week 11; final evaluation, Week 13). Never use golden examples for fine-tuning or for building the retrieval corpus.

## Composition

| Task | Mode | IDs | Items | dev | test |
|---|---|---|---:|---:|---:|
| `dialect_qa` | – | g-001, g-005 – g-013, g-081 – g-090 | 20 | 14 | 6 |
| `retrieval` | folk | g-002, g-014 – g-018, g-091 – g-095 | 11 | 8 | 3 |
| `retrieval` | rap | g-019 – g-022, g-096 – g-100 | 9 | 6 | 3 |
| `generation` | folk | g-003, g-023 – g-026, g-031 – g-055 | 30 | 21 | 9 |
| `generation` | rap | g-004, g-027 – g-030, g-056 – g-080 | 30 | 21 | 9 |
| **Total** | | | **100** | **70** | **30** |

This matches the planned distribution in `docs/architecture.md` §2 (40 dialect/retrieval, 30 folk, 30 rap).

Eight generation items (g-052 – g-055 folk, g-077 – g-080 rap) ask the system to turn a plain sentence into verse. Their `constraints.source_text` is used to score meaning preservation.

## Schema

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable identifier `g-NNN` |
| `task` | `dialect_qa` \| `retrieval` \| `generation` | Evaluation category |
| `mode` | `folk` \| `rap` \| null | Creative mode (null for dialect questions) |
| `prompt` | string | Input given to the system, **in Romanian** |
| `prompt_en` | string | English version of the prompt, for reviewers |
| `expected_answer` | string \| null | Reference answer in Romanian (dialect_qa) or relevance description (retrieval); null for generation |
| `expected_answer_en` | string \| null | English version of `expected_answer` |
| `expected_chunks` | list[string] | IDs from `data/processed/chunks.jsonl` that count as relevant (retrieval) or that ground the answer (dialect_qa) |
| `constraints` | object | Generation: `lines`, `syllables` (`{min, max}` per line), `scheme`, `theme`, `dialect_terms_min`, optional `source_text`. Retrieval: `theme` and/or `scheme`. Dialect: empty |
| `reference` | string \| null | Optional human-written reference output (none yet) |
| `split` | `dev` \| `test` | Development or locked test split |
| `status` | string | `draft`, `pending_dialect_validation`, `needs_answer`, `validated` |
| `notes` | string \| null | Caveats, e.g. weak or missing corpus coverage |

## Splits

- 30% locked test, stratified by task, mode, Week 7 vs Week 8 dialect items and meaning-preservation items; fixed seed 2026.
- Items used outside evaluation must stay in `dev`: **g-001, g-003, g-004** (used in the Week 7 fine-tuning smoke tests). The validator enforces this.

## Syllable targets

Based on the Week 7 corpus (heuristic count per line): folk median 8 (p10–p90: 7–9), rap median 15 (p10–p90: 13–16).

| Mode | `syllables` | `dialect_terms_min` |
|---|---|---|
| folk | 7–8 (traditional trochaic line) | 2 |
| rap | 12–16 | 1 |

## Validation

Run from the repository root:

    python eval/validate_golden.py

It checks JSON validity, fields, allowed values, generation constraints, that every `expected_chunks` ID exists in the corpus, and that exposed items are not in `test`.

## Dialect validation

| Batch | Items | Status |
|---|---|---|
| Week 7 | g-001, g-005 – g-013 | **Validated** on 2026-11-11 by the Evaluation Lead (Luiza) and the Data Lead (Taisia), native-speaker agreement. g-005 – g-012 are not yet in the corpus. |
| Week 8 | g-081 – g-090 | **Pending validation** with the Data Lead. All 10 terms occur in the folk corpus. |

Week 8 terms to validate:

| ID | Term | Draft answer | Corpus chunks |
|---|---|---|---|
| g-081 | lele | older woman / older sister; in folk poetry a young woman or sweetheart | folk-jb1895-014, -025 |
| g-082 | nime | nobody (nimeni) | folk-jb1895-026, -030 |
| g-083 | de urât | out of loneliness, boredom, longing | folk-jb1895-004 |
| g-084 | ibovnic | lover, beloved | folk-jb1895-020 |
| g-085 | șurț | apron (șorț) | folk-jb1895-005 |
| g-086 | chică | hair, long locks | folk-jb1895-036 |
| g-087 | rujă | rose (trandafir) | folk-jb1895-012, -033 |
| g-088 | scoverzi | pancakes (clătite) | folk-jb1895-024 |
| g-089 | a omeni | to host with food and drink | folk-jb1895-024 |
| g-090 | cioareci | tight woollen peasant trousers | folk-jb1895-023 |

## Before freezing

1. Validate g-081 – g-090 with the Data Lead and set their `status` to `validated`.
2. Check the Romanian wording of the 70 new prompts (g-031 – g-100).
3. Remap `expected_chunks` if the Data Lead's Week 8 corpus changes chunk IDs (stanza-based chunking), and link chunks for g-005 – g-012 once dialect material is added.
4. Confirm the *(proposed)* values in `docs/evaluation-criteria.md`.
5. Rename to `golden_v1.jsonl` and commit. After freezing, change `test` items only to fix clear errors, and record every change.

## Known gaps

- **Corpus coverage:** g-002 (homesickness) has only a weak folk match; g-021 depends on `rap-original-021`, which is still pending team review.
- **References:** generation items have no human-written reference verses (`reference: null`); constraints and judged scores are used instead.
- **Chunk references** point to the provisional Week 7 corpus (61 records, all `provisional_unapproved`).
