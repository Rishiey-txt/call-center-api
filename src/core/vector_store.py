import chromadb
from sentence_transformers import SentenceTransformer
from src.config import settings

_embedder = None
_collection = None

def init_vector_store():
    global _embedder, _collection
    _embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    _collection = client.get_or_create_collection(
        name="call_transcripts",
        metadata={"hnsw:space": "cosine"}
    )

def store_transcript(call_id: str, transcript: str, metadata: dict) -> None:
    embedding = _embedder.encode(transcript).tolist()
    _collection.add(
        documents=[transcript],
        embeddings=[embedding],
        metadatas=[{
            "call_id": call_id,
            "language": metadata.get("language", ""),
            "payment": metadata.get("payment", ""),
            "sentiment": metadata.get("sentiment", ""),
        }],
        ids=[call_id]
    )
