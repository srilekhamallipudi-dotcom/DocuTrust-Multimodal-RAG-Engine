import sys
from sentence_transformers import SentenceTransformer
import hashlib

model = None

def load_model():
    global model
    if model is not None:
        return model
    
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded successfully")
        return model
    except Exception as e:
        print(f"⚠️ Warning: Could not load embedding model: {e}")
        print("   Using fallback hash-based embeddings")
        return None


def create_embeddings(chunks):
    """
    Create embeddings for text chunks. Uses SentenceTransformer if available,
    falls back to hash-based embeddings if model loading fails.
    """
    model_instance = load_model()
    
    if model_instance is not None:
        embeddings = model_instance.encode(chunks)
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return [list(map(float, x)) for x in embeddings]
    
    # Fallback: hash-based embeddings (deterministic, consistent)
    embeddings = []
    for chunk in chunks:
        hash_digest = hashlib.sha256(chunk.encode()).hexdigest()
        # Convert hex to float embeddings (384 dimensions like all-MiniLM-L6-v2)
        embedding = [float(int(hash_digest[i:i+2], 16)) / 255.0 for i in range(0, min(len(hash_digest), 384*2), 2)]
        # Pad if necessary
        while len(embedding) < 384:
            embedding.append(0.0)
        embeddings.append(embedding[:384])
    
    return embeddings


def get_embedding(text):
    """
    Get embedding for a single text (query).
    """
    model_instance = load_model()
    
    if model_instance is not None:
        embedding = model_instance.encode(text)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return list(map(float, embedding))
    
    # Fallback: hash-based embedding
    hash_digest = hashlib.sha256(text.encode()).hexdigest()
    embedding = [float(int(hash_digest[i:i+2], 16)) / 255.0 for i in range(0, min(len(hash_digest), 384*2), 2)]
    while len(embedding) < 384:
        embedding.append(0.0)
    return embedding[:384]