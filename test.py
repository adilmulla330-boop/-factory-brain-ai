from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import os

# Read PDFs
all_text = ""

for file in os.listdir("documents"):
    if file.endswith(".pdf"):
        reader = PdfReader(os.path.join("documents", file))
        for page in reader.pages:
            all_text += page.extract_text() or ""

# Create chunks
chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 1000)]

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection("factory_docs")

# Store chunks
for i, chunk in enumerate(chunks):
    embedding = model.encode(chunk).tolist()

    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[chunk]
    )

print("Stored", len(chunks), "chunks in ChromaDB")