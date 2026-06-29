import os
import uuid
import chromadb
from embeddings import get_embedding

# ==========================
# Chroma DB Setup
# ==========================
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

os.makedirs(DB_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="doctrust",
    metadata={"hnsw:space": "cosine"}
)


# ==========================
# Reset Collection
# ==========================
def reset_collection():
    global collection

    try:
        client.delete_collection(name="doctrust")
    except:
        pass

    collection = client.get_or_create_collection(
        name="doctrust",
        metadata={"hnsw:space": "cosine"}
    )

    print("🧹 Database cleared successfully.")
# ==========================
# Store Embeddings
# ==========================
def store_embeddings(chunks, embeddings, filename):

    global collection

    try:
        ids = [str(uuid.uuid4()) for _ in chunks]

        metadatas = []

        for i in range(len(chunks)):
            metadatas.append(
                {
                    "source": filename,
                    "page": i + 1
                }
            )

        if hasattr(embeddings, "tolist"):
            embeddings = embeddings.tolist()

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(
            f"✅ Stored {len(chunks)} chunks from {filename}"
        )
        print(
            f"📊 Total chunks in DB : {collection.count()}"
        )

    except Exception as e:
        print("❌ Store Error:", e)
        raise e


# ==========================
# Check Uploaded Documents
# ==========================
def has_uploaded_documents():

    try:
        return collection.count() > 0
    except:
        return False


# ==========================
# Search Similar Chunks
# ==========================
def search_similar_chunks(question, top_k=5):

    global collection

    try:
        total_docs = collection.count()

        print(f"\n📊 Total chunks available : {total_docs}")

        if total_docs == 0:
            print("❌ Database empty.")
            return []

        query_embedding = get_embedding(question)

        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()

        top_k = min(top_k, total_docs)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        print("\n========== CHROMA RESULTS ==========")
        print(results)
        print("====================================\n")

        if (
            not results
            or "documents" not in results
            or not results["documents"]
            or not results["documents"][0]
        ):
            return []

        docs = results["documents"][0]
        metas = results["metadatas"][0]

        retrieved = []

        for doc, meta in zip(docs, metas):
            retrieved.append(
                {
                    "text": doc,
                    "source": meta.get("source", "Unknown"),
                    "page": meta.get("page", 1)
                }
            )

        print(
            f"✅ Retrieved {len(retrieved)} chunks."
        )

        return retrieved

    except Exception as e:
        print("❌ Search Error:", e)
        return []