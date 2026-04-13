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
            Tu meta es aumentar la audiencia digital (suscriptores) atrayendo tráfico desde las redes sociales.
            Tu tono es atractivo, cercano y usas llamadas a la acción (CTAs) efectivas.
            
            IMPORTANTE: Tu salida debe ser exclusivamente un objeto JSON válido con las siguientes claves:
            - "tweet": Un texto de máximo 280 caracteres con emojis y un hashtag.
            - "instagram": Un texto apelando a la comunidad con una sugerencia visual de la imagen de fondo."""),
            ("human", """Toma el siguiente texto de un artículo y genera las publicaciones para redes sociales en formato JSON.
            
            ARTÍCULO:
            {article}
            
            JSON:""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def create_posts(self, article: str) -> str:
        """Genera posts para redes sociales y devuelve un JSON string."""
        if not self.chain: 
            return '{"error": "LLM no inicializado"}'
        
        try:
            # Forzamos a Groq a usar JSON mode si el modelo lo permite, 
            # aunque con el prompt suele ser suficiente para modelos potentes.
            response = self.chain.invoke({"article": article})
            return response.content
        except Exception as e:
            logger.error(f"Error al generar posts de redes sociales: {e}")
            return f'{{"error": "{str(e)}"}}'

if __name__ == "__main__":
    agent = SocialMediaAgent()
    print(agent.create_posts("Festival local de música atrae a miles de jóvenes en Madrid."))
