import json

import pytest

from src.finetune import compare_models as cm


def test_load_items_uses_only_validated_dev_generation_and_dialect():
    items = cm.load_items()
    assert items and all(i["split"] == "dev" and i["status"] == "validated" for i in items)
    assert {i["task"] for i in items} == {"generation", "dialect_qa"}
    with pytest.raises(ValueError):
        cm.load_items(split="test")


def test_verse_lines_drops_preamble_and_notes():
    text = ("Sigur, iată poezia:\n\n**Bate vântul peste sat**\nLuna urcă peste deal\n"
            "(Termeni regionali: pită)\n* notă")
    assert cm.verse_lines(text) == ["Bate vântul peste sat", "Luna urcă peste deal"]


def test_regional_terms_match_inflected_forms_only():
    assert cm.regional_terms("Badea mănâncă pită și curechi") == ["bade", "curechi", "pită"]
    assert cm.regional_terms("oamenii au omenie, pădurea e mare") == []


def test_score_generation_structural_pass():
    item = {"constraints": {"lines": 4, "syllables": {"min": 7, "max": 8}, "scheme": "AABB",
                            "theme": "t", "dialect_terms_min": 2}}
    verse = ("Bate vântul peste sat\nPită caldă s-a-ntâmplat\n"
             "Badea vine de la deal\nCu curechi pân-la Ardeal")
    s = cm.score_generation(item, verse)
    assert s["line_count_ok"] and s["rhyme_match"] and s["regional_ok"]
    assert s["syllable_accuracy"] >= 0.75 and s["structural_pass"]


def test_score_generation_wrong_line_count_is_not_an_error():
    item = {"constraints": {"lines": 4, "syllables": {"min": 7, "max": 8}, "scheme": "ABAB",
                            "theme": "t", "dialect_terms_min": 2}}
    s = cm.score_generation(item, "Un singur vers aici")
    assert s["line_count_ok"] is False and s["rhyme_match"] is False and not s["structural_pass"]


def test_token_f1_proxy():
    assert cm.token_f1("Nimeni.", "Nimeni.") == 1.0
    assert cm.token_f1("altceva", "Nimeni.") == 0.0


def test_same_task_text_with_and_without_context():
    item = next(i for i in cm.load_items() if i["task"] == "generation")
    plain = cm.build_message(item, [])[0]["content"]
    rag = cm.build_message(item, [{"id": "x", "text": "Frunză verde"}])[0]["content"]
    assert rag.endswith(plain.split("\n\n", 1)[1]) and "[1] Frunză verde" in rag


def test_dry_run_writes_outputs(tmp_path):
    cm.run(["qwen3-4b"], limit=1, dry_run=True, output=tmp_path)
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert set(summary["results"]) == {"qwen3-4b__no_rag", "qwen3-4b__rag"}
    assert (tmp_path / "qwen3-4b__rag.jsonl").exists() and (tmp_path / "summary.md").exists()
