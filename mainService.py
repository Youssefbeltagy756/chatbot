# semantic_service.py
import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pickle
from fastapi import FastAPI
from pydantic import BaseModel

# ----------------------------
# Load embeddings and chunks
# ----------------------------
embeddings = np.load("ocelot_emb.npy")  # NumPy array
with open("ocelot_chunks.pkl", "rb") as f:
    all_context_chunks = pickle.load(f)

# Convert embeddings to torch tensor
embeddings = torch.tensor(embeddings)

# ----------------------------
# Load embedding model
# ----------------------------
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(title="Semantic Search API")

# Request model
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3  # optional, default 3

# Semantic search function
def search_semantic(query, embeddings, top_context_chunks, top_k=3):
    query_emb = embed_model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)
    results = [top_context_chunks[int(idx)] for idx in top_results.indices]
    return results

# API endpoint
@app.post("/search")
def search_api(request: QueryRequest):
    results = search_semantic(request.query, embeddings, all_context_chunks, request.top_k)
    return {"results": results}