from fastapi import FastAPI
from pydantic import BaseModel
from db import initialize_db, log_experiment, fetch_all, compare_configs

app = FastAPI(title="Evaluation Service")

class ExperimentLog(BaseModel):
    query: str
    chunk_size: int
    top_k: int
    retrieval_latency: float
    generation_latency: float
    total_latency: float
    context_length: int


@app.on_event("startup")
def startup():
    initialize_db()


@app.post("/log")
def log(data: ExperimentLog):
    log_experiment(data.dict())
    return {"status": "logged"}


@app.get("/metrics")
def metrics():
    return {"data": fetch_all()}


@app.get("/compare")
def compare(chunk_size: int = None, top_k: int = None):
    return {
        "comparison": compare_configs(chunk_size, top_k)
    }