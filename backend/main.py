from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from upload import router as upload_router
from rag_engine import get_answer_from_rag
from gemini_service import generate_answer
from summary import generate_document_summary

app = FastAPI(
    title="DocuTrust Multimodal RAG Engine",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)


# Fix Swagger file upload rendering
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    for schema in schemas.values():
        if not isinstance(schema, dict):
            continue

        properties = schema.get("properties", {})

        for prop in properties.values():
            if not isinstance(prop, dict):
                continue

            # Single file upload
            if prop.get("contentMediaType"):
                prop["format"] = "binary"

            # Multiple file upload
            items = prop.get("items")
            if isinstance(items, dict) and items.get("contentMediaType"):
                items["format"] = "binary"

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def home():
    return {
        "project": "DocuTrust",
        "status": "Running"
    }


@app.get("/test-gemini")
def test_gemini():
    answer = generate_answer(
        context="MERN Stack consists of MongoDB, Express.js, React.js and Node.js.",
        question="What is MERN Stack?"
    )
    return {
        "answer": answer
    }


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(payload: AskRequest):
    return get_answer_from_rag(payload.question)


@app.get("/summary")
def get_summary():
    return {
        "summary": generate_document_summary()
    }