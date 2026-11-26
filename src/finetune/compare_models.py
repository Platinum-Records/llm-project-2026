"""Week 8 model comparison: candidate SLMs with and without retrieved context.

Runs every validated dev item of the Golden Dataset (generation and dialect_qa)
through each candidate model twice: without context ("no_rag") and with the
top-3 chunks from the Week 8 BGE-M3 baseline ("rag"). Outputs are scored
automatically with the project's MCP tools; dialect correctness and theme /
meaning scores still need the judge or a human (docs/evaluation-criteria.md).

Needs a GPU (Colab T4) and Hugging Face access; Gemma requires accepting its
terms and a token. Use the dev split only: the test split is locked.

    python -m src.finetune.compare_models                 # full run
    python -m src.finetune.compare_models --limit 2       # quick smoke test
    python -m src.finetune.compare_models --dry-run       # no models, checks the pipeline
"""
import argparse
import datetime as dt
import gc
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "data/eval/golden_v1.jsonl"
CHUNKS = ROOT / "data/processed/chunks.jsonl"
OUTPUT = ROOT / "eval/results/week8_model_comparison"

MODELS = {
    "qwen3-4b": "Qwen/Qwen3-4B-Instruct-2507",
    "gemma3-4b": "google/gemma-3-4b-it",
}
CONDITIONS = ("no_rag", "rag")
TASKS = ("generation", "dialect_qa")
CONTEXT_K = 3
# dialect_qa cap is fixed by the evaluation criteria; generation uses one common cap.
MAX_NEW_TOKENS = {"generation": 200, "dialect_qa": 300}

INSTRUCTION = ("Ești un asistent care scrie poezie populară ardelenească și rap ardelenesc "
               "și explică regionalisme. Răspunde în limba română.")

# Validated dialect list (docs/evaluation-criteria.md §5), with the word forms
# accepted when counting regional terms automatically. This is an approximation
# until the dialect_lookup tool exists; borderline cases are reviewed manually.
DIALECT_TERMS = {
    "bade": r"\bbad(e|ea|iu)\b|\bbădi",
    "pită": r"\bpit(ă|a|e|ei)\b",
    "no, bine": r"\bno,? bine\b",
    "curechi": r"\bcurech",
    "cocon": r"\bcocon",
    "a se hodini": r"\bhodin",
    "fain": r"\bfain",
    "oleacă": r"\bolea(că|ca)\b",
    "a sta la povești": r"\bla povești\b",
    "mândru": r"\bmândr",
    "lele": r"\blele(a|i)?\b",
    "nime": r"\bnime\b",
    "de urât": r"\bde ur[âî]t\b",
    "ibovnic": r"\bibovnic",
    "șurț": r"\bșurț",
    "chică": r"\bchic(ă|a)\b",
    "rujă": r"\bruj(ă|a|e)\b",
    "scoverzi": r"\bscov[ae]r",
    "a omeni": r"\bomen(i|it|esc|ește)\b",
    "cioareci": r"\bcioarec",
}


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]


def load_items(split="dev", limit=None):
    """Validated items of the requested split, generation and dialect_qa only."""
    items = [row for row in read_jsonl(GOLDEN)
             if row["split"] == split and row["status"] == "validated" and row["task"] in TASKS]
    if split != "dev":
        raise ValueError("Only the dev split may be used for this comparison.")
    if limit:
        per_task = {task: [r for r in items if r["task"] == task][:limit] for task in TASKS}
        items = [r for task in TASKS for r in per_task[task]]
    return items


def verse_lines(text):
    """Lines of the poem itself: drops preambles ending in ':', notes and markdown."""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("* ", "- ", "— ", "• ", "#", "(", "[")):
            continue  # bullets, headings and notes
        line = line.strip("*_").strip()  # markdown bold / italics around a verse
        if not line or line.endswith(":"):
            continue
        lines.append(line)
    return lines


def regional_terms(text):
    lowered = text.lower()
    return sorted(term for term, pattern in DIALECT_TERMS.items() if re.search(pattern, lowered))


def score_generation(item, text):
    from mcp_server.rhyme_checker import rhyme_checker
    from mcp_server.syllable_counter import syllable_counter

    c = item["constraints"]
    lines = verse_lines(text)
    counts = [row["syllables"] for row in syllable_counter("\n".join(lines))["lines"]]
    in_range = [c["syllables"]["min"] <= n <= c["syllables"]["max"] for n in counts]
    syllable_accuracy = sum(in_range) / len(in_range) if in_range else 0.0
    try:
        rhyme = rhyme_checker("\n".join(lines), c["scheme"])
        rhyme_match, found_scheme = bool(rhyme["matches_expected"]), rhyme["scheme"]
    except ValueError:  # wrong number of lines for the scheme, or no final vowel
        rhyme_match, found_scheme = False, None
    terms = regional_terms("\n".join(lines))
    line_count_ok = len(lines) == c["lines"]
    regional_ok = len(terms) >= c["dialect_terms_min"]
    return {
        "verse_lines": len(lines),
        "line_count_ok": line_count_ok,
        "syllables_per_line": counts,
        "syllable_accuracy": round(syllable_accuracy, 4),
        "rhyme_scheme_found": found_scheme,
        "rhyme_match": rhyme_match,
        "regional_terms": terms,
        "regional_ok": regional_ok,
        "structural_pass": line_count_ok and syllable_accuracy >= 0.75 and rhyme_match and regional_ok,
    }


def token_f1(answer, reference):
    """Word-overlap F1 with the reference answer: a rough proxy, not a correctness score."""
    words = lambda s: re.findall(r"[^\W\d_]+", (s or "").lower())
    a, r = words(answer), words(reference)
    common = sum(min(a.count(w), r.count(w)) for w in set(a))
    if not a or not r or not common:
        return 0.0
    precision, recall = common / len(a), common / len(r)
    return round(2 * precision * recall / (precision + recall), 4)


def score_dialect(item, text, retrieved_ids):
    expected = set(item["expected_chunks"])
    return {
        "answer_words": len(text.split()),
        "token_f1_proxy": token_f1(text, item["expected_answer"]),
        "grounding_hit": (bool(expected & set(retrieved_ids)) if expected and retrieved_ids is not None
                          else None),
        "correctness": None,  # filled by the LLM judge / human review (criteria §3)
    }


def build_message(item, context):
    if item["task"] == "generation":
        c = item["constraints"]
        word = "cuvânt regional" if c["dialect_terms_min"] == 1 else "cuvinte regionale"
        task = (f"{item['prompt']}\nCerințe: {c['lines']} versuri, {c['syllables']['min']}–"
                f"{c['syllables']['max']} silabe pe vers, rimă {c['scheme']}, cel puțin "
                f"{c['dialect_terms_min']} {word}. Scrie doar versurile, fără explicații.")
        header = "Fragmente din corpus (folosește-le ca inspirație și ca sursă de cuvinte regionale):"
    else:
        task = f"{item['prompt']}\nRăspunde pe scurt, în una sau două propoziții."
        header = "Fragmente din corpus care pot conține cuvântul:"
    parts = [INSTRUCTION]
    if context:
        parts.append(header + "\n" + "\n\n".join(
            f"[{n}] {chunk['text']}" for n, chunk in enumerate(context, 1)))
    parts.append(task)
    # System text is folded into the user turn so every model gets identical input.
    return [{"role": "user", "content": "\n\n".join(parts)}]


def build_contexts(items, retriever):
    """Retrieve once per item so both models see exactly the same context."""
    contexts = {}
    for item in items:
        mode = item["mode"] if item["task"] == "generation" else None
        hits = retriever.retrieve(item["prompt"], mode=mode, limit=CONTEXT_K)
        contexts[item["id"]] = [{"id": h["id"], "text": h["text"], "score": h.get("score")}
                                for h in hits]
    return contexts


def make_retriever():
    """The RAG Lead's Week 8 baseline, with an in-memory Qdrant (no server needed)."""
    from qdrant_client import QdrantClient
    from src.rag.baseline import DEFAULT_DATA, BaselineRetriever

    class InMemoryRetriever(BaselineRetriever):
        def __init__(self, data_path=DEFAULT_DATA):
            self.data = Path(data_path).read_bytes()
            self.collection = f"week8_bge_m3_{hashlib.sha256(self.data).hexdigest()[:16]}"
            self.client = QdrantClient(":memory:")
            self.model = None

    retriever = InMemoryRetriever()
    retriever.ingest()
    return retriever


class HFGenerator:
    """Greedy decoding with a Hugging Face chat model in BF16 on the GPU."""

    def __init__(self, model_id):
        import torch
        from huggingface_hub import model_info
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.revision = model_info(model_id).sha
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=self.revision)
        options = {"revision": self.revision, "dtype": torch.bfloat16, "device_map": "cuda"}
        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_id, **options)
        except ValueError:  # Gemma 3 4B is registered as an image-text-to-text model
            from transformers import AutoModelForImageTextToText
            self.model = AutoModelForImageTextToText.from_pretrained(model_id, **options)
        self.model.eval()

    def __call__(self, messages, max_new_tokens):
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True,
        ).to(self.model.device)
        pad = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        with self.torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens,
                                         do_sample=False, pad_token_id=pad)
        new_tokens = output[0, inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip(), len(new_tokens)

    def close(self):
        del self.model
        gc.collect()
        self.torch.cuda.empty_cache()


class DryRunGenerator:
    """Stand-in for a model: returns a fixed verse or answer, to test the pipeline."""
    revision = "dry-run"

    def __call__(self, messages, max_new_tokens):
        if "Cerințe:" in messages[-1]["content"]:
            return "Bate vântul peste sat\nLuna urcă peste deal\nPe cărare s-a-nnoptat\nPită caldă pe-un tăiat", 20
        return "Înseamnă pâine.", 4

    def close(self):
        pass


class DryRunRetriever:
    """Stand-in for BGE-M3: returns the first chunks of the requested mode."""

    def __init__(self):
        self.chunks = read_jsonl(CHUNKS)

    def retrieve(self, query, mode=None, limit=5):
        return [c for c in self.chunks if mode in (None, c["mode"])][:limit]


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 4) if values else None


def summarize(rows):
    summary = {}
    for row in rows:
        group = row["task"] if row["task"] == "dialect_qa" else f"generation/{row['mode']}"
        summary.setdefault(group, []).append(row)
    out = {}
    for group, items in sorted(summary.items()):
        s = [r["scores"] for r in items]
        stats = {"items": len(items),
                 "hit_token_limit": sum(r["hit_token_limit"] for r in items),
                 "mean_generation_seconds": mean([r["seconds"] for r in items])}
        if group.startswith("generation"):
            stats.update({
                "structural_pass_rate": mean([float(x["structural_pass"]) for x in s]),
                "line_count_ok_rate": mean([float(x["line_count_ok"]) for x in s]),
                "mean_syllable_accuracy": mean([x["syllable_accuracy"] for x in s]),
                "rhyme_match_rate": mean([float(x["rhyme_match"]) for x in s]),
                "regional_ok_rate": mean([float(x["regional_ok"]) for x in s]),
                "mean_regional_terms": mean([float(len(x["regional_terms"])) for x in s]),
            })
        else:
            stats.update({
                "mean_token_f1_proxy": mean([x["token_f1_proxy"] for x in s]),
                "grounding_hit_rate": mean([None if x["grounding_hit"] is None else float(x["grounding_hit"])
                                            for x in s]),
                "mean_answer_words": mean([float(x["answer_words"]) for x in s]),
            })
        out[group] = stats
    return out


def markdown_table(summary):
    lines = ["| Model | Condition | Group | Items | Structural pass | Syllable acc. | Rhyme match | "
             "Regional OK | Token-F1 (proxy) | Grounding hit | Hit token limit |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    fmt = lambda v: "–" if v is None else (f"{v:.0%}" if isinstance(v, float) and v <= 1 else str(v))
    for key, groups in summary.items():
        model, condition = key.split("__")
        for group, s in groups.items():
            lines.append("| " + " | ".join([
                model, condition, group, str(s["items"]),
                fmt(s.get("structural_pass_rate")), fmt(s.get("mean_syllable_accuracy")),
                fmt(s.get("rhyme_match_rate")), fmt(s.get("regional_ok_rate")),
                fmt(s.get("mean_token_f1_proxy")), fmt(s.get("grounding_hit_rate")),
                str(s["hit_token_limit"])]) + " |")
    return "\n".join(lines)


def run(models, limit=None, dry_run=False, output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    items = load_items(limit=limit)
    retriever = DryRunRetriever() if dry_run else make_retriever()
    contexts = build_contexts(items, retriever)
    del retriever
    gc.collect()
    (output / "contexts.json").write_text(json.dumps(contexts, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8")
    summary, settings = {}, {"models": {}}
    for name in models:
        generator = DryRunGenerator() if dry_run else HFGenerator(MODELS[name])
        settings["models"][name] = {"id": MODELS[name], "revision": generator.revision}
        for condition in CONDITIONS:
            rows = []
            for item in items:
                context = contexts[item["id"]] if condition == "rag" else []
                cap = MAX_NEW_TOKENS[item["task"]]
                start = time.perf_counter()
                text, n_tokens = generator(build_message(item, context), cap)
                seconds = round(time.perf_counter() - start, 2)
                retrieved = [c["id"] for c in context] if condition == "rag" else None
                scores = (score_generation(item, text) if item["task"] == "generation"
                          else score_dialect(item, text, retrieved))
                rows.append({"id": item["id"], "task": item["task"], "mode": item["mode"],
                             "model": name, "condition": condition, "output": text,
                             "generated_tokens": n_tokens, "hit_token_limit": n_tokens >= cap,
                             "seconds": seconds, "retrieved_ids": retrieved, "scores": scores})
            with (output / f"{name}__{condition}.jsonl").open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            summary[f"{name}__{condition}"] = summarize(rows)
            print(f"{name} / {condition}: {len(rows)} items done", flush=True)
        generator.close()

    settings.update(_environment(dry_run))
    settings.update({
        "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "split": "dev", "items": len(items), "limit_per_task": limit, "dry_run": dry_run,
        "decoding": "greedy (do_sample=False)", "dtype": "bfloat16",
        "max_new_tokens": MAX_NEW_TOKENS, "context_k": CONTEXT_K,
        "golden_sha256": hashlib.sha256(GOLDEN.read_bytes()).hexdigest(),
        "corpus_sha256": hashlib.sha256(CHUNKS.read_bytes()).hexdigest(),
    })
    (output / "summary.json").write_text(
        json.dumps({"settings": settings, "results": summary}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    table = markdown_table(summary)
    (output / "summary.md").write_text(table + "\n", encoding="utf-8")
    print(table)
    return summary


def _environment(dry_run):
    if dry_run:
        return {"gpu": None}
    import torch
    import transformers
    return {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "torch": torch.__version__, "transformers": transformers.__version__}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", choices=sorted(MODELS), default=list(MODELS))
    parser.add_argument("--limit", type=int, help="Run only the first N items per task.")
    parser.add_argument("--dry-run", action="store_true", help="No models; checks the pipeline.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    run(args.models, args.limit, args.dry_run, args.output)


if __name__ == "__main__":
    main()
