import chromadb
import uuid
from collections import deque

EPISODIC_BUFFER_SIZE = 5

class MemoryManager:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("research_memory")
        self.episodic_buffer = deque(maxlen=EPISODIC_BUFFER_SIZE)

    def store(self, sub_question: str, answer: str):
        self.collection.add(
            documents=[answer],
            metadatas=[{"question": sub_question}],
            ids=[str(uuid.uuid4())]
        )
        self.episodic_buffer.append({"question": sub_question, "answer": answer})

    def retrieve(self, query: str, n=2) -> str:
        try:
            results = self.collection.query(query_texts=[query], n_results=min(n, self.collection.count()))
            docs = results["documents"][0] if results["documents"] else []
            return "\n\n".join(docs) if docs else ""
        except Exception:
            return ""

    def get_episodic_context(self) -> str:
        if not self.episodic_buffer:
            return ""
        return "\n\n".join([f"Q: {e['question']}\nA: {e['answer']}" for e in self.episodic_buffer])