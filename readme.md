
Production-grade AI assistant capable of handling business customer support, general queries, and context-aware conversations. Features include:

- RAG (Retrieval Augmented Generation) for accurate responses from knowledge bases
- Conversation memory to track user context
- Real-time logging and analytics
- Integration with multiple LLMs (OpenAI/Grok/Local models)
🎯 Overview
This is a fully functional, production-ready customer support chatbot that combines modern AI technologies to provide intelligent, context-aware responses. The system uses RAG to retrieve relevant information from a knowledge base and generates natural language responses using state-of-the-art LLMs.
Key Highlights
✅ RESTful API built with FastAPI
✅ Interactive UI using Streamlit
✅ RAG Pipeline with sentence transformers
✅ Conversation Memory (sliding window)
✅ Real-time Logging & analytics
✅ Multi-LLM Support (Groq/OpenAI)
✅ Vector Search with FAISS
✅ Deployment-ready (Render/Railway/AWS)

✨ Features
Core Features

🧠 RAG (Retrieval Augmented Generation)

Semantic search over knowledge base
Top-K document retrieval
Context-aware responses

💬 Conversation Memory
Maintains context across messages
Sliding window (last 10 messages)
Session management

🎯 Multi-Source Knowledge Base
20 comprehensive FAQs
6 detailed policy documents
Categorized information (Account, Billing, Technical, etc.)


📊 Logging & Analytics
Every interaction logged
Daily statistics
Processing time tracking
Error monitoring


Technical Features
⚡ Async API (FastAPI)
🔒 CORS configured for security
🔍 Vector embeddings (384-dimensional)
🎨 Custom UI with chat bubbles
📈 Health monitoring endpoints
🛡️ Error handling & fallback responses

 Architecture
┌─────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                       │
│                      (Streamlit Frontend)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Receive User Query                               │   │
│  │  2. Load Conversation History (Memory)               │   │
│  │  3. Retrieve Context (RAG Engine)                    │   │
│  │  4. Build Prompt (Context + History + Query)         │   │
│  │  5. Generate Response (LLM Engine)                   │   │
│  │  6. Save to Memory                                   │   │
│  │  7. Log Interaction (Logger)                         │   │
│  │  8. Return JSON Response                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐    ┌──────────┐    ┌─────────┐
    │  RAG   │    │   LLM    │    │ Memory  │
    │ Engine │    │  Engine  │    │ Handler │
    └────────┘    └──────────┘    └─────────┘
         │               │               │
         ▼               ▼               ▼
    ┌────────┐    ┌──────────┐    ┌─────────┐
    │ Vector │    │ Groq/GPT │    │ Session │
    │ Store  │    │   API    │    │  Store  │
    └────────┘    └──────────┘    └─────────┘
Data Flow
User Query → Memory Retrieval → RAG Context Search → Prompt Build
→ LLM Generation → Memory Update → Logging → Response to User

🛠️ Tech Stack
Backend

FastAPI - Modern async web framework
Uvicorn - ASGI server
Pydantic - Data validation

AI/ML

Sentence Transformers - Text embeddings
Groq/OpenAI APIs - LLM inference
Scikit-learn - Cosine similarity
NumPy - Vector operations

Frontend

Streamlit - Interactive web UI
Requests - HTTP client

Storage

JSON - Knowledge base storage
Pickle - Vector store serialization
File-based - Conversation logs


📂 Project Structure
chatbot-project/
│
├── backend/
│   ├── app.py              # FastAPI main server
│   ├── llm_engine.py       # LLM integration (Groq/OpenAI)
│   ├── rag_engine.py       # Vector search & retrieval
│   ├── memory.py           # Conversation memory handler
│   ├── database.py         # Knowledge base loader
│   └── logger.py           # Logging & analytics
│
├── frontend/
│   └── ui.py               # Streamlit interface
│
├── data/
│   ├── faqs.json           # 20 FAQ entries
│   └── policies.json       # 6 policy documents
│
├── models/
│   └── vector_store/       # Saved embeddings
│       └── vectors.pkl     # Pickle file
│
├── logs/                   # Auto-generated logs
│   ├── chat_log_YYYY-MM-DD.json
│   ├── errors.json
│   ├── system.log
│   └── app.log
│
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file

🚀 Setup & Installation
Prerequisites

Python 3.8 or higher
pip (Python package manager)
Git
API key from Groq (free) or OpenAI (paid)

Step 1: Clone Repository
bashgit clone https://github.com/yourusername/chatbot-project.git
cd chatbot-project
Step 2: Create Virtual Environment
bash# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
Step 3: Install Dependencies
bashpip install -r requirements.txt
Step 4: Setup Environment Variables
bash# Copy example file
cp .env.example .env

# Edit .env and add your API key
# For Groq (FREE): Get key from https://console.groq.com
# For OpenAI: Get key from https://platform.openai.com/api-keys
Example .env:
bashGROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
# or
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
Step 5: Initialize Vector Store
bashcd backend
python rag_engine.py
This will:

Load FAQs and policies
Generate embeddings
Save vector store to models/vector_store/


💻 Usage
Running Locally
Start Backend Server
bashcd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
Backend will be available at: http://localhost:8000
Start Frontend UI
Open a new terminal:
bashcd frontend
streamlit run ui.py
Frontend will be available at: http://localhost:8501
Testing API Endpoints
bash# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?",
    "session_id": "test123",
    "include_context": true,
    "top_k": 3
  }'

# Get statistics
curl http://localhost:8000/stats

📚API Documentation
Endpoints
GET /
Root endpoint with API information
GET /health
Health check endpoint

Returns service status
Checks RAG, LLM, Memory, Logger

POST /chat
Main chat endpoint
Request Body:
json{
  "message": "Your question here",
  "session_id": "optional-session-id",
  "include_context": true,
  "top_k": 3
}
Response:
json{
  "success": true,
  "response": "Bot response here",
  "session_id": "session-uuid",
  "processing_time": 1.23,
  "context_used": 3,
  "error": null
}
GET /stats
Get system statistics
DELETE /clear_session/{session_id}
Clear conversation history
GET /session/{session_id}
Get session history
Interactive API Docs:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

📸 Screenshots and Demo video
![Chatbot UI](https://raw.githubusercontent.com/DivyanshTech/OmniAI/main/assets/Chatbot%20Intro.png)
![General Question](https://raw.githubusercontent.com/DivyanshTech/OmniAI/main/assets/General%20question.png)
![How do I Contact Support](https://raw.githubusercontent.com/DivyanshTech/OmniAI/main/assets/How%20do%20i%20Contact%20support.png)
![Tech Question](https://raw.githubusercontent.com/DivyanshTech/OmniAI/main/assets/Tech%20Question.png)
[▶ Watch Demo Video](https://raw.githubusercontent.com/DivyanshTech/OmniAI/main/assets/Customer%20Support%2Bgeneral%20purpose%20Chatbot%20-%20Demo.mp4)


