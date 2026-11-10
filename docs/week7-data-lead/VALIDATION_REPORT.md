# Week 7 validation — 2026-11-09

Default command: `python src/clean.py`

```json
{
  "read": 60,
  "accepted": 60,
  "duplicates": 0,
  "invalid": 0,
  "unverified": 0
}
```

Approved-only test: `python src/clean.py --approved-only --output data/processed/chunks_approved_test.jsonl`

```json
{
  "read": 60,
  "accepted": 0,
  "duplicates": 0,
  "invalid": 0,
  "unverified": 60
}
```

All 60 provisional records have unique IDs and provisional status. No claims of final editorial or legal approval are made.
