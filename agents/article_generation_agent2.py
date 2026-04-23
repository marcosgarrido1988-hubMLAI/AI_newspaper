import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from llm_config import get_groq_llm 
from rag.vector_store import load_vector_store, get_rag_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleGenerationAgent:
    """Agente encargado de generar artículos utilizando RAG con archivos del periódico usando Groq."""
    def __init__(self, retriever=None):
        self.llm = get_groq_llm(temperature=0.5)
        self.retriever = retriever
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un periodista experto de un periódico local. Tu tarea es escribir artículos claros, objetivos y atractivos."),
            ("human", """Escribe un borrador de artículo periodístico sobre el siguiente tema: "{topic}".
            
            INSTRUCCIONES DE CONTEXTO:
            - Si hay información de contexto (RAG o Investigación previa) relevante a continuación, utilízala para dar profundidad y datos reales al artículo.
            - Si el contexto está vacío, es irrelevante o indica un error, redacta el artículo basándote exclusivamente en tendencias actuales y conocimientos generales sobre el tema.
            
            Información de contexto (Archivos y/o Investigación):
            {context}
            
            IMPORTANTE: Escribe el artículo ÍNTEGRAMENTE en el idioma: {target_lang}.""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def generate_article(self, topic: str, direct_context: str = "", target_lang: str = "spanish") -> str:
        if not self.chain: 
            return "Error: Cadena de LLM no inicializada."
        
        rag_context = direct_context
        context_encontrado = False
        
        if self.retriever:
            try:
                docs = self.retriever.invoke(topic)
                if docs:
                    retrieved_text = "\n\n".join([f"Fuente {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
                    rag_context += f"\n\n[Documentos de Archivo/RAG]:\n{retrieved_text}"
                    context_encontrado = True
            except Exception as e:
                logger.error(f"Error al recuperar documentos: {e}")
        
        if not context_encontrado and not direct_context:
            rag_context = "(No se encontró contexto histórico relevante. Redactar basándose en tendencias generales)."
            
        try:
            respuesta = self.chain.invoke({
                "topic": topic,
                "context": rag_context,
                "target_lang": target_lang
            })
            return respuesta.content
            
        except Exception as e:
            logger.error(f"Error en la generación del LLM: {e}")
            return f"Lo siento, ocurrió un error al redactar el artículo: {str(e)[:100]}"

if __name__ == "__main__":
    # Intentar cargar base de datos local para prueba
    kb = load_vector_store()
    retriever = get_rag_retriever(kb)
    
    agent = ArticleGenerationAgent(retriever=retriever)
    print("--- PRUEBA AGENTE GENERACIÓN ---")
    print(agent.generate_article("Clasificatorias actuales en la liga de futbol de España"))
