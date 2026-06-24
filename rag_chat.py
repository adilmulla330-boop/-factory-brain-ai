import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
client = chromadb.PersistentClient(path="db")
collection = client.get_collection("factory_docs")

while True:
    question = input("\nAsk a question (or type exit): ")

    if question.lower() == "exit":
        break

    query_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
You are Factory Brain AI.

Use ONLY the information provided below to answer.

Context:
{context}

Question:
{question}

Answer:
"""

    response = model.generate_content(prompt)

    print("\nAnswer:")
    print(response.text)