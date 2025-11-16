import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

# ✅ FIXED imports
from backend.database import KnowledgeBase
from backend.knowledge_base import kb

# ❌ OLD (WRONG)
# from backend.memory import memory

# ✅ NEW (CORRECT)
from backend.memory import conversation_memory as memory

from backend.llm_engine import llm_engine


class RAGEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.documents = []

        # Knowledge base
        self.kb = KnowledgeBase(data_dir="./data")

        # Vector store
        self.vector_store_path = "./models/vector_store"

    def initialize(self) -> bool:
        try:
            print("🔧 Initializing RAG Engine...")

            print(f"📥 Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)

            if not self.kb.load_data():
                print("❌ Failed to load knowledge base.")
                return False

            self.documents = self.kb.get_all_documents()

            if self._load_vector_store():
                print("✅ Vector store loaded")
            else:
                print("🔨 Building vector store...")
                self._build_vector_store()
                self._save_vector_store()

            return True

        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            return False

    def _build_vector_store(self):
        if not self.documents:
            self.embeddings = np.array([])
            print("⚠️ No documents to embed")
            return

        texts = [doc["content"] for doc in self.documents]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"✅ Generated {len(self.embeddings)} embeddings")

    def _save_vector_store(self):
        os.makedirs(self.vector_store_path, exist_ok=True)
        data = {
            "embeddings": self.embeddings,
            "documents": self.documents,
            "model_name": self.model_name
        }
        filepath = os.path.join(self.vector_store_path, "vectors.pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Vector store saved: {filepath}")

    def _load_vector_store(self) -> bool:
        filepath = os.path.join(self.vector_store_path, "vectors.pkl")
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            if data["model_name"] != self.model_name:
                print("⚠️ Model mismatch → rebuilding")
                return False

            self.embeddings = data["embeddings"]
            self.documents = data["documents"]
            return True

        except Exception as e:
            print(f"❌ Vector load error: {str(e)}")
            return False

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        try:
            if self.embeddings is None or len(self.embeddings) == 0:
                print("⚠️ No embeddings — build vector store first.")
                return []

            query_embedding = self.model.encode([query])
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                results.append({
                    "document": self.documents[idx],
                    "score": float(similarities[idx]),
                    "rank": len(results) + 1
                })

            return results

        except Exception as e:
            print(f"❌ Retrieval error: {str(e)}")
            return []

    def format_context(self, retrieved_docs: List[Dict]) -> str:
        if not retrieved_docs:
            return "No relevant information found."

        ctx = ["📚 Relevant Information:\n"]
        for i, item in enumerate(retrieved_docs, 1):
            doc = item["document"]
            score = item["score"]
            ctx.append(f"\n[Source {i}] (Relevance: {score:.2%})")
            ctx.append(f"Type: {doc['type'].upper()}")
            ctx.append(f"Category: {doc['category']}")
            ctx.append(f"Content: {doc['content']}")
            ctx.append("-" * 80)
        return "\n".join(ctx)

    def get_relevant_context(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        retrieved = self.retrieve_context(query, top_k)
        formatted = self.format_context(retrieved)
        return formatted, retrieved


rag_engine = RAGEngine()

if __name__ == "__main__":
    ok = rag_engine.initialize()
    if ok:
        ctx, docs = rag_engine.get_relevant_context("How do I reset password?", top_k=2)
        print(ctx)
    else:
        print("❌ RAG init failed")
