from vector_store import collection
from gemini_service import generate_answer


def generate_document_summary():

    results = collection.get()

    documents = results.get("documents", [])

    if not documents:
        return "No document found."

    context = "\n".join(documents[:20])

    summary = generate_answer(
        context,
        "Give a concise summary of this document in 5 bullet points."
    )

    return summary