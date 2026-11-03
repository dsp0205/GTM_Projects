import json
import chromadb, numpy as np
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from sklearn.cluster import AgglomerativeClustering

ef = DefaultEmbeddingFunction()

def build(rows, path="chroma_db"):
    texts = [f"{r['summary']} {r['quote']}" for r in rows]
    vecs = np.array(ef(texts))
    col = chromadb.PersistentClient(path=path).get_or_create_collection(
        "objections", embedding_function=ef, metadata={"hnsw:space": "cosine"})
    col.upsert(ids=[f"o{i}" for i in range(len(rows))], documents=texts, embeddings=vecs.tolist(),
               metadatas=[{"call_id": r["call_id"], "handled": r["handled"]} for r in rows])
    return vecs

def themes(rows, vecs, threshold=0.6, min_size=2):
    labels = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                     distance_threshold=threshold).fit_predict(vecs)
    out = []
    for lab in set(labels):
        idx = np.where(labels == lab)[0]
        if len(idx) < min_size:
            continue
        score = vecs[idx] @ vecs[idx].mean(axis=0) / np.linalg.norm(vecs[idx], axis=1)
        members = [rows[i] for i in idx[np.argsort(-score)]]
        out.append({"calls": len({m["call_id"] for m in members}), "examples": members[:8]})
    return sorted(out, key=lambda t: -t["calls"])

def search(query, n=5, path="chroma_db"):
    col = chromadb.PersistentClient(path=path).get_collection("objections", embedding_function=ef)
    return col.query(query_texts=[query], n_results=n)

if __name__ == "__main__":
    with open("objections.json", "r", encoding="utf-8") as f:
        rows = json.load(f)
    vecs = build(rows)
    t = themes(rows, vecs)
    with open("themes.json", "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2)
    print(f"Indexed {len(rows)} objections and clustered into {len(t)} distinct themes.")
