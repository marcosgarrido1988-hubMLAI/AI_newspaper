import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from llm_config import get_groq_llm 

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
            - Si hay información de contexto (RAG) relevante a continuación, utilízala para dar profundidad histórica y datos locales al artículo.
            - Si el contexto está vacío, es irrelevante o indica un error, redacta el artículo basándote exclusivamente en tendencias actuales y conocimientos generales sobre el tema.
            
            Información de contexto (Archivos y RAG):
            {context}
            
            Escribir artículo:""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def generate_article(self, topic: str, direct_context: str = "") -> str:
        if not self.chain: 
            return "Error: Cadena de LLM no inicializada."
        
        rag_context = direct_context
        context_encontrado = False
        
        if self.retriever:
            try:
                docs = self.retriever.invoke(topic)
                if docs:
                    retrieved_text = "\n\n".join([f"Fuente {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
                    rag_context += f"\n\n[Documentos de Archivo]:\n{retrieved_text}"
                    context_encontrado = True
            except Exception as e:
                logger.error(f"Error al recuperar documentos: {e}")
                # No bloqueamos el flujo, simplemente dejamos el contexto vacío o con el aviso
        
        if not context_encontrado and not direct_context:
            rag_context = "(No se encontró contexto histórico relevante. Redactar basándose en tendencias generales)."
            
        try:
            respuesta = self.chain.invoke({
                "topic": topic,
                "context": rag_context
            })
            return respuesta.content
            
        except Exception as e:
            logger.error(f"Error en la generación del LLM: {e}")
            return f"Lo siento, ocurrió un error al redactar el artículo. Detalle para el terminal: {str(e)[:100]}"

if __name__ == "__main__":
    from rag.vector_store import load_vector_store, get_rag_retriever
    
    # Intentar cargar base de datos local
    kb = load_vector_store()
    retriever = get_rag_retriever(kb)
    
    agent = ArticleGenerationAgent(retriever=retriever)
    print(agent.generate_article("Clasificatorias actuales en la liga de futbol de España en 2026"))
