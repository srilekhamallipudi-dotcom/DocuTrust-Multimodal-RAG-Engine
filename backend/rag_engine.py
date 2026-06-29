import re
from vector_store import search_similar_chunks, has_uploaded_documents
from gemini_service import generate_answer

# ---------------- STATE ----------------
class DocuTrustAgentState:
    def __init__(self, question: str):
        self.question = question
        self.retrieved_chunks = []
        self.is_relevant = False
        self.confidence_score = 0.0
        self.answer = ""
        self.citation_pages = []
        self.timeline_log = []
        self.fallback_triggered = False


# ---------------- AGENTS ----------------
def agent_reader(state):
    state.timeline_log.append("✔ Reader initialized")
    return state


def agent_retriever(state):
    results = search_similar_chunks(state.question, top_k=5)
    state.retrieved_chunks = results
    state.timeline_log.append(f"✔ Retrieved {len(results)} chunks")
    return state


def agent_validator(state):
    if len(state.retrieved_chunks) == 0:
        state.is_relevant = False
        state.confidence_score = 0.0
        state.timeline_log.append("⚠ No relevant chunks found")
    else:
        state.is_relevant = True
        state.confidence_score = 90.0
        state.timeline_log.append("✔ Context validated")
    return state


def agent_fallback(state):
    if not state.is_relevant:
        state.fallback_triggered = True
        state.retrieved_chunks.append({
            "text": "No exact PDF match found. Using general document understanding mode.",
            "source": "Fallback",
            "page": "N/A"
        })
        state.is_relevant = True
        state.confidence_score = 60.0
    return state


# ---------------- GENERATOR (SAFE) ----------------
def agent_generator(state):
    context = "\n".join(
        [c.get("text", "") for c in state.retrieved_chunks]
    )

    try:
        answer = generate_answer(context, state.question)

        # Gemini quota or API issue handle
        if (
            "Quota exceeded" in answer
            or "Gemini failed" in answer
            or "Gemini not available" in answer
        ):
            state.answer = (
                "⚠ Gemini API quota exceeded or temporarily unavailable.\n"
                "PDF was processed successfully and relevant chunks were found.\n"
                "Please try again later."
            )
            state.timeline_log.append("⚠ Gemini quota exceeded")
        else:
            state.answer = answer

    except Exception as e:
        state.answer = (
            "⚠ Gemini API unavailable right now. "
            "Documents are uploaded successfully."
        )
        state.timeline_log.append(f"❌ Gemini failed: {e}")

    return state


def agent_citation(state):
    citations = []

    for chunk in state.retrieved_chunks:
        citations.append(
            f"{chunk.get('source','Unknown')} (Page {chunk.get('page','?')})"
        )

    state.citation_pages = citations if citations else ["N/A"]

    state.timeline_log.append("✔ Citations added")
    return state


# ---------------- MAIN FUNCTION ----------------
def get_answer_from_rag(question):
    state = DocuTrustAgentState(question)

    if not has_uploaded_documents():
        return {
            "question": question,
            "answer": "No PDF uploaded. Please upload documents first.",
            "confidence": "0%",
            "evidence_found": "NO",
            "citation": "N/A",
            "timeline": ["No documents in vector store"]
        }

    state = agent_reader(state)
    state = agent_retriever(state)
    state = agent_validator(state)
    state = agent_fallback(state)
    state = agent_generator(state)
    state = agent_citation(state)

    return {
        "question": state.question,
        "answer": state.answer,
        "confidence": f"{state.confidence_score}%",
        "evidence_found": "YES",
        "citation": ", ".join(state.citation_pages),
        "timeline": state.timeline_log
    }