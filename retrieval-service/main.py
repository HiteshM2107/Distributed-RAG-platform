from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import RAGPipeline

app = FastAPI(title="Retrieval Service")

pipeline = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


@app.on_event("startup")
def load_pipeline():
    global pipeline
    pipeline = RAGPipeline()


@app.post("/query")
def query_rag(request: QueryRequest):
    retrieved_chunks, retrieval_latency = pipeline.retrieve(
        request.query,
        request.top_k
    )

    context = "\n".join(retrieved_chunks)

    answer, generation_latency = pipeline.generate(
        request.query,
        context
    )

    return {
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
        "retrieval_latency": round(retrieval_latency, 3),
        "generation_latency": round(generation_latency, 3),
        "context_length": len(context),
        "top_k": request.top_k
    }