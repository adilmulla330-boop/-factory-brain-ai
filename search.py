import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="db")
collection = client.get_collection("factory_docs")

query = input("Ask a question: ")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

for i, doc in enumerate(results["documents"][0], 1):
    print(f"\nResult {i}:")
    print(doc[:1000])