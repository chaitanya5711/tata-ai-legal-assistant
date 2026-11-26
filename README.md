⚖️ Tata AI Legal Document Intelligence System

An AI legal assistant that reads vendor contracts and answers questions about them in seconds, always citing the source clause. Built with RAG (Retrieval-Augmented Generation): it first finds the relevant clauses, then the LLM answers only from them.

Applied GenAI Engineering: Capstone Project

🔗 Links
What	Link
🎥 Project video:https://docs.google.com/videos/d/1L3F6A0uUKrFTo6vMX0tcQinEttROJ7QDCo-YDvyIKxw/play
🌐 Live app | https://tata-ai-legal-assistant-1.onrender.com |
⚙️ API docs | https://tata-ai-legal-assistant.onrender.com/docs |
📊 Presentation:https://drive.google.com/file/d/1TtmnygmfBlZ0NUQGGsdOVzKHIUOMzn2j/view?usp=sharing

Hosted on Render's free plan: the first load can take about a minute while the server wakes up.

✨ Features
Tab	Feature	What it does
💬 Chat & Audits	Chat with memory	Ask questions in plain English; follow-up questions work
	Summarize / Risks / Deadlines	One-click audits of any document
	Highlighted sources	Shows the source chunks and highlights the lines behind each answer
	Word report	Downloads a full contract review as a .docx file
🛡️ Policy Check & Compare	Contract vs Tata policy	Marks each topic ✅ Compliant, ⚠️ Deviation or ❌ Missing
	Compare two contracts	Clause-by-clause table showing which is better for Tata
📊 Risk Dashboard	Risk score	0–100 score, risk level, chart by severity, risks with fixes
🗓️ Deadline Tracker	Real due dates	Turns notice periods into calendar dates; .ics export and email reminders
🧪 Accuracy Test	Evaluation	13 questions with known answers; scores retrieval, answer and citation accuracy
Sidebar	Languages	Answers in English, Hindi or Marathi
Settings	Offline mode	Runs on a local LLM through Ollama

Supported uploads: PDF, DOCX, TXT, MD, CSV.

🏗️ Architecture
Streamlit UI (app.py)  ──HTTP──►  FastAPI backend (backend/main.py)
                                        │
                                        ▼
                          LangGraph pipeline:  retrieve ──► generate
                                        │                      │
                          ChromaDB + MiniLM (ONNX)     Groq LLM (GPT-OSS-120B)
                          vector search                or Ollama (offline)
Indexing: documents are split into 500-character chunks (50 overlap), embedded with all-MiniLM-L6-v2 (384 dimensions) and stored in ChromaDB.
Retrieve: chat uses the top 4 chunks by cosine similarity; audits read the whole document; the policy check sends the contract plus all policy clauses.
Generate: the LLM answers with a strict prompt (use only the context, cite the source, say "not covered" if absent), temperature 0.1.
Every query is logged to SQLite as an audit trail.
🧰 Tech stack
Layer	Tools
Frontend	Streamlit
Backend	FastAPI, Pydantic
AI workflow	LangGraph
Vector DB	ChromaDB
Embeddings	all-MiniLM-L6-v2 (ONNX runtime)
LLM	Groq GPT-OSS-120B / Ollama (offline)
Database	SQLite + SQLAlchemy
Files & reports	pypdf, python-docx
Testing	pytest (49 tests, LLM mocked)
Deployment	Render, Docker, Docker Compose
📁 Project structure
├── app.py                 # Streamlit frontend
├── config.py              # Settings (read from .env)
├── backend/               # FastAPI app, database models, query log
├── graph/                 # LangGraph workflow, state, prompts
├── rag/                   # File parsing, vector store, KB loader, LLM client
├── utils/                 # Chunking, highlighting, JSON parsing, calendar, report, email
├── evaluation/            # Accuracy test questions and scorer
├── Knowledge_base/        # Tata vendor policy clauses (sample data)
├── tests/                 # Pytest suite
└── .env.example           # Template for secrets (no real keys)
🚀 Run locally
bash
git clone <this-repo-url>
cd <repo-folder>
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then add your Groq API key
bash
uvicorn backend.main:app --reload   # terminal 1: backend (http://localhost:8000/docs)
streamlit run app.py                # terminal 2: frontend (http://localhost:8501)

Or run both with Docker: docker compose up --build

🔐 API key & secret protection
All secrets (Groq API key, SMTP password) live only in .env, which is listed in .gitignore and never committed.
.env.example contains placeholders only.
On Render, keys are stored as environment variables in the dashboard.
🧪 Testing
bash
pytest tests/                    # unit tests, no API key needed (LLM and vector DB mocked)
python -m evaluation.evaluate    # real accuracy test against the LLM
⚠️ Limitations & future work
The policy knowledge base is sample data, not real Tata policy.
Scanned PDFs need OCR; very long contracts need section-by-section (map-reduce) analysis.
No login or user roles yet.
Future: OCR, authentication and roles, a verification step for every claim, batch processing, a managed cloud database.
👤 Author

Chaitanya Jadhav GitHub: chaitanya5711 · LinkedIn: chaitanyatj369344259
