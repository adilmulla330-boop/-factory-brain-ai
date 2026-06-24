from sentence_transformers import SentenceTransformer
import chromadb
import os
import pandas as pd
from pypdf import PdfReader

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="db")

try:
    client.delete_collection("factory_docs")
except:
    pass

collection = client.create_collection("factory_docs")

docs_folder = "documents"
doc_id = 1

for filename in os.listdir(docs_folder):
    filepath = os.path.join(docs_folder, filename)
    chunks = []
    metadatas = []

    try:
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                chunks.append(f.read())
                metadatas.append({"source": filename, "page": "1"})

        elif filename.endswith(".csv"):
            df = pd.read_csv(filepath)
            for idx, row in df.iterrows():
                chunks.append(f"Row {idx+1}:\n{row.to_string()}")
                metadatas.append({"source": filename, "page": str(idx+1)})

        elif filename.endswith(".xlsx"):
            excel_file = pd.ExcelFile(filepath)
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet)
                chunks.append(f"Sheet: {sheet}\n{df.to_string(index=False)}")
                metadatas.append({"source": filename, "page": f"Sheet {sheet}"})

        elif filename.endswith(".pdf"):
            reader = PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    chunks.append(page_text)
                    metadatas.append({"source": filename, "page": str(i+1)})
        else:
            continue

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            embedding = model.encode(chunk).tolist()
            
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[metadatas[i]],
                ids=[f"doc_{doc_id}"]
            )
            doc_id += 1
            
        print(f"Indexed: {filename}")

    except Exception as e:
        print(f"Failed: {filename} -> {e}")

print("TitanForge knowledge base ready!")