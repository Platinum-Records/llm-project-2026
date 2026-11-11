import asyncio
import sys
from pathlib import Path
from unicodedata import normalize

import pytest
from mcp import Client, StdioServerParameters

from mcp_server.syllable_counter import syllable_counter


# Original verses, hand-scanned below. Slashes separate words and hyphens
# separate spoken syllables; the expected totals are independent of the tool.
@pytest.mark.parametrize(
    ("verse", "expected"),
    [
        ("Bate vântul peste sat", 7),  # ba-te / vân-tul / pes-te / sat
        ("Luna urcă peste deal", 7),  # lu-na / ur-că / pes-te / deal
        ("Pe cărare cresc bujori", 7),  # pe / că-ra-re / cresc / bu-jori
        ("Pomi înfloresc lângă râu", 7),  # pomi / în-flo-resc / lân-gă / râu
        ("Iarna bate la fereastră", 8),  # iar-na / ba-te / la / fe-reas-tră
        ("Mi-a cântat un pui de cuc", 7),  # mi_a / cân-tat / un / pui / de / cuc
        ("Cântă ploaia pe hotar", 7),  # cân-tă / ploa-ia / pe / ho-tar
        ("Aer rece peste câmp", 7),  # a-er / re-ce / pes-te / câmp
        ("Scriu poezie pe foi", 7),  # scriu / po-e-zi-e / pe / foi
        ("Codri verzi păzesc izvorul", 8),  # co-dri / verzi / pă-zesc / iz-vo-rul
        ("Vreau să zbor mai sus de nori", 7),  # vreau / să / zbor / mai / sus / de / nori
        ("Nu-i tăcere când bat tobe", 8),  # nu_i / tă-ce-re / când / bat / to-be
    ],
)
def test_hand_scanned_verses(verse: str, expected: int) -> None:
    assert syllable_counter(verse) == {
        "lines": [{"line_number": 1, "text": verse, "syllables": expected}],
    }


def test_preserves_lines_and_normalizes_only_for_counting() -> None:
    first = normalize("NFD", "  ŞI‑A ZIS!  ")
    assert syllable_counter(f"{first}\r\n\r\n42!?\r\n") == {
        "lines": [
            {"line_number": 1, "text": first, "syllables": 2},
            {"line_number": 2, "text": "", "syllables": 0},
            {"line_number": 3, "text": "42!?", "syllables": 0},
        ],
    }
    assert syllable_counter("") == {"lines": []}


def test_distinguishes_diphthongs_and_hiatus_in_common_words() -> None:
    result = syllable_counter("geam\ngeologie\niar\nziar")
    assert [line["syllables"] for line in result["lines"]] == [1, 5, 1, 2]


def test_tool_can_be_discovered_and_called_over_stdio() -> None:
    async def check() -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            cwd=Path(__file__).resolve().parents[1],
        )
        async with Client(params) as client:
            (tool,) = (await client.list_tools()).tools
            assert tool.name == "syllable_counter"
            assert tool.input_schema["properties"]["text"]["type"] == "string"
            result = await client.call_tool(tool.name, {"text": "Pomi\nUn râu"})
            assert not result.is_error
            assert result.structured_content == {
                "lines": [
                    {"line_number": 1, "text": "Pomi", "syllables": 1},
                    {"line_number": 2, "text": "Un râu", "syllables": 2},
                ],
            }

    asyncio.run(asyncio.wait_for(check(), timeout=20))
