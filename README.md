🏭 Factory Brain AI

An AI-powered Industrial Intelligence Assistant designed to help manufacturing organizations improve maintenance, reliability, safety, compliance, and operational decision-making through Retrieval-Augmented Generation (RAG), Vector Search, and Large Language Models.

🚀 Overview

Factory Brain AI combines enterprise knowledge, maintenance records, inspection reports, safety manuals, root cause analysis documents, and operational procedures into a single intelligent assistant.

The platform enables engineers, operators, maintenance teams, and managers to quickly retrieve information, analyze incidents, generate recommendations, and make data-driven decisions.

✨ Features

🔍 Intelligent Document Search

* Semantic search using vector embeddings
* Retrieval-Augmented Generation (RAG)
* Context-aware responses from industrial documents

🛠 Maintenance Intelligence

* Equipment troubleshooting support
* Maintenance recommendations
* Historical failure analysis
* Predictive maintenance insights

📊 Root Cause Analysis (RCA)

* Failure investigation assistance
* Incident pattern detection
* Lessons learned retrieval
* Corrective action suggestions

🛡 Safety & Compliance Support

* Safety procedure retrieval
* Compliance document search
* Risk assessment assistance
* Audit preparation support

📋 Inspection Management

* Equipment inspection logging
* AI-generated corrective actions
* Failure tracking and reporting
* Knowledge base enrichment

🤖 AI Assistant

* Natural language conversations
* Manufacturing-specific guidance
* Engineering knowledge support
* Industrial decision assistance

⸻

🏗 Technology Stack

Frontend

* Streamlit

AI & Machine Learning

* Sentence Transformers
* Groq API
* Retrieval-Augmented Generation (RAG)

Vector Database

* ChromaDB

Data Processing

* Pandas
* NumPy
* PyPDF

Visualization

* Plotly
* Streamlit AGraph

Search

* DuckDuckGo Search (DDGS)

⸻

📂 Project Structure

factory-brain-ai/
│
├── app.py
├── rag_chat.py
├── search.py
├── index_titanforge.py
│
├── documents/
│   ├── Maintenance Manuals
│   ├── Safety Procedures
│   ├── RCA Reports
│   ├── Audit Reports
│   └── Training Documents
│
├── db/
│   └── ChromaDB Vector Store
│
├── requirements.txt
└── README.md

⚙️ Installation

git clone https://github.com/adilmulla330-boop/-factory-brain-ai.git
cd -factory-brain-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

▶️ Run Application

streamlit run app.py

🔑 Environment Variables

Create a .env file or configure secrets:

GROQ_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here

🎯 Use Cases

* Manufacturing Operations
* Reliability Engineering
* Asset Management
* Industrial Maintenance
* Safety Management
* Compliance Audits
* Failure Analysis
* Knowledge Management

📈 Future Enhancements

* Multi-Agent AI Architecture
* Predictive Failure Forecasting
* IoT Sensor Integration
* Industrial Digital Twin Support
* Advanced Analytics Dashboard
* Real-Time Alerting System

👨‍💻 Author

Mulla Adil
Computer Science & Engineering Student
Sri Venkateswara College of Engineering (SVCE), Tirupati

📜 License

This project is intended for educational, research, and innovation purpose 

“Transforming Industrial Knowledge into Intelligent Action.”
