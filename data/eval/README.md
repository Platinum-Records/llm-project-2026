# Golden Dataset — Week 7 draft

**File:** `golden_v1_draft.jsonl` (30 examples, one JSON object per line)
**Owner:** Evaluation & Documentation Lead
**Status:** Draft. It will be expanded to ~100 examples and frozen as `golden_v1.jsonl` with dev / locked-test splits in Week 8.

> The locked test split must never be used for fine-tuning or retrieval-corpus construction (data-leakage rule, see `docs/timeline.md` §5).

## Composition

| Task | Mode | Count | What it evaluates |
|---|---|---|---|
| `dialect_qa` | – | 10 (g-001, g-005 – g-013) | Correct meaning of Transylvanian / regional words and expressions |
| `retrieval` | folk | 6 (g-002, g-014 – g-018) | Whether RAG returns relevant folk chunks |
| `retrieval` | rap | 4 (g-019 – g-022) | Whether RAG returns relevant rap chunks |
| `generation` | folk | 5 (g-003, g-023 – g-026) | Structural and stylistic constraints on generated folk verse |
| `generation` | rap | 5 (g-004, g-027 – g-030) | Structural and stylistic constraints on generated rap verse |

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
| `constraints` | object | Generation: always `lines`, `syllables` (`{min, max}` per line), `scheme`, `theme`, `dialect_terms_min`. Retrieval: `theme` and/or `scheme`. Dialect: empty |
| `reference` | string \| null | Optional human-written reference output (none yet) |
| `status` | string | `draft`, `pending_dialect_validation`, `needs_answer`, `validated` |
| `notes` | string \| null | Caveats, e.g. weak or missing corpus coverage |

## Planned metrics

- **dialect_qa:** answer correctness against the validated reference (manual / LLM-judge), plus grounding in `expected_chunks`.
- **retrieval:** Recall@k and MRR against `expected_chunks` (E1, E3).
- **generation:** constraint satisfaction via MCP tools (`syllable_counter`, `rhyme_checker`), dialect-term count, plus human rating of dialect authenticity (E7).

## Syllable targets

Ranges are based on the Week 7 corpus (heuristic count per line): folk median 8 (p10–p90: 7–9), rap median 15 (p10–p90: 13–16).

| Mode | `syllables` | `dialect_terms_min` |
|---|---|---|
| folk | 7–8 (traditional trochaic line) | 2 |
| rap | 12–16 | 1 |

These are provisional and should be confirmed by the team.

## Validation

Run from the repository root:

    python eval/validate_golden.py

## Chunk references

`expected_chunks` point to the Data Lead's provisional Week 7 corpus (61 records, all `provisional_unapproved`). If chunk IDs change in Week 8 (e.g. stanza-based re-chunking), these references must be updated.

## Open items for Week 8

### Dialect validation (done)

All 10 dialect answers were **validated on 2026-11-11** by the Evaluation Lead (Luiza) and the Data Lead (Taisia) through native-speaker agreement. No written dialect source was used, because dialect glossaries are deferred; answers marked *not in corpus* cannot yet be grounded by retrieval.

| ID | Term | Draft answer | Status |
|---|---|---|---|
| g-001 | bade | form of address for an older brother/man; in folk poetry the beloved | validated (grounded in folk chunks) |
| g-005 | pită | bread | validated, not in corpus |
| g-006 | no, bine | informal agreement | validated, not in corpus |
| g-007 | curechi | cabbage | validated, not in corpus |
| g-008 | cocon | small child | validated, not in corpus |
| g-009 | a se hodini | to rest | validated, not in corpus |
| g-010 | fain | nice, pleasant | validated, not in corpus |
| g-011 | oleacă | a little | validated, not in corpus |
| g-012 | a sta la povești | to chat | validated, not in corpus |
| g-013 | mândru | proud / handsome / beloved | validated (grounded in folk chunks) |

### Other gaps

- **Corpus coverage:** g-002 (homesickness) has only a weak folk match. For g-021 (rap with regional expressions), the Evaluation Lead added one rap draft, `rap-original-021`, to the corpus; it needs the same team review as the other rap drafts.
- **References:** generation items have no human-written reference verses yet (`reference: null`); constraints are used for evaluation instead.
- **Balance:** the architecture plans 40 dialect/retrieval, 30 folk generation and 30 rap generation items. The Week 8 expansion should add ~20 dialect/retrieval, ~25 folk and ~25 rap generation items.
- **Native-speaker review:** `docs/architecture.md` §2.1 requires review by two native Transylvanian speakers; reviewers and dates are not recorded yet.
