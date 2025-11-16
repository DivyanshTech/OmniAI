import json
import os
from typing import List, Dict

class KnowledgeBase:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.faqs: List[Dict] = []
        self.policies: List[Dict] = []
        self.all_documents: List[Dict] = []

    def load_data(self) -> bool:
        try:
            faqs_path = os.path.join(self.data_dir, "faqs.json")
            if not os.path.exists(faqs_path):
                raise FileNotFoundError(f"{faqs_path} not found")
            with open(faqs_path, 'r', encoding='utf-8') as f:
                self.faqs = json.load(f)

            policies_path = os.path.join(self.data_dir, "policies.json")
            if not os.path.exists(policies_path):
                raise FileNotFoundError(f"{policies_path} not found")
            with open(policies_path, 'r', encoding='utf-8') as f:
                self.policies = json.load(f)

            self.all_documents = self._prepare_documents()
            print(f"Loaded {len(self.faqs)} FAQs and {len(self.policies)} policies")
            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def _prepare_documents(self) -> List[Dict]:
        documents = []

        for faq in self.faqs:
            doc = {
                "id": f"faq_{faq.get('id', 'NA')}",
                "type": "faq",
                "category": faq.get("category", "General"),
                "content": f"Question: {faq.get('question','')}\nAnswer: {faq.get('answer','')}",
                "metadata": faq
            }
            documents.append(doc)

        for policy in self.policies:
            doc = {
                "id": f"policy_{policy.get('id', 'NA')}",
                "type": "policy",
                "category": policy.get("category", "General"),
                "content": f"Title: {policy.get('title','')}\nCategory: {policy.get('category','')}\nContent: {policy.get('content','')}",
                "metadata": policy
            }
            documents.append(doc)

        return documents

    def get_all_documents(self) -> List[Dict]:
        return self.all_documents

kb = KnowledgeBase()
