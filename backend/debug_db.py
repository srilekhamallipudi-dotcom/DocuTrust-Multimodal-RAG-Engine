from vector_store import search_similar_chunks

print("🔍 Checking ChromaDB Storage Text Chunks...")
chunks = search_similar_chunks("What technical skills does John Doe have?", top_k=3)

print(f"\n📊 Total Chunks Retrieved: {len(chunks)}")
for idx, chunk in enumerate(chunks, 1):
    print(f"\n🧩 Chunk #{idx}:")
    print(chunk)