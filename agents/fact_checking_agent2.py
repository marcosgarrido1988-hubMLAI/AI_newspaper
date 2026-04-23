import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from llm_config import get_groq_llm

logger = logging.getLogger(__name__)

class FactCheckingAgent:
    """Agente que verifica la información y evalúa la fiabilidad de las fuentes usando Groq y búsqueda web."""
    def __init__(self):
        self.llm = get_groq_llm(temperature=0.1) 
        self.search = DuckDuckGoSearchRun()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un editor jefe de Fact-Checking sumamente riguroso. 
            Tu objetivo es garantizar la veracidad y objetividad absoluta.
            Utiliza los resultados de búsqueda proporcionados para contrastar los datos del artículo.
            Si encuentras discrepancias, menciónalas claramente."""),
            ("human", """Revisa el siguiente borrador de artículo. Hemos realizado una búsqueda de verificación sobre los puntos clave del artículo:
            
            RESULTADOS DE VERIFICACIÓN (WEB):
            {search_results}
            
            ARTÍCULO A REVISAR:
            {article}
            
            Proporciona una evaluación crítica basada EN EVIDENCIAS. Identifica errores, sesgos o datos sin contrastar.
            Responde en el mismo idioma que el artículo.""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def verify_information(self, article: str) -> str:
        if not self.chain: 
            return "Error: Cadena LLM no inicializada."
        
        try:
            # Asegurarse de que el artículo sea una cadena antes de procesarlo
            article_text = str(article)
            # Extraemos una consulta de verificación basada en el inicio del artículo
            search_query = f"fact check: {article_text[:120]}"
            
            logger.info(f"Realizando búsqueda de fact-checking: {search_query}")
            search_results = self.search.run(search_query)
            
            response = self.chain.invoke({
                "article": article_text,
                "search_results": search_results
            })
            return response.content
        except Exception as e:
            logger.error(f"Error al verificar la información con búsqueda: {e}")
            # Fallback a verificación interna
            try:
                fallback_prompt = f"Realiza una revisión crítica interna de este artículo basándote en tu conocimiento:\n\n{article}"
                response = self.llm.invoke(fallback_prompt)
                return f"(Nota: Búsqueda de verificación fallida. Evaluación interna activa)\n\n{response.content}"
            except:
                return f"Error en el proceso de Fact-Checking: {str(e)}"

if __name__ == "__main__":
    agent = FactCheckingAgent()
    articulo_test = "El Real Madrid ha ganado 15 Champions Leagues hasta el año 2024."
    print("--- PRUEBA AGENTE FACT-CHECKING ---")
    print(agent.verify_information(articulo_test))
