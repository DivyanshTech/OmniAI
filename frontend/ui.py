# ui.py — Hybrid Streamlit UI (backend -> fallback to llm_engine)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import requests
import uuid
import time
from datetime import datetime

# Try importing local LLM engine
try:
    from backend.llm_engine import llm_engine
except Exception as e:
    llm_engine = None
    print(f"⚠️ Warning: llm_engine import failed: {e}")

# Page configuration
st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI (unchanged)
st.markdown("""<style>
    .main { background-color: #f5f7fa; }
    .user-message { background-color: #007bff; color: white; padding: 12px 18px; border-radius: 18px 18px 4px 18px; margin: 8px 0; margin-left: auto; max-width: 70%; float: right; clear: both; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .bot-message { background-color: white; color: #333; padding: 12px 18px; border-radius: 18px 18px 18px 4px; margin: 8px 0; max-width: 70%; float: left; clear: both; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #007bff; }
    .timestamp { font-size: 0.75rem; color: #666; margin-top: 4px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; }
    .metric-card { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 10px 0; }
</style>""", unsafe_allow_html=True)

# Backend API URL (local default)
BACKEND_URL = "http://localhost:8000"

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False

# ---------- Helpers ----------

def check_backend_health() -> bool:
    """Return True if backend health endpoint responds 200."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False

def _call_backend(user_message: str, top_k: int = 3, include_context: bool = True) -> dict:
    """
    Call FastAPI backend /chat endpoint.
    Returns backend JSON or raises Exception on failure.
    """
    payload = {
        "message": user_message,
        "session_id": st.session_state.session_id,
        "include_context": include_context,
        "top_k": top_k
    }
    resp = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=20)
    # Raise for non-200 so caller uses fallback
    resp.raise_for_status()
    return resp.json()

def _call_llm_direct(user_message: str) -> dict:
    """
    Call local LLM engine (llm_engine.generate_response).
    Returns dict with keys similar to backend response: success, response, processing_time, context_used
    """
    start = time.time()
    if llm_engine is None:
        return {"success": False, "error": "Local LLM not available"}
    try:
        # build context empty — RAG not run here; it's a fallback
        result = llm_engine.generate_response(user_query=user_message, context="", conversation_history=None, temperature=0.7)
        elapsed = round(time.time() - start, 2)
        if result.get("success"):
            return {
                "success": True,
                "response": result.get("response", ""),
                "processing_time": elapsed,
                "context_used": 0
            }
        else:
            return {"success": False, "error": result.get("error", "LLM returned failure")}
    except Exception as e:
        return {"success": False, "error": f"LLM exception: {e}"}

def send_message(user_message: str) -> dict:
    """
    Hybrid send_message:
      1) Try backend (preferred) -> returns backend response (uses RAG, memory, logging)
      2) If backend unavailable/fails -> fallback to local LLM (llm_engine)
    Always returns a dict with at least 'success' key.
    """
    # Try backend first
    try:
        if check_backend_health():
            try:
                backend_resp = _call_backend(user_message, top_k=3, include_context=True)
                # backend_resp expected to match ChatResponse model from backend
                # Normalize shape
                if isinstance(backend_resp, dict) and backend_resp.get("success"):
                    return {
                        "success": True,
                        "response": backend_resp.get("response", ""),
                        "processing_time": backend_resp.get("processing_time", 0),
                        "context_used": backend_resp.get("context_used", 0)
                    }
                else:
                    # Backend returned success=False -> fallback
                    return {"success": False, "error": backend_resp.get("error", "Backend returned failure")}
            except requests.exceptions.RequestException as e:
                # Backend call failed despite health check — fallback
                print(f"⚠️ Backend request failed: {e}")
            except Exception as e:
                print(f"⚠️ Backend unexpected error: {e}")
        else:
            print("⚠️ Backend not healthy or unreachable — using local LLM fallback.")
    except Exception as e:
        print(f"⚠️ Health check error: {e}")

    # Fallback to direct LLM call
    llm_result = _call_llm_direct(user_message)
    return llm_result

def clear_conversation():
    """Clear conversation both locally and on backend (best effort)"""
    try:
        requests.delete(f"{BACKEND_URL}/clear_session/{st.session_state.session_id}", timeout=3)
    except Exception:
        pass
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.conversation_started = False

def display_message(role: str, content: str, timestamp: str = None):
    """Render a chat bubble in Streamlit"""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            {content}
            {f'<div class="timestamp">{timestamp}</div>' if timestamp else ''}
        </div><div style="clear: both;"></div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            🤖 {content}
            {f'<div class="timestamp">{timestamp}</div>' if timestamp else ''}
        </div><div style="clear: both;"></div>
        """, unsafe_allow_html=True)

# ---------- UI Layout (same as yours) ----------

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1>🤖 Customer Support Chatbot</h1>
        <p>AI-powered assistant with RAG and conversation memory</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        backend_status = check_backend_health()
        status_color = "🟢" if backend_status else "🔴"
        status_text = "Connected" if backend_status else "Disconnected"
        st.markdown(f"**Backend Status:** {status_color} {status_text}")

        if not backend_status:
            st.error("⚠️ Backend is not running. Start FastAPI server to enable RAG/context logging.")
            st.code("uvicorn app:app --reload --host 0.0.0.0 --port 8000")

        st.divider()
        st.subheader("📊 Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        st.text(f"Messages: {len(st.session_state.messages)}")

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            clear_conversation()
            st.rerun()

        st.divider()
        st.subheader("⚡ Quick Actions")
        quick_questions = [
            "How do I reset my password?",
            "What payment methods do you accept?",
            "How do I cancel my subscription?",
            "Is my data secure?",
            "How do I contact support?"
        ]
        for q in quick_questions:
            if st.button(q, key=q, use_container_width=True):
                st.session_state.quick_question = q
                st.rerun()

        st.divider()
        st.subheader("ℹ️ About")
        st.info("""
        This chatbot uses:
        - FastAPI backend (preferred)
        - RAG for context retrieval (backend)
        - LLM (Groq/OpenAI) as fallback or direct
        - Conversation memory & logging (backend)
        """)

    # Main chat area
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        if not st.session_state.conversation_started and len(st.session_state.messages) == 0:
            st.markdown("""
            ### 👋 Welcome to Customer Support!
            I'm your AI assistant. Ask anything or use quick actions in the sidebar.
            """)

        # Display history
        for message in st.session_state.messages:
            display_message(message["role"], message["content"], message.get("timestamp"))

        st.divider()
        default_value = ""
        if "quick_question" in st.session_state:
            default_value = st.session_state.quick_question
            del st.session_state.quick_question

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_area("Your message:", value=default_value, height=100, placeholder="Type your question here...", key="user_input")
            col_a, col_b, col_c = st.columns([1,1,4])
            with col_a:
                submit_button = st.form_submit_button("Send 📤", use_container_width=True)
            with col_b:
                if st.form_submit_button("Clear 🗑️", use_container_width=True):
                    clear_conversation()
                    st.rerun()

        if submit_button and user_input.strip():
            st.session_state.conversation_started = True
            timestamp = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            display_message("user", user_input, timestamp)

            # Send & handle
            with st.spinner("🤔 Thinking..."):
                start = time.time()
                resp = send_message(user_input)
                elapsed_total = round(time.time() - start, 2)

            if resp.get("success"):
                bot_message = resp.get("response", "")
                processing_time = resp.get("processing_time", elapsed_total)
                context_used = resp.get("context_used", 0)
                bot_ts = datetime.now().strftime("%I:%M %p")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_message,
                    "timestamp": f"{bot_ts} • {processing_time}s • {context_used} sources"
                })
                display_message("assistant", bot_message, f"{bot_ts} • {processing_time}s")
                st.success(f"✅ Response generated in {processing_time}s using {context_used} knowledge sources")
            else:
                err = resp.get("error", "Unknown error")
                st.error(f"❌ {err}")
                fallback = "I'm having trouble right now. Please try again or contact support@ourcompany.com"
                st.session_state.messages.append({"role":"assistant","content":fallback,"timestamp":datetime.now().strftime("%I:%M %p")})
            st.rerun()

if __name__ == "__main__":
    main()
