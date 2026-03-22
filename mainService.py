import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pickle

# ----------------------------
# Load embeddings and chunks
# ----------------------------
embeddings = np.load("ocelot_emb.npy")  # NumPy array
with open("ocelot_chunks.pkl", "rb") as f:
    all_context_chunks = pickle.load(f)

# Convert embeddings to torch tensor if not already
embeddings = torch.tensor(embeddings)

# ----------------------------
# Load embedding model
# ----------------------------
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ----------------------------
# Semantic search function
# ----------------------------
def search_semantic(query, embeddings, top_context_chunks, top_k=3):
    query_emb = embed_model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    results = []
    for idx, score in zip(top_results.indices, top_results.values):
        idx = int(idx)
        results.append(top_context_chunks[idx])
    return results

# ----------------------------
# Interactive loop
# ----------------------------
print("Semantic search ready. Type your query and press Enter (type 'exit' to quit).")
while True:
    query = input("\nYour query: ")
    if query.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

    retrieved_chunks = search_semantic(query, embeddings, all_context_chunks, top_k=3)
    print("\nTop results:")
    for i, chunk in enumerate(retrieved_chunks, 1):
        print(f"\nResult {i}:\n{chunk}\n---")