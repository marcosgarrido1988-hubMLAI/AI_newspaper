import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from llm_config import get_groq_llm

logger = logging.getLogger(__name__)

class SocialMediaAgent:
    """Agente que crea publicaciones para redes sociales usando Groq."""
    def __init__(self):
        self.llm = get_groq_llm(temperature=0.7)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres el audaz y creativo Community Manager de nuestro periódico local. 
            Tu meta es aumentar la audiencia digital atrayendo tráfico desde las redes sociales.
            Tu tono es atractivo, cercano y usas llamadas a la acción (CTAs) efectivas.
            
            IMPORTANTE: Tu salida debe ser EXCLUSIVAMENTE un objeto JSON válido con las siguientes claves:
            - "tweet": Un texto de máximo 280 caracteres con emojis y hashtags.
            - "instagram": Un texto apelando a la comunidad con una sugerencia visual de la imagen.
            """),
            ("human", """Toma el siguiente texto de un artículo y genera las publicaciones para redes sociales en formato JSON.
            
            ARTÍCULO:
            {article}
            
            JSON (sin comentarios ni markdown):""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def create_posts(self, article: str) -> str:
        """Genera posts para redes sociales y devuelve un JSON string."""
        if not self.chain: 
            return '{"error": "LLM no inicializado"}'
        
        try:
            response = self.chain.invoke({"article": article})
            content = response.content.strip()
            
            # Buscamos el inicio y fin del objeto JSON de forma robusta
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return content[start:end]
                
            return content
        except Exception as e:
            logger.error(f"Error al generar posts de redes sociales: {e}")
            return f'{{"error": "{str(e)}"}}'

if __name__ == "__main__":
    agent = SocialMediaAgent()
    print("--- PRUEBA AGENTE REDES SOCIALES ---")
    print(agent.create_posts("Festival local de música atrae a miles de jóvenes en Madrid."))
