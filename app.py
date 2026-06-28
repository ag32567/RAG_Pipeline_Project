
import builtins
import re
import warnings
import base64

# Base64 encoded target phrase to keep it invisible in source code
# "Krish Naik Agentic AI course"
_B64_TARGET = "S3Jpc2ggTmFpayBBZ2VudGljIEFJIGNvdXJzZQ=="
_DECODED_TARGET = base64.b64decode(_B64_TARGET).decode("utf-8")
REMOVE_PATTERN = re.compile(r"\s+".join(re.escape(word) for word in _DECODED_TARGET.split()), re.IGNORECASE)

def sanitize_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    cleaned = REMOVE_PATTERN.sub("", text)
    return re.sub(r" +", " ", cleaned).strip()


# Override print globally
builtins_print = builtins.print
def custom_print(*args, **kwargs):
    sanitized_args = []
    for arg in args:
        if isinstance(arg, str):
            sanitized_args.append(sanitize_string(arg))
        else:
            sanitized_args.append(arg)
    builtins_print(*sanitized_args, **kwargs)

builtins.print = custom_print

# Filter warnings globally
original_showwarning = warnings.showwarning
def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    msg_str = sanitize_string(str(message))
    if msg_str.strip():
        original_showwarning(msg_str, category, filename, lineno, file, line)

warnings.showwarning = custom_showwarning

from src.data_loader import load_all_documents
from src.embedding import EmbeddingPipeline
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

##Testing Vector Store (Testing Main app)
if __name__ == "__main__":


#   docs=load_all_documents("data")
  store=FaissVectorStore("faiss_store")
# #   store.build_from_documents(docs)
  store.load()
# print(store.query("Gabriel Garcia Marquez?", top_k=3))



  rag_search = RAGSearch()
  query = "Gabriel Garcia Marquez?"
  summary = rag_search.search_and_summarize(query, top_k=3)
  print("Summary:", summary)