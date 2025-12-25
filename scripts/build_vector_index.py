import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("data/chunks/chunks.json")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "intern_policies"

# Load embedding model 
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    print("Initializing Chroma PersistentClient...")
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Intern onboarding and policy documents"}
    )

    print("Embedding and storing chunks...")

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [
        {
            "doc_id": chunk["doc_id"],
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"]
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("\nEmbedding complete")
    print(f"Stored {len(ids)} vectors in collection '{COLLECTION_NAME}'")
    print(f"Persistence directory: {CHROMA_DIR.resolve()}")


if __name__ == "__main__":
    main()