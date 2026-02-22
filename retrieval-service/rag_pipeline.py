import os
import faiss
import numpy as np
import pickle
import time
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

SHARED_DIR = "/shared-data"
INDEX_PATH = os.path.join(SHARED_DIR, "faiss.index")
METADATA_PATH = os.path.join(SHARED_DIR, "metadata.pkl")


class RAGPipeline:
    def __init__(self):
        # Load embedding model
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Load LLM
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        self.llm = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

        # Load FAISS index + metadata safely
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = None
            self.metadata = []

    def retrieve(self, query: str, top_k: int):
        if self.index is None:
            return [], 0.0
        
        start = time.time()

        query_embedding = self.embed_model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype("float32"),
            top_k
        )

        retrieved_chunks = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]

        retrieval_latency = time.time() - start
        return retrieved_chunks, retrieval_latency

    def generate(self, query: str, context: str):
        start = time.time()

        prompt = f"""
Answer the question based only on the provided context.

Context:
{context}

Question:
{query}
"""

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)

        with torch.no_grad():
            outputs = self.llm.generate(**inputs, max_length=256)

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        generation_latency = time.time() - start
        return answer, generation_latency