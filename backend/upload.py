import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
import storage


from pdf_reader import read_pdf
from chunker import split_text
from embeddings import create_embeddings
from vector_store import store_embeddings, reset_collection

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/", summary="Upload PDF")
async def upload_pdf(files: List[UploadFile] = File(...)):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one PDF."
        )

    try:
        print(f"\n📥 FILES RECEIVED: {len(files)}")

        # Fresh upload session
        reset_collection()
        storage.UPLOADED_DOCUMENT_CHUNKS.clear()

        runtime_payload = []
        upload_summary = []
        total_chunks = 0

        for file in files:

            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is not a PDF."
                )

            print(f"📄 Processing: {file.filename}")

            unique_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(
                UPLOAD_FOLDER,
                unique_name
            )

            contents = await file.read()

            with open(file_path, "wb") as f:
                f.write(contents)

            print("✅ PDF Saved")

            pdf_text = read_pdf(file_path)

            print("PDF TEXT:")
            print(pdf_text[:500] if pdf_text else "NO TEXT EXTRACTED")

            if not pdf_text or not pdf_text.strip():
                raise HTTPException(
                status_code=422,
                detail=f"{file.filename} is empty."
    )

            print(
                f"📄 Extracted Text Length: "
                f"{len(pdf_text)}"
            )

            chunks = split_text(pdf_text)

            print(
                f"📊 Chunks Created: "
                f"{len(chunks)}"
            )

            embeddings = create_embeddings(chunks)

            print(
                f"📊 Embeddings Created: "
                f"{len(embeddings)}"
            )

            store_embeddings(
                chunks=chunks,
                embeddings=embeddings,
                filename=file.filename
            )

            for i, chunk in enumerate(chunks):
                runtime_payload.append({
                    "text": chunk,
                    "page": i + 1,
                    "source": file.filename
                })

            upload_summary.append({
                "filename": file.filename,
                "chunks": len(chunks)
            })

            total_chunks += len(chunks)

            print(
                f"✅ Stored {len(chunks)} chunks "
                f"from {file.filename}"
            )

        storage.UPLOADED_DOCUMENT_CHUNKS.extend(
            runtime_payload
        )

        print(
            f"✅ Runtime Chunks: "
            f"{len(storage.UPLOADED_DOCUMENT_CHUNKS)}"
        )

        return {
            "message":
                f"Uploaded {len(files)} PDF file(s) successfully.",
            "uploaded_files":
                upload_summary,
            "total_files":
                len(files),
            "total_chunks":
                total_chunks,
            "status":
                "Healthy",
            "language":
                "English"
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("❌ Upload Error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )