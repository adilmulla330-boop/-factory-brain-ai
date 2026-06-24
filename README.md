🏭 Factory Brain AI

An AI-powered document intelligence system that enables users to upload PDF documents, perform semantic search, and receive context-aware answers using Retrieval-Augmented Generation (RAG).

---

✨ Features

- 📄 PDF Document Processing
- 🤖 AI-Powered Question Answering
- 🔍 Semantic Search with ChromaDB
- 🧠 Context-Aware Responses
- ⚡ Retrieval-Augmented Generation (RAG)
- 🌐 Streamlit Web Interface
- 📚 Knowledge Base Management
- 🔒 Secure Local Processing

---

🛠️ Technology Stack

- Frontend: Streamlit
- LLM: Groq API
- Vector Database: ChromaDB
- Embeddings: Sentence Transformers
- Programming Language: Python
- Deployment: Render

---

📁 Project Structure

Factory-Brain-AI/
│
├── app.py
├── requirements.txt
├── chroma_db/
├── data/
├── utils/
├── assets/
└── README.md

---

🚀 Installation

1. Clone Repository

git clone https://github.com/your-username/Factory-Brain-AI.git
cd Factory-Brain-AI

2. Install Dependencies

pip install -r requirements.txt

3. Configure API Key

Create a ".env" file:

GROQ_API_KEY=your_api_key_here

4. Run Application

streamlit run app.py

---

🎯 How It Works

1. Upload PDF documents.
2. Documents are processed and embedded.
3. ChromaDB stores vector representations.
4. User queries are matched semantically.
5. Groq LLM generates context-aware responses.

---

🔮 Future Enhancements

- Multi-document chat
- Voice-based interaction
- OCR support
- User authentication
- Cloud knowledge synchronization

---

👨‍💻 Developer

Mulla Adil
B.Tech CSE Student
Sri Venkateswara College of Engineering, Tirupati

---

📜 License

This project is licensed under the MIT License.