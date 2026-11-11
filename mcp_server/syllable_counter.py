"""Rule-based estimates for Romanian verse in standard spelling."""

import re
from typing import TypedDict
from unicodedata import normalize


class LineCount(TypedDict):
    line_number: int
    text: str
    syllables: int


class SyllableCount(TypedDict):
    lines: list[LineCount]


_VOWELS = "aeiouăâî"
_WORD = re.compile(r"[^\W\d_]+")
_NUCLEUS = re.compile(
    r"eai|eau|iai|iau|iei|ieu|ioi|oai|"
    rf"ea|ia|(?<=[{_VOWELS}])ie|ie(?!$)|io|iu|oa|ua|uă|"
    r"ai|au|ăi|ău|âi|âu|ei|eu|ii|oi|ou|ui|"
    rf"[{_VOWELS}]"
)
_VOCAL_FINAL_I = re.compile(r"[b-dfghptv][lr]i$")
_EXCEPTIONS = {  # Ambiguous written vowel groups and a few common loanwords.
    "aer": 2,
    "pian": 2,
    "taxi": 2,
    "ziar": 2,
}
_SPELLING_VARIANTS = str.maketrans("şţ‐‑", "șț--")
_CLITIC_BEFORE_VOWEL = re.compile(r"\b(mi|ți|și|i|li|ni|vi|ne|le|se|te)-(a|ai|au|am|ați|aș|ar|o)\b")
_CLITIC_I = re.compile(rf"([{_VOWELS}])-i\b")


def _count_word(word: str) -> int:
    if word in _EXCEPTIONS:
        return _EXCEPTIONS[word]
    if (
        len(word) > 1
        and word.endswith("i")
        and word[-2] not in _VOWELS
        and not _VOCAL_FINAL_I.search(word)
        and any(letter in _VOWELS for letter in word[:-1])
    ):
        # A final whispered i does not add a syllable (pomi, pași).
        word = word[:-1]
    return sum(1 for _ in _NUCLEUS.finditer(word))


def syllable_counter(text: str) -> SyllableCount:
    """Estimate Romanian syllables per line; preserve blank lines and original text."""
    lines: list[LineCount] = []
    for number, line in enumerate(text.splitlines(), start=1):
        spelling = normalize("NFC", line).lower().translate(_SPELLING_VARIANTS)
        spelling = _CLITIC_BEFORE_VOWEL.sub(r"\1\2", spelling)
        spelling = _CLITIC_I.sub(r"\1i", spelling)
        lines.append({
            "line_number": number,
            "text": line,
            "syllables": sum(_count_word(word) for word in _WORD.findall(spelling)),
        })
    return {"lines": lines}
