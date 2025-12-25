import chromadb
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, chroma_dir="chroma_db", collection_name="intern_policies"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=str(chroma_dir))
        self.collection = self.client.get_collection(name=collection_name)

    def retrieve(self, query: str, top_k: int = 3):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "distances", "metadatas"]
        )

        formatted_results = []
        for doc, dist, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
            similarity = 1 / (1 + dist)
            formatted_results.append((doc, similarity, meta))
        return formatted_results