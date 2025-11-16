import os
from typing import Dict, Tuple
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self, provider: str = "groq"):  # ✅ Correct constructor
        self.provider = provider
        self.api_key = None
        self.model = None
        self.api_url = None
        self._setup_provider()
    
    def _setup_provider(self):
        if self.provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY") or "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"
            self.model = "llama-3.3-70b-versatile"
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = "gpt-4o-mini"
            self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            print(f"⚠️ Warning: {self.provider.upper()}_API_KEY not found in environment")
    
    # ---------------- FIXED: tuple return + mode ---------------- #
    def build_prompt(self, user_query: str, context: str, conversation_history: str = None, mode: str = "default") -> Tuple[str, str]:
        if mode == "business":
            system_prompt = (
                "You are a business professional assistant. Provide detailed, structured, precise answers "
                "for business-related queries. Be professional, concise, and actionable."
            )
        elif mode == "education":
            system_prompt = (
                "You are an educational tutor assistant. Explain concepts clearly, give examples, and "
                "help the user understand step by step."
            )
        else:
            system_prompt = (
                "You are GROK — an intelligent, witty, professional assistant with deep knowledge in "
                "AI, education, coding, reasoning, psychology, technology, and research. "
                "Always give detailed, structured, clear, and smart answers. "
                "Never behave like a simple customer-support bot."
            )

        user_prompt = ""
        if conversation_history:
            user_prompt += f"Conversation History:\n{conversation_history}\n"
        if context:
            user_prompt += f"Context:\n{context}\n"
        user_prompt += f"User Question:\n{user_query}\n"

        return system_prompt, user_prompt

    # ---------------- FIXED: messages array ---------------- #
    def ask_llm(self, prompt_tuple: Tuple[str, str], temperature: float = 0.7, max_tokens: int = 500) -> Dict:
        system_prompt, user_prompt = prompt_tuple

        if not self.api_key:
            return {"success": False, "response": "", "error": f"{self.provider.upper()}_API_KEY not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data["choices"][0]["message"]["content"].strip()
                return {"success": True, "response": bot_response, "error": None, "model": self.model, "provider": self.provider}
            else:
                return {"success": False, "response": "", "error": f"API Error {response.status_code}: {response.text}"}
        except requests.exceptions.Timeout:
            return {"success": False, "response": "", "error": "Request timed out. Please try again."}
        except Exception as e:
            return {"success": False, "response": "", "error": f"LLM Error: {str(e)}"}
    
    # ---------------- FIXED: generate_response includes mode ---------------- #
    def generate_response(self, user_query: str, context: str, conversation_history: str = None, temperature: float = 0.7, mode: str = "default") -> Dict:
        prompt_tuple = self.build_prompt(user_query, context, conversation_history, mode)
        result = self.ask_llm(prompt_tuple, temperature=temperature)
        return result
    
    def get_fallback_response(self, user_query: str) -> str:
        return f"""I apologize, but I'm having trouble processing your request right now.

However, I can help you with:
* Account management questions
* Billing and payment inquiries
* Technical support issues
* Subscription and plan information
* Privacy and security questions

Your question was: "{user_query}".
Please try rephrasing your question or contact support."""

# ✅ Global instance
llm_engine = LLMEngine(provider="groq")

if __name__ == "__main__":
    test_context = """
    Question: How do I reset my password?
    Answer: Go to login page, click 'Forgot Password', enter your email, and follow the instructions.
    """
    
    result = llm_engine.generate_response(
        user_query="I forgot my password, what should I do?",
        context=test_context,
        mode="default"   # ← now compatible
    )
    
    print("🤖 LLM Response:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Response: {result['response']}")
    else:
        print(f"Error: {result['error']}")
