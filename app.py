from sentence_transformers import SentenceTransformer
import streamlit as st
from groq import Groq
import os
st.set_page_config(page_title="OmniCorp Industrial Copilot", layout="wide", page_icon="⚙️")
import chromadb
import time
import pandas as pd
import re
from ddgs import DDGS
from datetime import datetime

# Load Groq API Key from Render/Environment Variables
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_chat(messages, model="llama-3.3-70b-versatile"):
    response = client_groq.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

if "messages" not in st.session_state:
    st.session_state.messages = []

if "avg_response_time" not in st.session_state:
    st.session_state.avg_response_time = 0

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection("factory_docs")
st.title("OmniCorp Industrial Copilot")

try:
    record_count = collection.count()
except Exception:
    record_count = 0

if os.path.exists("omnicorp_logo.png"):
    st.sidebar.image("omnicorp_logo.png", use_container_width=True)
st.sidebar.caption(f"Database Records Synchronized: {record_count}")

from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config
with st.sidebar:
    app_mode = option_menu(
        menu_title=None,
        options=["Chat Assistant", "QMS Dashboard", "Vision Scanner"],
        icons=["chat-left-dots", "bar-chart", "camera"],
        default_index=0,
    )

if app_mode == "QMS Dashboard":
    st.header("Quality & Maintenance Dashboard")
    try:
        df_dt = pd.read_excel("documents/downtime_tracker.xlsx")
        fig1 = px.bar(df_dt, x="Machine", y="Hours", color="Reason", title="Downtime by Machine")
        st.plotly_chart(fig1, use_container_width=True)
        
        df_mh = pd.read_excel("documents/machine_health.xlsx")
        fig2 = px.scatter(df_mh, x="Temperature", y="Vibration", color="Risk", size="Temperature", hover_data=["Machine"], title="Machine Health Risk Map")
        st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        st.subheader("🚨 Active Alerts & Inspections")
        df_insp = pd.read_csv("documents/failure_inspections.csv")
        high_risk = df_insp[df_insp["Risk_Level"].isin(["High", "Critical"])]
        if not high_risk.empty:
            for _, row in high_risk.iterrows():
                if row["Risk_Level"] == "Critical":
                    st.error(f"**CRITICAL:** {row['Equipment_Tag']} ({row['Equipment_Type']}) - {row['Finding']}. Action: {row['Recommended_Action']}")
                else:
                    st.warning(f"**HIGH RISK:** {row['Equipment_Tag']} ({row['Equipment_Type']}) - {row['Finding']}. Action: {row['Recommended_Action']}")
        else:
            st.success("No active high-risk alerts.")
            
        st.divider()
        st.subheader("📝 Submit Inspection Report")
        with st.form("inspection_report_form"):
            col1, col2 = st.columns(2)
            with col1:
                eq_tag = st.text_input("Equipment Tag (e.g., PMP-102A)")
                eq_type = st.text_input("Equipment Type")
            with col2:
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
                inspector = st.text_input("Inspector Name")
            finding = st.text_area("Finding / Issue Description")
            submit_btn = st.form_submit_button("Analyze & Submit Report")
            
            if submit_btn and eq_tag and finding:
                with st.spinner("AI is analyzing the finding..."):
                    try:
                        import uuid
                        insp_id = f"INSP-{str(uuid.uuid4())[:4].upper()}"
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        rec_action = groq_chat([
                            {"role": "user", "content": f"A field inspector found the following issue on {eq_tag} ({eq_type}): '{finding}'. Risk level is {risk_level}. Generate a short, 1-sentence recommended corrective action."}
                        ]).strip()
                        
                        new_row = f'{insp_id},{date_str},{eq_tag},{eq_type},{inspector},"{finding}",{risk_level},"{rec_action}"\n'
                        with open("documents/failure_inspections.csv", "a", encoding="utf-8") as f:
                            f.write(new_row)
                            
                        import subprocess
                        subprocess.run(["python3", "index_titanforge.py"], capture_output=True)
                        
                        st.success(f"Report submitted and indexed! AI Recommended Action: {rec_action}")
                        time.sleep(3)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to submit: {e}")
            
    except Exception as e:
        st.warning(f"Could not load dashboard data: {e}")
    st.stop()

if app_mode == "Vision Scanner":
    st.header("P&ID Parsing & Document Digitization")
    st.write("Upload a P&ID diagram, schematic, or scanned form.")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Gemini API key. Alternatively, set GEMINI_API_KEY in a .env file.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
        if st.button("Extract Entities & Analyze"):
            api_key = api_key_input.strip() or os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                st.warning("Local Moondream via Ollama is not supported on Streamlit Cloud. Please provide a Gemini API key to use Vision Analysis.")
            else:
                with st.spinner("Analyzing document with Gemini Vision..."):
                    try:
                        import tempfile
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
                            tf.write(uploaded_file.getbuffer())
                            temp_path = tf.name
                        
                        myfile = genai.upload_file(temp_path)
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        response = model.generate_content([myfile, "Analyze this industrial document. Extract any equipment tags, parameters, and provide a brief summary of the schematic or form."])
                        st.markdown("### Analysis Results")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
    st.stop()

st.sidebar.header("Chat History")

for i, msg in enumerate(st.session_state.get("messages", [])):
    if msg["role"] == "user":
        st.sidebar.write(f"• {msg['content'][:40]}")

if st.sidebar.button("Start New Chat"):
    st.session_state.messages = []
    st.rerun()

graph_edges = []
is_general_chat = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask Factory Brain AI")

greetings = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "who are you",
    "what can you do",
    "thanks",
    "thank you"
]

if question:
    is_general_chat = question.lower().strip() in greetings


    if is_general_chat:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        start_time = time.time()

        with st.chat_message("assistant"):
            groq_response = groq_chat([
                {
                    "role": "system",
                    "content": """
You are Factory Brain AI.
Be friendly, conversational and professional.
Introduce yourself when greeted.
Explain that you can help with manufacturing, RCA, compliance, maintenance troubleshooting, lessons learned and industrial insights.
"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ])

            st.markdown(groq_response)

        response_time = round(time.time() - start_time, 2)
        st.session_state.avg_response_time = response_time

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": groq_response
            }
        )

        st.caption(f"Response Time: {response_time}s")

    else:

        employee_lookup = False
        employee_context = ""

        try:
            with open("documents/employees.csv", "r", encoding="utf-8") as f:
                lines = f.readlines()

            matches = []
            for line in lines[1:]: # Skip header
                parts = line.split(',')
                if len(parts) >= 2:
                    name = parts[1].strip()
                    # Check if any part of the name (>=3 chars) is in the question
                    name_parts = name.lower().split()
                    for np in name_parts:
                        if len(np) >= 3 and np in question.lower():
                            matches.append(line.strip())
                            break

            if matches:
                employee_lookup = True
                employee_context = "Employee Records found:\nemployee_id,name,department\n" + "\n".join(matches)

        except Exception:
            pass

        query_embedding = embedding_model.encode(question).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=15,
            include=["documents", "metadatas", "distances"]
        )

        context_chunks = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        for i, doc in enumerate(docs):
            source = metas[i].get("source", "Unknown") if metas and len(metas) > i else "Unknown"
            page = metas[i].get("page", "N/A") if metas and len(metas) > i else "N/A"
            context_chunks.append(f"[Source: {source}, Page: {page}]\n{doc}")
        context = "\n\n".join(context_chunks)

        if employee_lookup and employee_context:
            context = employee_context + "\n\n" + context

        if not context.strip() or len(context.strip()) < 50:
            context = "NO_RELEVANT_CONTEXT_FOUND"

        # Fast AI-driven Knowledge Graph & Classifier using Groq's instant model
        mode = "Knowledge"
        try:
            prompt = f"""
Analyze the query and context.
1. Classify query into: RCA, Compliance, Lessons, Knowledge, or External. 
CRITICAL: If it asks about real-world facts (Elon Musk, Google CEO, dates, etc.), classify as External.
2. Extract up to 4 relationship pairs from the context. Format as a JSON array of 3-item arrays: [["Source Entity", "Target Entity", "Relationship Description"]].

Query: {question}
Context snippet: {context[:1000]}

Respond EXACTLY in this format:
MODE: [Classification]
GRAPH: [JSON Array]
"""
            # Use the 8b-instant model to make this pass lightning fast
            ai_analysis = groq_chat([{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
            
            for line in ai_analysis.split('\n'):
                if line.startswith("MODE:"):
                    m = line.replace("MODE:", "").strip()
                    if m in ["RCA", "Compliance", "Lessons", "Knowledge", "External"]:
                        mode = m
                elif "GRAPH:" in line or line.strip().startswith("[["):
                    import json
                    try:
                        json_str = line.replace("GRAPH:", "").strip()
                        edges = json.loads(json_str)
                        for edge in edges:
                            if len(edge) >= 3:
                                graph_edges.append([str(edge[0]).title(), str(edge[1]).title(), str(edge[2]).title()])
                            elif len(edge) == 2:
                                graph_edges.append([str(edge[0]).title(), str(edge[1]).title(), "Related To"])
                    except:
                        pass
        except:
            pass

        if mode == "Knowledge":
            role_prompt = """
You are Factory Brain AI for TitanForge Industries.

Use only the retrieved context.

If partial information exists, provide the available information and clearly identify what is missing.

Only respond with 'Information not found in TitanForge knowledge base.' when no relevant evidence exists.

Provide a structured answer using the available evidence.
"""
        elif mode == "RCA":
            role_prompt = """
You are a senior reliability engineer for TitanForge Industries.

Use only the retrieved context.

If partial information exists, provide the available information and clearly identify what is missing.

Only respond with 'Information not found in TitanForge knowledge base.' when no relevant evidence exists.

Provide:
1. Evidence Found
2. Likely Root Cause
3. Corrective Actions
4. Preventive Actions
5. Risk Assessment

CRITICAL INSTRUCTION: If the context indicates Critical or High failure risks (e.g. from inspection records), you MUST start your response with a bold **[SAFETY ALERT]** summarizing the immediate danger.
"""
        elif mode == "Compliance":
            role_prompt = """
You are an industrial compliance auditor for TitanForge Industries.

Use only the retrieved context.

If partial information exists, provide the available information and clearly identify what is missing.

Only respond with 'Information not found in TitanForge knowledge base.' when no relevant evidence exists.

Provide:
1. Compliance Findings
2. Safety Risks
3. Missing Procedures
4. Recommendations
"""
        elif mode == "External":
            role_prompt = """
You are a helpful AI assistant for TitanForge Industries.

The user asked a general question about the real world or something outside the company knowledge base.
Use the provided Web Search Results and Current Date to answer the question accurately.
Provide a clear, direct answer.
"""
            try:
                web_results = DDGS().text(question, max_results=3)
                web_context = ""
                for res in web_results:
                    web_context += f"Title: {res.get('title')}\nBody: {res.get('body')}\nURL: {res.get('href')}\n\n"
                
                context = f"Current Date: {datetime.now().strftime('%Y-%m-%d')}\n\nWeb Search Results:\n{web_context}\n\nLocal Documents Context:\n{context}"
            except Exception as e:
                context = f"Current Date: {datetime.now().strftime('%Y-%m-%d')}\n\nFailed to fetch web results.\n\nLocal Documents Context:\n{context}"
        else:
            role_prompt = """
You are an industrial knowledge analyst for TitanForge Industries.

Use only the retrieved context.

If partial information exists, provide the available information and clearly identify what is missing.

Only respond with 'Information not found in TitanForge knowledge base.' when no relevant evidence exists.

Provide:
1. Recurring Patterns
2. Lessons Learned
3. Recommended Actions
"""


        prompt = f"""
{role_prompt}

Document Context:
{context}

User Query:
{question}

Provide a structured answer using headings and bullet points. Whenever you state a fact from the Document Context, you MUST cite its source and page inline (e.g. [Source: Manual.pdf, Page: 4]).
AT THE VERY END of your response, you MUST generate exactly 3 highly specific, contextual follow-up questions the user should ask next. Format them EXACTLY like this:
SUGGESTED_Q: [Question 1]
SUGGESTED_Q: [Question 2]
SUGGESTED_Q: [Question 3]
"""

        start_time = time.time()

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        conversation = []

        for msg in st.session_state.messages[-10:]:
            conversation.append(
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
            )

        conversation.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("assistant"):
            with st.spinner("🧠 Factory Brain AI is analyzing documents, detecting intent, and generating insights..."):
                raw_content = groq_chat(conversation)
            
            suggested_qs = []
            clean_content_lines = []
            for line in raw_content.split('\n'):
                if line.strip().startswith("SUGGESTED_Q:"):
                    q = line.replace("SUGGESTED_Q:", "").replace("*", "").strip()
                    if q: suggested_qs.append(q)
                else:
                    clean_content_lines.append(line)
            
            clean_content = "\n".join(clean_content_lines).strip()
            
            st.session_state.suggested_qs = suggested_qs
            st.markdown(clean_content)
            response_time = round(time.time() - start_time, 2)
            st.caption(f"Response Time: {response_time}s")

        response_time = round(time.time() - start_time, 2)
        st.session_state.avg_response_time = response_time

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": clean_content
            }
        )

        machine_match = re.search(r'([A-Z]{3}-\d{2,3}[A-Z]?)', question.upper())
        if machine_match:
            tag = machine_match.group(1)
            try:
                df_mh = pd.read_excel("documents/machine_health.xlsx")
                if tag in df_mh["Machine"].values:
                    machine_data = df_mh[df_mh["Machine"] == tag].iloc[0]
                    fig_diag = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = machine_data['Risk'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Real-Time Risk Level: {tag}"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "red" if machine_data['Risk'] > 70 else "yellow" if machine_data['Risk'] > 40 else "green"}
                        }
                    ))
                    st.plotly_chart(fig_diag, use_container_width=True)
            except Exception as e:
                pass

        with st.expander("📚 Sources & Evidence Used"):
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i, doc in enumerate(docs, 1):
                st.markdown(f"### Source {i}")

                if metas and len(metas) >= i and metas[i-1]:
                    source_name = metas[i-1].get("source", "Unknown Document")
                    page = metas[i-1].get("page", "N/A")
                    st.caption(f"📄 {source_name} | Page: {page}")

                if distances and len(distances) >= i:
                    score = max(0, min(100, int((1 - distances[i-1]) * 100)))
                    st.caption(f"🎯 Relevance Score: {score}%")

                st.write(doc[:500])

        st.subheader("💡 Suggested Follow-up Questions")

        if not suggested_qs:
            suggested_qs = ["Can you explain that more simply?", "What are the best practices here?", "What are the biggest risks?"]

        cols = st.columns(min(3, len(suggested_qs)))

        for idx, suggestion in enumerate(suggested_qs[:3]):
            with cols[idx]:
                st.button(suggestion, key=f"suggestion_{idx}_{time.time()}")

if graph_edges and not is_general_chat:
    st.divider()
    st.subheader("🕸️ Knowledge Graph")

    nodes = []
    edges = []
    node_ids = set()
    
    for edge_data in graph_edges:
        if len(edge_data) == 3:
            eq, issue, rel = edge_data
        else:
            eq, issue = edge_data[0], edge_data[1]
            rel = "Related To"
            
        if eq not in node_ids:
            nodes.append(Node(id=eq, label=eq, size=25, shape="circularImage", image="https://cdn-icons-png.flaticon.com/512/2000/2000300.png"))
            node_ids.add(eq)
        if issue not in node_ids:
            nodes.append(Node(id=issue, label=issue, size=20, color="#FF5733"))
            node_ids.add(issue)
        edges.append(Edge(source=eq, target=issue, label=rel))
        
    config = Config(width=700, height=400, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6", collapsible=True, physics=False, staticGraph=True)
    agraph(nodes=nodes, edges=edges, config=config)