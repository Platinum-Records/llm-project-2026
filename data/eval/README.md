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

## Evaluation rules

PR #8 documents the following rules. Team approval is pending.

- A generation item passes the structural check only if it meets all four conditions together. The output has the required line count, syllable accuracy is at least 0.75 (at least 3 of 4 lines within range), the rhyme scheme matches, and the regional-term minimum is met.
- Recall@5 is the primary retrieval metric. Average the scores per eligible item, use the same eligible set for all systems in a comparison, and report by split and mode with the number of items scored and the IDs excluded. Items with empty `expected_chunks` are excluded. The current exclusions are g-002 and g-021, as described under Known gaps. Excluded items receive no score.
- In `dialect_qa` comparisons, cap responses at 300 newly generated tokens (`max_new_tokens=300` or equivalent) and record the effective cap for each system. For `generation`, set and record a separate common cap before the run. Retrieval scored on returned chunk IDs uses no generation token cap.

## Validation

Run from the repository root:

    python eval/validate_golden.py

It checks JSON validity, fields, allowed values, generation constraints, that every `expected_chunks` ID exists in the corpus, and that exposed items are not in `test`.

## Dialect validation

| Batch | Items | Status |
|---|---|---|
| Week 7 | g-001, g-005 – g-013 | **Validated** on 2026-11-11 by the Evaluation Lead (Luiza) and the Data Lead (Taisia), native-speaker agreement. |
| Week 8 | g-081 – g-090 | All 10 examples are marked `validated` in the JSONL. All 10 terms occur in the folk corpus. |

The answers for g-005 – g-012 are marked `validated`, but their `expected_chunks` lists are empty because no corpus excerpts are eligible for grounding. Several forms appear in `rap-original-021`, a provisional draft excluded as evidence for `dialect_qa`.

Week 8 answers from the JSONL:

| ID | Term | Reference answer (Romanian) | Corpus chunks |
|---|---|---|---|
| g-081 | lele | Apelativ popular pentru o soră mai mare sau o femeie mai în vârstă. În versurile citate, este o adresare afectuoasă către iubită. | folk-jb1895-014, -025 |
| g-082 | nime | Nimeni. | folk-jb1895-026, -030 |
| g-083 | de urât | Din plictiseală sau din apăsarea singurătății. | folk-jb1895-004 |
| g-084 | ibovnic | Iubit, persoana iubită. | folk-jb1895-020 |
| g-085 | șurț | Șorț. | folk-jb1895-005 |
| g-086 | chică | Păr (lung), plete; „cu chica creață” înseamnă „cu părul creț”. | folk-jb1895-036 |
| g-087 | rujă | O floare. „Trandafir” este un sens regional posibil, dar specia nu este precizată în versuri. | folk-jb1895-012, -033 |
| g-088 | scoverzi | Un preparat din aluat prăjit, de tip plăcintă sau clătită. | folk-jb1895-024 |
| g-089 | a omeni | A primi cu ospitalitate, a ospăta. | folk-jb1895-024 |
| g-090 | cioareci | Pantaloni țărănești strânși pe picior, din țesătură de lână, de exemplu pănură sau dimie. | folk-jb1895-023 |

## Before freezing

1. Record the Data Lead confirmation for g-081 – g-090. All ten are already marked `validated` in the JSONL.
2. Check the Romanian wording of the 70 new prompts (g-031 – g-100).
3. Remap `expected_chunks` if the Data Lead's Week 8 corpus changes chunk IDs (stanza-based chunking), and link chunks for g-005 – g-012 once dialect material is added.
4. Confirm the evaluation rules documented in PR #8 and in `docs/evaluation-criteria.md` with the team.
5. Rename to `golden_v1.jsonl` and commit. After freezing, change `test` items only to fix clear errors, and record every change.

## Known gaps

- **Corpus coverage.** g-002 has an empty `expected_chunks` list because the corpus has no directly relevant folk excerpt about homesickness. g-021 retains `rap-original-021` as a candidate reference and is excluded from official scoring until the chunk is approved and included in the retrieval index. The chunk provides no grounding for `dialect_qa` answers.
- **References:** generation items have no human-written reference verses (`reference: null`); constraints and judged scores are used instead.
- **Chunk references** point to the current corpus (66 records, all `provisional_unapproved`).
