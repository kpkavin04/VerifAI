from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "intern_policies"

TOP_K = 2

# Load embedding model (same as ingestion)
model = SentenceTransformer("all-MiniLM-L6-v2")


def main():
    print("Initializing Chroma PersistentClient...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_collection(name=COLLECTION_NAME)

    while True:
        query = input("Enter a question (or type 'exit'): ").strip()

        if query.lower() == "exit":
            break

        print("\nEmbedding query...")
        query_embedding = model.encode(query).tolist()

        print("Retrieving top chunks...\n")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        ids = results["ids"][0]

        for i in range(len(documents)):
            print(f"--- Result {i + 1} ---")
            print(f"Chunk ID: {ids[i]}")
            print(f"Source: {metadatas[i]['source']}")
            print("\nText:")
            print(documents[i])
            print("\n")

if __name__ == "__main__":
    main()
