"""Validate the Golden Dataset file.

Checks that every line is valid JSON, that all records share the same fields,
that IDs are unique, that task/mode/status values are allowed, that each task
type has the constraints it needs, and that every `expected_chunks` ID exists
in the processed corpus.

Usage (from the repository root):
    python eval/validate_golden.py [path/to/golden.jsonl] [path/to/chunks.jsonl]
"""
import json
import sys
from collections import Counter
from pathlib import Path

GOLDEN = Path(sys.argv[1] if len(sys.argv) > 1 else "data/eval/golden_v1_draft.jsonl")
CHUNKS = Path(sys.argv[2] if len(sys.argv) > 2 else "data/processed/chunks.jsonl")

FIELDS = ["id", "task", "mode", "prompt", "prompt_en", "expected_answer", "expected_answer_en",
          "expected_chunks", "constraints", "reference", "status", "notes"]
TASKS = {"dialect_qa", "retrieval", "generation"}
MODES = {None, "folk", "rap"}
STATUSES = {"draft", "pending_dialect_validation", "needs_answer", "validated"}
GENERATION_CONSTRAINTS = {"lines", "syllables", "scheme", "theme", "dialect_terms_min"}


def main() -> int:
    errors = []
    chunk_ids = {json.loads(l)["id"] for l in CHUNKS.open(encoding="utf-8") if l.strip()}
    rows = []
    for n, line in enumerate(GOLDEN.open(encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            errors.append(f"line {n}: invalid JSON ({e})")

    for dup, c in Counter(r.get("id") for r in rows).items():
        if c > 1:
            errors.append(f"duplicate id {dup}")

    for r in rows:
        rid = r.get("id", "?")
        if list(r) != FIELDS:
            errors.append(f"{rid}: fields {list(r)} != expected {FIELDS}")
        if r.get("task") not in TASKS:
            errors.append(f"{rid}: unknown task {r.get('task')!r}")
        if r.get("mode") not in MODES:
            errors.append(f"{rid}: unknown mode {r.get('mode')!r}")
        if r.get("status") not in STATUSES:
            errors.append(f"{rid}: unknown status {r.get('status')!r}")
        for c in r.get("expected_chunks", []):
            if c not in chunk_ids:
                errors.append(f"{rid}: expected chunk {c} not found in {CHUNKS}")
        if r.get("task") == "generation":
            missing = GENERATION_CONSTRAINTS - set(r.get("constraints", {}))
            if missing:
                errors.append(f"{rid}: missing generation constraints {sorted(missing)}")
        if r.get("task") == "retrieval" and not r.get("expected_chunks"):
            print(f"warning: {rid} has no expected_chunks (see notes: {r.get('notes')})")
        if r.get("task") == "dialect_qa" and r.get("expected_answer") is None:
            print(f"warning: {rid} has no expected_answer yet")

    print(f"{len(rows)} records:", dict(Counter(r.get('task') for r in rows)),
          "| status:", dict(Counter(r.get('status') for r in rows)))
    for e in errors:
        print("ERROR:", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
