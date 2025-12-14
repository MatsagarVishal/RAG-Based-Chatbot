from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq


class RAGBot:
    def __init__(self, kb_id: str, storage):
        """
        Initialize RAG bot with storage backend
        
        Args:
            kb_id: Knowledge base identifier
            storage: Storage backend instance (S3Storage or LocalStorage)
        """
        self.kb_id = kb_id
        self.storage = storage

        # Embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Load FAISS index + metadata from storage
        self.index, self.data = storage.load_kb(kb_id)

        # LLM
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

    def retrieve(self, query: str, k: int = 10):
        query_vec = self.embedder.encode([query])
        distances, indices = self.index.search(query_vec, k)

        texts = []
        sources = set()

        for idx in indices[0]:
            idx = int(idx)  # FAISS → list index

            # Safety guard
            if idx < 0 or idx >= len(self.data["texts"]):
                continue

            texts.append(self.data["texts"][idx])

            metadata = self.data["metadatas"][idx]
            source = metadata.get("source")
            if source:
                sources.add(source)

        return texts, list(sources)

    def ask(self, question: str):
        contexts, sources = self.retrieve(question)

        if not contexts:
            return "I don't know based on the website content.", []

        context_text = "\n\n".join(contexts)

        prompt = f"""
You are a helpful assistant answering questions about a website.

Use ONLY the context below to answer.
The website may describe services using words like:
"offerings", "products", "solutions", or "what we do".

If the answer cannot be inferred from the context, say:
"I don't know based on the website content."

Context:
{context_text}

Question:
{question}
"""

        response = self.llm.invoke(prompt)

        return response.content.strip(), sources

