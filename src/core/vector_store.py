import chromadb
from chromadb.utils import embedding_functions
from src.config import settings

_collection = None

def init_vector_store():
    global _collection
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
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
