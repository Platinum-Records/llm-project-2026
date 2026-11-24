"""Week 8 dense retrieval with BGE-M3 and Qdrant."""

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models


DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data/processed/chunks.jsonl"
MODES = ("folk", "rap")
MODEL_ID = "BAAI/bge-m3"
MODEL_REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
VECTOR_SIZE = 1024


class BaselineRetriever:
    """Reuse one instance across queries to keep the embedding model loaded."""

    def __init__(self, data_path=DEFAULT_DATA, url="http://localhost:6333"):
        self.data = Path(data_path).read_bytes()
        digest = hashlib.sha256(self.data).hexdigest()
        self.collection = f"week8_bge_m3_{digest[:16]}"
        self.client = QdrantClient(url=url)
        self.model = None

    def _encode(self, texts):
        if self.model is None:
            os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
            from sentence_transformers import SentenceTransformer

            model_options = {"revision": MODEL_REVISION, "device": "cpu"}
            try:
                self.model = SentenceTransformer(
                    MODEL_ID, local_files_only=True, **model_options
                )
            except OSError:
                self.model = SentenceTransformer(MODEL_ID, **model_options)
        return self.model.encode(texts, batch_size=2, normalize_embeddings=True)

    def ingest(self):
        """Index the full corpus and return the number of indexed fragments."""
        chunks = [json.loads(line) for line in self.data.decode("utf-8").split("\n")
                  if line.strip()]
        ids = {chunk["id"] for chunk in chunks}
        if not chunks or len(ids) != len(chunks):
            raise ValueError("Corpus must contain at least one chunk and unique IDs.")
        for chunk in chunks:
            if not chunk["text"].strip() or chunk["mode"] not in MODES:
                raise ValueError(f"Invalid text or mode for chunk {chunk['id']}.")

        vectors = self._encode([chunk["text"] for chunk in chunks])
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE, distance=models.Distance.COSINE
                ),
            )
        points = [
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["id"])),
                vector=vector.tolist(),
                payload=chunk,
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(self.collection, points, wait=True)
        count = self.client.count(self.collection, exact=True).count
        if count != len(chunks):
            raise RuntimeError(f"Expected {len(chunks)} indexed chunks, found {count}.")
        return count

    def retrieve(self, query, *, mode=None, limit=5):
        """Return ranked payloads with scores, optionally limited to one mode."""
        if not query.strip() or limit < 1:
            raise ValueError("Provide a nonempty query and a positive limit.")
        if mode is not None and mode not in MODES:
            raise ValueError("Mode must be folk, rap or None.")
        if not self.client.collection_exists(self.collection):
            raise RuntimeError("Ingest this corpus before running retrieval.")

        return self._search(self._encode(query).tolist(), mode=mode, limit=limit)

    def _search(self, vector, *, mode, limit):
        query_filter = None
        if mode is not None:
            query_filter = models.Filter(
                must=[models.FieldCondition(key="mode", match=models.MatchValue(value=mode))]
            )
        hits = self.client.query_points(
            self.collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        ).points
        return [{**hit.payload, "score": hit.score} for hit in hits]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--url", default="http://localhost:6333")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest")
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--mode", choices=MODES)
    search.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    retriever = BaselineRetriever(args.data, args.url)
    if args.command == "ingest":
        print(f"Indexed {retriever.ingest()} chunks in {retriever.collection}.")
    else:
        hits = retriever.retrieve(args.query, mode=args.mode, limit=args.limit)
        print(json.dumps(hits, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
