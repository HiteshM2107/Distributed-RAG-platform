from fastapi import FastAPI, UploadFile, File, Form
from sentence_transformers import SentenceTransformer
import pdfplumber
from vector_store import VectorStore
import time

app = FastAPI(title="Ingestion Service")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
vector_store = VectorStore()


def chunk_text(text: str, chunk_size: int, overlap: int = 50):
    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    chunk_size: int = Form(300)
):
    start_time = time.time()

    # Extract text from PDF
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text.strip():
        return {"error": "No extractable text found in PDF"}

    # Chunk text
    chunks = chunk_text(text, chunk_size)

    # Generate embeddings
    embeddings = embedding_model.encode(chunks, show_progress_bar=False)

    # Store in FAISS
    vector_store.add_embeddings(embeddings, chunks)

    latency = time.time() - start_time

    return {
        "status": "Document processed successfully",
        "chunks_created": len(chunks),
        "total_vectors": vector_store.total_vectors(),
        "processing_latency_seconds": round(latency, 3)
    }