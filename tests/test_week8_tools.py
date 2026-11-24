import asyncio
import importlib
import json
import sys
from pathlib import Path
from unicodedata import normalize

import pytest
from mcp import Client, StdioServerParameters
from qdrant_client import QdrantClient

from mcp_server.rhyme_checker import rhyme_checker
from src.rag import baseline

retrieval = importlib.import_module("mcp_server.retrieve_context")


@pytest.mark.parametrize(("text", "scheme", "quality"), [
    ("Un sat!\nUn dor\nAm cântat\nUn izvor", "ABAB", "estimated_rhyme"),
    ("Un dor\nUn izvor\nUn sat\nAm cântat", "AABB", "estimated_rhyme"),
    ("În pădure\nCu iubire", "AB", "no_rhyme"),
    ("Un sat\nTot sat", "AA", "repeated_end_word"),
    ("\n", "", "no_rhyme"),
])
def test_rhyme_schemes(text, scheme, quality):
    result = rhyme_checker(text, scheme)
    assert result["scheme"] == scheme
    assert result["matches_expected"] is True
    assert result["quality"] == quality


def test_rhyme_normalization_and_expected_scheme():
    result = rhyme_checker(normalize("NFD", "PAŞI!\n\nGingași."), "B B")
    assert result["scheme"] == "AA"
    assert [line["line_number"] for line in result["lines"]] == [1, 3]
    assert result["lines"][0]["ending"] == "aș"
    assert rhyme_checker("sat\ndor", "AA")["matches_expected"] is False
    assert rhyme_checker("sat")["matches_expected"] is None


@pytest.mark.parametrize(("text", "scheme"), [
    ("sat", "AB"), ("sat", "1"), ("123", None), ("!!!", None),
])
def test_invalid_rhyme_input(text, scheme):
    with pytest.raises(ValueError):
        rhyme_checker(text, scheme)


@pytest.fixture
def local_retriever(tmp_path, monkeypatch):
    data = tmp_path / "chunks.jsonl"
    chunks = [
        {"id": "folk-1", "text": "Un dor", "mode": "folk", "source_id": "original"},
        {"id": "rap-1", "text": "Un sat", "mode": "rap", "source_id": "original"},
    ]
    data.write_text("\n".join(json.dumps(chunk) for chunk in chunks), encoding="utf-8")
    client = QdrantClient(":memory:")
    monkeypatch.setattr(baseline, "QdrantClient", lambda **kwargs: client)
    # Deterministic embedding stand-in: exercise the real baseline and Qdrant,
    # without a model download. This is not a semantic quality evaluation.
    class Vector(list):
        def tolist(self):
            return list(self)

    retriever = baseline.BaselineRetriever(data)
    monkeypatch.setattr(retriever, "_encode", lambda texts: (
        [Vector([1.0] + [0.0] * 1023) for _ in texts]
        if isinstance(texts, list) else Vector([1.0] + [0.0] * 1023)
    ))
    monkeypatch.setattr(retrieval, "_get_retriever", lambda: retriever)
    assert retriever.ingest() == 2
    yield retriever
    client.close()


def test_retrieval_uses_real_baseline_with_filter_and_payload(local_retriever):
    hits = retrieval.retrieve_context("dor", "folk")["chunks"]
    assert len(hits) == 1
    assert hits[0]["id"] == "folk-1"
    assert hits[0]["source_id"] == "original"
    assert hits[0]["score"] == pytest.approx(1.0)
    assert len(retrieval.retrieve_context("sat")["chunks"]) == 2
    assert len(retrieval.retrieve_context("sat", limit=1)["chunks"]) == 1
    local_retriever.client.delete_collection(local_retriever.collection)
    with pytest.raises(RuntimeError, match="Ingest"):
        retrieval.retrieve_context("dor")


def test_empty_retrieval_results(local_retriever):
    local_retriever.client.delete(
        local_retriever.collection,
        points_selector=baseline.models.FilterSelector(filter=baseline.models.Filter(
            must=[baseline.models.FieldCondition(key="mode", match=baseline.models.MatchValue(value="rap"))]
        )), wait=True,
    )
    assert retrieval.retrieve_context("sat", "rap") == {"chunks": []}


@pytest.mark.parametrize("kwargs", [
    {"query": " "}, {"query": "dor", "mode": "other"},
    {"query": "dor", "limit": 0}, {"query": "dor", "limit": 21},
    {"query": "dor", "limit": True}, {"query": "dor", "limit": 1.5},
])
def test_invalid_retrieval_does_not_initialize_backend(kwargs, monkeypatch):
    def unexpected():
        pytest.fail("Invalid requests must not initialize retrieval")
    monkeypatch.setattr(retrieval, "_get_retriever", unexpected)
    with pytest.raises(ValueError):
        retrieval.retrieve_context(**kwargs)


def test_retriever_is_initialized_once(monkeypatch):
    retrieval._get_retriever.cache_clear()
    calls = []
    monkeypatch.setenv("QDRANT_URL", "http://example.invalid:6333")
    monkeypatch.setenv("RAG_DATA_PATH", "custom.jsonl")
    monkeypatch.setattr(baseline, "BaselineRetriever", lambda **kwargs: calls.append(kwargs) or object())
    try:
        assert retrieval._get_retriever() is retrieval._get_retriever()
        assert calls == [{"data_path": "custom.jsonl", "url": "http://example.invalid:6333"}]
    finally:
        retrieval._get_retriever.cache_clear()


def test_retrieval_through_mcp(local_retriever):
    from mcp_server.server import server

    async def check():
        async with Client(server) as client:
            result = await client.call_tool("retrieve_context", {"query": "dor", "mode": "folk"})
            assert not result.is_error
            assert result.structured_content["chunks"][0]["id"] == "folk-1"
    asyncio.run(asyncio.wait_for(check(), 20))


def test_week8_stdio_tools_and_errors():
    async def check():
        params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"],
                                       cwd=Path(__file__).resolve().parents[1])
        async with Client(params) as client:
            result = await client.call_tool("rhyme_checker", {"text": "Un sat\nAm cântat", "expected_scheme": "AA"})
            assert not result.is_error
            assert result.structured_content["matches_expected"] is True
            for arguments in ({"query": " "}, {"query": "dor", "mode": "other"}):
                result = await client.call_tool("retrieve_context", arguments)
                assert result.is_error
    asyncio.run(asyncio.wait_for(check(), 20))
