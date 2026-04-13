import os
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
# Las pesadas se mueven dentro de las funciones

logger = logging.getLogger(__name__)

# Configuración de embeddings (modelo ligero local)
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
INDEX_PATH = "faiss_index"

def get_embeddings():
    """Devuelve el modelo de embeddings configurado."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

def build_vector_store(text_chunks: List[str]) -> Optional[FAISS]:
    """
    Construye un Vector Store usando FAISS y Embeddings locales.
    """
    if not text_chunks:
        logger.warning("La lista de textos está vacía.")
        return None

    try:
        from langchain_community.vectorstores import FAISS
        embeddings = get_embeddings()
        documents = [Document(page_content=text) for text in text_chunks]
        vector_store = FAISS.from_documents(documents, embeddings)
        logger.info(f"Vector Store construido con {len(documents)} documentos.")
        return vector_store
    except Exception as e:
        logger.error(f"Error al construir el Vector Store: {e}")
        return None

def load_from_directory(directory_path: str) -> Optional[FAISS]:
    """
    Carga archivos (.txt, .pdf) de un directorio, los procesa y crea un Vector Store.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Creado directorio: {directory_path}")
        return None

    try:
        from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        
        # Cargamos archivos de texto
        txt_loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
        # Cargamos archivos PDF
        pdf_loader = DirectoryLoader(directory_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
        
        raw_docs = txt_loader.load() + pdf_loader.load()
        
        if not raw_docs:
            logger.warning(f"No se encontraron archivos indexables en {directory_path}")
            return None

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(raw_docs)
        
        embeddings = get_embeddings()
        vector_store = FAISS.from_documents(docs, embeddings)
        logger.info(f"Indexados {len(docs)} fragmentos desde {directory_path}")
        return vector_store
    except Exception as e:
        logger.error(f"Error al cargar desde directorio: {e}")
        return None

def save_vector_store(vector_store: FAISS, folder_path: str = INDEX_PATH):
    """Guarda el Vector Store en disco."""
    try:
        vector_store.save_local(folder_path)
        logger.info(f"Vector Store guardado en {folder_path}")
    except Exception as e:
        logger.error(f"Error al guardar el Vector Store: {e}")

def load_vector_store(folder_path: str = INDEX_PATH) -> Optional[FAISS]:
    """Carga el Vector Store desde el disco."""
    if not os.path.exists(folder_path):
        return None
    try:
        from langchain_community.vectorstores import FAISS
        embeddings = get_embeddings()
        vector_store = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
        logger.info(f"Vector Store cargado desde {folder_path}")
        return vector_store
    except Exception as e:
        logger.error(f"Error al cargar el Vector Store: {e}")
        return None

def get_rag_retriever(vector_store: FAISS) -> Optional[VectorStoreRetriever]:
    """Devuelve un retriever a partir de la base de vectores."""
    if vector_store:
        return vector_store.as_retriever(search_kwargs={"k": 3})
    return None
