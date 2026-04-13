import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from llm_config import get_groq_llm

logger = logging.getLogger(__name__)

class NewsResearchAgent:
    """Agente encargado de investigar tendencias y proponer ideas de artículos usando Groq y búsqueda en la web."""
    def __init__(self):
        # Temperatura alta (0.8) ideal para brainstorming y creatividad
        self.llm = get_groq_llm(temperature=0.8) 
        self.search = DuckDuckGoSearchRun()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un visionario editor de investigación para un periódico local que busca modernizarse.
            Tu objetivo es proponer ángulos noticiosos frescos basados en tendencias REALES y actuales.
            Utiliza la información de búsqueda proporcionada para fundamentar tus propuestas."""),
            ("human", """Investiga el siguiente tema. Aquí tienes los resultados de una búsqueda reciente en internet sobre el tema:
            
            RESULTADOS DE BÚSQUEDA: 
            {search_results}
            
            TEMA ORIGINAL: {topic}
            
            1. Identifica el IDIOMA del TEMA ORIGINAL (responde solo con una palabra: spanish, english, german, dutch, portuguese, o pinyin).
            2. Enumera 3 tendencias actuales o ideas de artículos innovadores.
            
            Formato de respuesta:
            IDIOMA: [idioma]
            IDEAS: [tus ideas]""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def research_trends(self, topic: str) -> dict:
        if not self.chain: 
            return {"language": "spanish", "ideas": "Error: Cadena de LLM no inicializada."}
        
        try:
            logger.info(f"Buscando en internet sobre: {topic}")
            search_results = self.search.run(topic)
            
            response = self.chain.invoke({
                "topic": topic,
                "search_results": search_results
            })
            
            content = response.content
            # Extraer idioma e ideas
            lang = "spanish"
            ideas = content
            if "IDIOMA:" in content:
                parts = content.split("IDEAS:")
                lang_line = parts[0].replace("IDIOMA:", "").strip().lower()
                lang = "".join(filter(str.isalpha, lang_line)) # Limpiar puntuación
                ideas = parts[1].strip() if len(parts) > 1 else content
            
            return {"language": lang, "ideas": ideas}
        except Exception as e:
            logger.error(f"Error al investigar tendencias en la web: {e}")
            return {"language": "spanish", "ideas": f"Error en la investigación: {str(e)}"}

if __name__ == "__main__":
    agent = NewsResearchAgent()
    print(agent.research_trends("Tendencias tecnológicas 2026"))
    