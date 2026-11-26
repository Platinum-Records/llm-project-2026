# Week 7 — Data Lead Handoff (Provisional Sample)

## Overview

This deliverable contains **61 candidate text fragments** for the Transylvanian Folk & Rap Dual-Mode Creative Agent:

- **40 folk fragments** transcribed from historical Transylvanian folk poetry.
- **21 AI-assisted rap drafts** prepared for initial experimentation (`rap-original-021` was added by the Evaluation Lead to cover golden item g-021).

The dataset is intended for Week 7 RAG and embedding experiments. All records are provisional and have not received final editorial or licensing approval.

## Deliverables

| File | Description |
|---|---|
| `data/raw/folk_first_pass.jsonl` | 40 folk candidates with source and page provenance |
| `data/raw/rap_original_revised.jsonl` | 21 revised AI-assisted rap candidates |
| `data/processed/chunks.jsonl` | 61 normalized and deduplicated provisional records |
| `sources.csv` | Source inventory, provenance and licensing information |
| `src/ingestion/clean.py` | Text normalization, validation, exact deduplication and approval filtering |

## Data Processing

The cleaning script performs the following operations:

1. Normalizes Unicode text and Romanian diacritics, including comma-below `ș` and `ț`.
2. Normalizes whitespace and line formatting.
3. Validates required fields and rejects invalid records.
4. Removes exact duplicates.
5. Preserves source and licensing metadata.
6. Supports filtering records by approval status.

Historical spelling is preserved in the Week 7 folk dataset. Spelling modernization and further metadata improvements are planned for Week 8.

## Rebuild

Run the following command from the repository root:

```bash
python src/ingestion/clean.py
```

This generates `data/processed/chunks.jsonl` with the 61 provisional records for initial RAG testing.

To generate an approved-only dataset:

```bash
python src/ingestion/clean.py --approved-only
```

Currently, the approved-only output contains zero records because no candidate has received final approval.

## Dataset Status and Licensing

All 61 records have the status:

`dataset_status: provisional_unapproved`

The dataset is provided for initial local prototyping and evaluation only.

The folk material originates from historical public-domain texts, but the reuse conditions of the digitized source still require confirmation.

The rap fragments are AI-assisted drafts and require editorial review by the team.

These records must not be presented as fully approved, rights-cleared or ready for public deployment or model training.

## Deferred Sources

The initial dataset contains folk and rap fragments only.

- Dialect dictionaries and regional glossaries were deferred because their reuse conditions require further verification.
- Automated extraction from dexonline was excluded pending permission.
- Other candidate folk and literary sources, including Ion Pop-Reteganul and George Coșbuc, were considered but not included in this initial sample.

## Week 7 Validation

| Check | Result |
|---|---|
| Folk fragments | 40 |
| Rap fragments | 21 |
| Total processed fragments | 61 |
| Exact duplicates | 0 |
| Invalid records | 0 |
| Approved records | 0 |

The processed dataset provides the initial JSONL format and sample required by the RAG Lead for local retrieval experiments.

## Planned Improvements — Week 8

The following improvements are deferred to Week 8:

1. Preserve historical text in `text_original` and add modernized spelling in `text`.
2. Apply stanza-based chunking to folk poetry.
3. Complete `theme`, `rhyme_scheme` and other metadata consistently.
4. Expand the corpus with suitable regional and dialect material.
5. Complete the source inventory metadata.
6. Coordinate editorial approval and resolve outstanding licensing questions.

## Important Notes

This is a **Week 7 provisional dataset**, not the final training or production corpus.

The raw files should remain available for traceability and future corrections. Any editorial review documents must remain separate from the retrieval corpus.

The Week 8 dataset will build on this initial sample and provide updated, validated chunks for the RAG pipeline.
