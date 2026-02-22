import faiss
import numpy as np
import os
import pickle

SHARED_DIR = "/shared-data"
INDEX_PATH = os.path.join(SHARED_DIR, "faiss.index")
METADATA_PATH = os.path.join(SHARED_DIR, "metadata.pkl")


class VectorStore:
    def __init__(self, dim=384):
        self.dim = dim

        if not os.path.exists(SHARED_DIR):
            os.makedirs(SHARED_DIR)

        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def add_embeddings(self, embeddings, chunks):
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)
        self.metadata.extend(chunks)

        faiss.write_index(self.index, INDEX_PATH)
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def total_vectors(self):
        return self.index.ntotal