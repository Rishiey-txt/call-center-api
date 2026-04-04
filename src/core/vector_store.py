import hashlib
import re
from collections import Counter
from typing import List

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import numpy as np
from src.config import settings

_collection = None


class LightweightEmbeddingFunction(EmbeddingFunction):
    """
    A dependency-free embedding function based on character n-gram TF vectors.

    This avoids pulling in onnxruntime / torch (which add ~1-2 GB to the image)
    while still producing meaningful cosine-similarity rankings for short call
    transcripts.  Dimensionality is fixed at 512 so ChromaDB's HNSW index works
    correctly across restarts.
    """

    DIM = 512

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed(doc) for doc in input]

    def _embed(self, text: str) -> List[float]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()

        counts: Counter = Counter()
        # unigrams
        counts.update(tokens)
        # bigrams
        counts.update(f"{a}_{b}" for a, b in zip(tokens, tokens[1:]))

        vec = np.zeros(self.DIM, dtype=np.float32)
        for term, freq in counts.items():
            idx = int(hashlib.md5(term.encode()).hexdigest(), 16) % self.DIM
            vec[idx] += freq

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()


def init_vector_store():
    global _collection
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    ef = LightweightEmbeddingFunction()
    _collection = client.get_or_create_collection(
        name="call_transcripts",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

def store_transcript(call_id: str, transcript: str, metadata: dict) -> None:
    _collection.add(
        documents=[transcript],
        metadatas=[{
            "call_id": call_id,
            "language": metadata.get("language", ""),
            "payment": metadata.get("payment", ""),
            "sentiment": metadata.get("sentiment", ""),
        }],
        ids=[call_id]
    )

def search_similar(query: str, n_results: int = 3) -> list[dict]:
    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return results
