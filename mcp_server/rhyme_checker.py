"""Conservative spelling-based Romanian end-rhyme estimates, not phonetic analysis."""

import re
from typing import TypedDict
from unicodedata import normalize


class RhymeLine(TypedDict):
    line_number: int
    word: str
    ending: str
    group: str


class RhymeResult(TypedDict):
    lines: list[RhymeLine]
    scheme: str
    matches_expected: bool | None
    quality: str


def _ending(word: str) -> str:
    # Treat final whispered i as nonsyllabic, except after consonant+r/l.
    if (len(word) > 1 and word.endswith("i") and word[-2] not in "aeiouăâî"
            and not re.search(r"[b-dfghptv][lr]i$", word)):
        word = word[:-1]
    nuclei = list(re.finditer(r"[aeiouăâî]+", word))
    if not nuclei:
        return word
    # Approximate penultimate stress for vowel-final words, final otherwise.
    index = -2 if word[-1] in "aeiouăâî" and len(nuclei) > 1 else -1
    return word[nuclei[index].start():]


def rhyme_checker(text: str, expected_scheme: str | None = None) -> RhymeResult:
    """Estimate end-rhyme groups; optionally compare an AABB/ABAB-style scheme.

    Blank lines are skipped. Quality is an orthographic estimate: repeated
    end words are marked separately. Stress, dialect and performance need review.
    """
    lines: list[RhymeLine] = []
    groups: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        spelling = normalize("NFC", line).lower().translate(str.maketrans("şţ", "șț"))
        words = re.findall(r"[^\W\d_]+", spelling)
        if not words or not any(v in words[-1] for v in "aeiouăâî"):
            raise ValueError(f"Line {number} must end in a word containing a Romanian vowel.")
        ending = _ending(words[-1])
        if ending not in groups:
            if len(groups) == 26:
                raise ValueError("At most 26 distinct rhyme groups are supported.")
            groups[ending] = chr(ord("A") + len(groups))
        lines.append({"line_number": number, "word": words[-1],
                      "ending": ending, "group": groups[ending]})
    scheme = "".join(line["group"] for line in lines)
    matches = None
    if expected_scheme is not None:
        expected = "".join(expected_scheme.upper().split())
        if len(expected) != len(lines) or not re.fullmatch(r"[A-Z]*", expected):
            raise ValueError("Expected scheme must have one A-Z letter per nonblank line.")
        labels: dict[str, str] = {}
        canonical = "".join(labels.setdefault(c, chr(65 + len(labels))) for c in expected)
        matches = scheme == canonical
    repeated_groups = [g for g in groups.values() if scheme.count(g) > 1]
    quality = "no_rhyme"
    if repeated_groups:
        quality = "estimated_rhyme"
        if any(len({line["word"] for line in lines if line["group"] == g}) == 1
               for g in repeated_groups):
            quality = "repeated_end_word"
    return {"lines": lines, "scheme": scheme,
            "matches_expected": matches, "quality": quality}
