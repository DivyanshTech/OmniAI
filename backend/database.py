import json
import os
from typing import List, Dict

class KnowledgeBase:
    def __init__(self, data_dir: str = "./data"):
        """
        data_dir: folder path jahan faqs.json aur policies.json hain
        """
        self.data_dir = data_dir
        self.faqs: List[Dict] = []
        self.policies: List[Dict] = []
        self.all_documents: List[Dict] = []

    def load_data(self) -> bool:
        """Load FAQs and policies from JSON files"""
        try:
            # Load FAQs
            faqs_path = os.path.join(self.data_dir, "faqs.json")
            if not os.path.exists(faqs_path):
                raise FileNotFoundError(f"{faqs_path} not found")
            with open(faqs_path, 'r', encoding='utf-8') as f:
                self.faqs = json.load(f)

            # Load Policies
            policies_path = os.path.join(self.data_dir, "policies.json")
            if not os.path.exists(policies_path):
                raise FileNotFoundError(f"{policies_path} not found")
            with open(policies_path, 'r', encoding='utf-8') as f:
                self.policies = json.load(f)

            # Prepare combined documents
            self.all_documents = self._prepare_documents()
            print(f"✅ Loaded {len(self.faqs)} FAQs and {len(self.policies)} policies")
            return True

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

    def _prepare_documents(self) -> List[Dict]:
        """Prepare documents for embeddings"""
        documents = []

        for faq in self.faqs:
            doc = {
                "id": f"faq_{faq.get('id', 'NA')}",
                "type": "faq",
                "category": faq.get("category", "General"),
                "content": f"Question: {faq.get('question','')}\nAnswer: {faq.get('answer','')}",
                "metadata": {
                    "question": faq.get("question", ""),
                    "answer": faq.get("answer", ""),
                    "category": faq.get("category", "")
                }
            }
            documents.append(doc)

        for policy in self.policies:
            doc = {
                "id": f"policy_{policy.get('id', 'NA')}",
                "type": "policy",
                "category": policy.get("category", "General"),
                "content": f"Title: {policy.get('title','')}\nCategory: {policy.get('category','')}\nContent: {policy.get('content','')}",
                "metadata": {
                    "title": policy.get("title", ""),
                    "category": policy.get("category", ""),
                    "content": policy.get("content", "")
                }
            }
            documents.append(doc)

        return documents

    def get_all_documents(self) -> List[Dict]:
        return self.all_documents

    def get_document_by_id(self, doc_id: str) -> Dict:
        for doc in self.all_documents:
            if doc["id"] == doc_id:
                return doc
        return None

    def search_by_category(self, category: str) -> List[Dict]:
        return [doc for doc in self.all_documents if doc["category"].lower() == category.lower()]

    def get_statistics(self) -> Dict:
        return {
            "total_documents": len(self.all_documents),
            "total_faqs": len(self.faqs),
            "total_policies": len(self.policies),
            "categories": list(set(doc["category"] for doc in self.all_documents))
        }

# ✅ Global KnowledgeBase instance
kb = KnowledgeBase()

if __name__ == "__main__":
    # Test loading
    loaded = kb.load_data()
    if loaded:
        stats = kb.get_statistics()
        print(f"\n📊 Knowledge Base Stats: {stats}")
    else:
        print("❌ Failed to load knowledge base. Ensure faqs.json and policies.json exist in ./data")
