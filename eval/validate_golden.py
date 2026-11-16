"""Validate the Golden Dataset file.

Checks that every line is valid JSON, that all records share the same fields,
that IDs are unique, that task/mode/split/status values are allowed, that each
task type has the constraints it needs, that every `expected_chunks` ID exists
in the processed corpus, and that examples already exposed during development
are not in the locked test split.

Usage (from the repository root):
    python eval/validate_golden.py [path/to/golden.jsonl] [path/to/chunks.jsonl]

Without arguments it validates data/eval/golden_v1.jsonl if it exists,
otherwise data/eval/golden_v1_draft.jsonl.
"""
import json
import sys
from collections import Counter
from pathlib import Path

DEFAULT = Path("data/eval/golden_v1.jsonl")
if not DEFAULT.exists():
    DEFAULT = Path("data/eval/golden_v1_draft.jsonl")
GOLDEN = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
CHUNKS = Path(sys.argv[2] if len(sys.argv) > 2 else "data/processed/chunks.jsonl")

FIELDS = ["id", "task", "mode", "prompt", "prompt_en", "expected_answer", "expected_answer_en",
          "expected_chunks", "constraints", "reference", "split", "status", "notes"]
TASKS = {"dialect_qa", "retrieval", "generation"}
MODES = {None, "folk", "rap"}
SPLITS = {"dev", "test"}
STATUSES = {"draft", "pending_dialect_validation", "needs_answer", "validated"}
GENERATION_REQUIRED = {"lines", "syllables", "scheme", "theme", "dialect_terms_min"}
GENERATION_OPTIONAL = {"source_text"}
# Examples already used outside evaluation (Week 7 fine-tuning smoke tests): must stay in dev.
EXPOSED = {"g-001", "g-003", "g-004"}


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
        if r.get("split") not in SPLITS:
            errors.append(f"{rid}: unknown split {r.get('split')!r}")
        if r.get("status") not in STATUSES:
            errors.append(f"{rid}: unknown status {r.get('status')!r}")
        if rid in EXPOSED and r.get("split") == "test":
            errors.append(f"{rid}: already exposed during development, must be in dev split")
        for c in r.get("expected_chunks", []):
            if c not in chunk_ids:
                errors.append(f"{rid}: expected chunk {c} not found in {CHUNKS}")
        constraints = r.get("constraints", {})
        if r.get("task") == "generation":
            missing = GENERATION_REQUIRED - set(constraints)
            extra = set(constraints) - GENERATION_REQUIRED - GENERATION_OPTIONAL
            if missing:
                errors.append(f"{rid}: missing generation constraints {sorted(missing)}")
            if extra:
                errors.append(f"{rid}: unknown generation constraints {sorted(extra)}")
            syl = constraints.get("syllables")
            if not (isinstance(syl, dict) and set(syl) == {"min", "max"} and syl["min"] <= syl["max"]):
                errors.append(f"{rid}: syllables must be {{'min': int, 'max': int}} with min <= max")
        if r.get("task") == "retrieval" and not r.get("expected_chunks"):
            print(f"warning: {rid} has no expected_chunks (see notes: {r.get('notes')})")
        if r.get("task") == "dialect_qa" and r.get("expected_answer") is None:
            print(f"warning: {rid} has no expected_answer yet")

    print(f"{GOLDEN}: {len(rows)} records")
    print("  tasks: ", dict(Counter(f"{r.get('task')}/{r.get('mode')}" for r in rows)))
    print("  splits:", dict(Counter(r.get("split") for r in rows)))
    print("  status:", dict(Counter(r.get("status") for r in rows)))
    for e in errors:
        print("ERROR:", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
