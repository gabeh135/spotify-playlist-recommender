from sentence_transformers import SentenceTransformer

# Loading once at import time avoids reloading on every request (~300ms cost).
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """Returns a 384-dim vector in the same space as track embeddings."""
    return _model.encode(text).tolist()
