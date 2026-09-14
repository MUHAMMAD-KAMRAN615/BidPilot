import os
import pypdf
from typing import List

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

class TenderVectorStore:
    def __init__(self, tender_id: str):
        self.tender_id = tender_id
        self.collection_name = f"tender_{tender_id.replace('-', '_').replace('.', '_')}"
        
        # Runs 100% locally on CPU: zero API keys needed, zero 404 errors
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )

    def ingest_document(self, file_path: str) -> int:
        raw_text = ""
        if file_path.endswith(".pdf"):
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    raw_text += text + "\n"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(raw_text)
        metadatas = [{"tender_id": self.tender_id, "chunk_idx": i} for i in range(len(chunks))]
        
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
        return len(chunks)

    def query(self, query_text: str, k: int = 4) -> str:
        docs = self.vector_store.similarity_search(query_text, k=k)
        return "\n\n---\n\n".join([d.page_content for d in docs])