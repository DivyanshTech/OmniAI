from typing import List, Dict
from collections import deque
from datetime import datetime
import time

class ConversationMemory:
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory with sliding window
        max_messages: Maximum number of messages to keep in memory
        """
        self.max_messages = max_messages
        self.conversations = {}  # session_id -> deque of messages

        # Analytics store: simple in-memory log
        self.analytics_log = []  # List[Dict]

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """
        Add a message to conversation history
        role: 'user' or 'assistant'
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = deque(maxlen=self.max_messages)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.conversations[session_id].append(message)

        # Log to analytics automatically
        self.log_message(session_id, role, content, metadata=metadata)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Retrieve full conversation history for a session"""
        if session_id not in self.conversations:
            return []
        return list(self.conversations[session_id])

    def get_last_n_messages(self, session_id: str, n: int = 5) -> List[Dict]:
        """Get last N messages from conversation"""
        history = self.get_conversation_history(session_id)
        return history[-n:] if history else []

    def format_history_for_prompt(self, session_id: str, include_last_n: int = 5) -> str:
        """
        Format conversation history as a string for LLM prompt
        """
        messages = self.get_last_n_messages(session_id, include_last_n)

        if not messages:
            return "This is the start of the conversation."

        formatted = ["Previous conversation:"]
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role_label}: {msg['content']}")

        return "\n".join(formatted)

    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]

    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a conversation session"""
        history = self.get_conversation_history(session_id)

        if not history:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "session_start": None,
                "session_duration": None
            }

        user_msgs = [m for m in history if m["role"] == "user"]
        assistant_msgs = [m for m in history if m["role"] == "assistant"]

        first_msg_time = datetime.fromisoformat(history[0]["timestamp"])
        last_msg_time = datetime.fromisoformat(history[-1]["timestamp"])
        duration = (last_msg_time - first_msg_time).total_seconds()

        return {
            "total_messages": len(history),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "session_start": history[0]["timestamp"],
            "session_duration_seconds": duration
        }

    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs"""
        return list(self.conversations.keys())

    def export_conversation(self, session_id: str) -> Dict:
        """Export conversation in structured format"""
        return {
            "session_id": session_id,
            "messages": self.get_conversation_history(session_id),
            "stats": self.get_session_stats(session_id)
        }

    # ------------------ ANALYTICS LOGGING ------------------ #
    def log_message(self, session_id: str, role: str, content: str, context_used: int = 0,
                    processing_time: float = None, metadata: Dict = None):
        """Log message for analytics"""
        log_entry = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "context_used": context_used,
            "processing_time": processing_time,
            "metadata": metadata or {}
        }
        self.analytics_log.append(log_entry)

    def get_analytics_summary(self) -> Dict:
        """Return summary analytics"""
        total_msgs = len(self.analytics_log)
        user_msgs = len([m for m in self.analytics_log if m["role"] == "user"])
        assistant_msgs = len([m for m in self.analytics_log if m["role"] == "assistant"])
        return {
            "analytics_total_messages": total_msgs,
            "analytics_user_messages": user_msgs,
            "analytics_assistant_messages": assistant_msgs
        }

# Global memory instance
conversation_memory = ConversationMemory(max_messages=10)

# ------------------ TEST ------------------ #
if __name__ == "__main__":
    # Test memory
    mem = ConversationMemory(max_messages=5)

    # Simulate conversation
    session = "test_session_123"
    mem.add_message(session, "user", "Hello!")
    mem.add_message(session, "assistant", "Hi! How can I help you?")
    mem.add_message(session, "user", "I need help with my account")
    mem.add_message(session, "assistant", "Sure! What specific issue are you facing?")

    print("📜 Conversation History:")
    print(mem.format_history_for_prompt(session))

    print("\n📊 Session Stats:")
    print(mem.get_session_stats(session))

    print("\n📈 Analytics Summary:")
    print(mem.get_analytics_summary())
