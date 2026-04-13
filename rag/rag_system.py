import os
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

def build_vector_store(text_chunks: List[str]) -> Optional[FAISS]:
    """
    Construye un Vector Store usando FAISS y Embeddings locales de HuggingFace.
    """
    if not text_chunks:
        logger.warning("La lista de textos está vacía. No se puede construir el Vector Store.")
        return None

    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        documents = [Document(page_content=text) for text in text_chunks]
        
        vector_store = FAISS.from_documents(documents, embeddings)
        logger.info(f"Vector Store construido exitosamente con {len(documents)} documentos.")
        
        return vector_store
    except Exception as e:
        logger.error(f"Error al construir el Vector Store: {e}")
        return None

def get_rag_retriever(vector_store: FAISS) -> Optional[VectorStoreRetriever]:
    """
    Devuelve un retriever a partir de la base de vectores.
    """
    if vector_store:
        return vector_store.as_retriever(search_kwargs={"k": 3})
    
    logger.warning("Se intentó crear un retriever, pero el Vector Store es None.")
    return None
