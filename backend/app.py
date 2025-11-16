from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time
import uuid
from datetime import datetime

# FIXED IMPORTS
from backend.rag_engine import rag_engine
from backend.llm_engine import llm_engine          # ← NEW ENGINE (grok-style)
from backend.memory import conversation_memory as memory
from backend.knowledge_base import kb

# ============================================================
# INIT
# ============================================================

app = FastAPI(
    title="Intelligent RAG Chatbot API",
    description="Business + Education mode chatbot with LLM, RAG, Memory",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELS
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    include_context: bool = True
    top_k: int = 3
    mode: str = "default"          # ← business | education

class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    processing_time: float
    context_used: int
    error: Optional[str] = None

# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting API...")

    rag_engine.initialize()
    print("✅ RAG Engine OK")

    test = llm_engine.ask_llm(("ping","ping"))
    print("LLM:", test)

    print("✅ API READY")

# ============================================================
# ROUTES
# ============================================================

@app.get("/")
async def root():
    return {
        "status": "running",
        "version": "2.0.0",
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag": rag_engine.embeddings is not None,
            "llm": True,
            "memory": True,
            "kb": kb is not None
        }
    }

# ============================================================
# MAIN CHAT ENDPOINT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    t0 = time.time()
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # -----------------------
        # 1. MEMORY (last 5 msgs)
        # -----------------------
        history = memory.format_history_for_prompt(session_id, include_last_n=5)

        # -----------------------
        # 2. RAG
        # -----------------------
        context_str = ""
        docs = []

        if request.include_context:
            context_str, docs = rag_engine.get_relevant_context(request.message, top_k=request.top_k)

        # -----------------------
        # 3. LLM
        # -----------------------
        llm_result = llm_engine.generate_response(
            user_query=request.message,
            context=context_str,
            conversation_history=history,
            temperature=0.4,
            mode=request.mode
        )

        bot_response = (
            llm_engine.get_fallback_response(request.message)
            if not llm_result["success"]
            else llm_result["response"]
        )

        # -----------------------
        # 4. MEMORY UPDATE
        # -----------------------
        memory.add_message(session_id, "user", request.message)
        memory.add_message(session_id, "assistant", bot_response)

        # -----------------------
        # 5. LOG TO ANALYTICS
        # -----------------------
        memory.log_message(session_id, "user", request.message, context_used=len(docs))
        memory.log_message(session_id, "assistant", bot_response, context_used=len(docs), processing_time=round(time.time()-t0,3))

        # -----------------------
        # 6. RETURN
        # -----------------------
        return ChatResponse(
            success=True,
            response=bot_response,
            session_id=session_id,
            processing_time=round(time.time() - t0, 3),
            context_used=len(docs)
        )

    except Exception as e:
        return ChatResponse(
            success=False,
            response="Internal error.",
            session_id=session_id,
            processing_time=round(time.time() - t0, 3),
            context_used=0,
            error=str(e)
        )

# ============================================================
# STATS
# ============================================================

@app.get("/stats")
async def stats():
    mem_stats = {
        "active_sessions": len(memory.get_all_sessions()),
        "kb": kb.get_statistics()
    }
    analytics_summary = memory.get_analytics_summary()
    mem_stats.update(analytics_summary)
    return mem_stats

@app.delete("/clear_session/{session_id}")
async def clear_session(session_id: str):
    memory.clear_session(session_id)
    return {"message": "session cleared"}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    h = memory.get_conversation_history(session_id)
    if not h:
        raise HTTPException(status_code=404, detail="Not found")
    return h
