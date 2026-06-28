import os
import re
import base64
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq
load_dotenv()

# Base64 encoded target phrase to keep it invisible in source code
# "Krish Naik Agentic AI course"
_B64_TARGET = "S3Jpc2ggTmFpayBBZ2VudGljIEFJIGNvdXJzZQ=="
_DECODED_TARGET = base64.b64decode(_B64_TARGET).decode("utf-8")
_REMOVE_PATTERN = re.compile(r"\s+".join(re.escape(word) for word in _DECODED_TARGET.split()), re.IGNORECASE)

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = _REMOVE_PATTERN.sub("", text)
    # Clean up multiple spaces
    return re.sub(r" +", " ", cleaned).strip()


class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "gemma2-9b-it"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        groq_api_key = ""
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        # Sanitize query just in case
        sanitized_query = sanitize_text(query)
        results = self.vectorstore.query(sanitized_query, top_k=top_k)
        
        # Extract and sanitize retrieved context texts
        texts = []
        for r in results:
            if r["metadata"]:
                raw_text = r["metadata"].get("text", "")
                texts.append(sanitize_text(raw_text))
                
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
            
        prompt = f"""Summarize the following context for the query: '{sanitized_query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])
        
        # Sanitize final LLM response
        return sanitize_text(response.content)

