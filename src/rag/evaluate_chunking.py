"""Compare corpus chunks and fixed word windows on labeled development queries."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

from .baseline import DEFAULT_DATA, MODEL_ID, MODEL_REVISION, BaselineRetriever


GOLDEN_DATA = DEFAULT_DATA.parents[1] / "eval/golden_v1.jsonl"
WINDOW_WORDS = 16
TOP_K = 5


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n")
            if line.strip()]


def fixed_windows(chunks):
    for chunk in chunks:
        words = list(re.finditer(r"\S+", chunk["text"]))
        for start in range(0, len(words), WINDOW_WORDS):
            end = min(start + WINDOW_WORDS, len(words)) - 1
            yield {
                "id": f"{chunk['id']}/window-{start // WINDOW_WORDS + 1}",
                "parent_id": chunk["id"],
                "mode": chunk["mode"],
                "text": chunk["text"][words[start].start():words[end].end()],
            }


def score(retriever, examples, vectors, count):
    rows = []
    for example, vector in zip(examples, vectors, strict=True):
        hits = retriever._search(vector.tolist(), mode=None, limit=count)
        parents = list(dict.fromkeys(hit.get("parent_id", hit["id"]) for hit in hits))
        top_ids = parents[:TOP_K]
        expected = set(example["expected_chunks"])
        matching_ranks = [
            rank for rank, chunk_id in enumerate(top_ids, 1) if chunk_id in expected
        ]
        rows.append({
            "id": example["id"],
            "expected_ids": sorted(expected),
            "top_ids": top_ids,
            "hit": int(bool(matching_ranks)),
            "recall": len(matching_ranks) / len(expected),
            "reciprocal_rank": 1 / matching_ranks[0] if matching_ranks else 0,
        })
    return {
        "collection": retriever.collection,
        "indexed_chunks": count,
        "hit_rate_at_5": sum(row["hit"] for row in rows) / len(rows),
        "recall_at_5": sum(row["recall"] for row in rows) / len(rows),
        "mrr_at_5": sum(row["reciprocal_rank"] for row in rows) / len(rows),
        "queries": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    chunks = read_jsonl(DEFAULT_DATA)
    corpus_ids = {chunk["id"] for chunk in chunks}
    examples = [
        row for row in read_jsonl(GOLDEN_DATA)
        if row["split"] == "dev" and row["status"] == "validated"
        and row["expected_chunks"]
    ]
    if not examples or any(set(row["expected_chunks"]) - corpus_ids for row in examples):
        raise ValueError("Expected validated dev queries with labels in the corpus.")

    baseline = BaselineRetriever()
    baseline_count = baseline.ingest()
    vectors = baseline._encode([row["prompt"] for row in examples])
    with TemporaryDirectory() as directory:
        window_file = Path(directory) / "windows.jsonl"
        with window_file.open("w", encoding="utf-8") as file:
            for window in fixed_windows(chunks):
                file.write(json.dumps(window, ensure_ascii=False) + "\n")
        windows = BaselineRetriever(window_file)
        windows.model = baseline.model
        window_count = windows.ingest()
        report = {
            "model": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "corpus_sha256": hashlib.sha256(baseline.data).hexdigest(),
            "golden_sha256": hashlib.sha256(GOLDEN_DATA.read_bytes()).hexdigest(),
            "query_count": len(examples),
            "split": "dev",
            "mode_filter": None,
            "window_words": WINDOW_WORDS,
            "corpus_chunks": score(baseline, examples, vectors, baseline_count),
            "fixed_windows": score(windows, examples, vectors, window_count),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
