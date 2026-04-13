import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate
from llm_config import get_groq_llm 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualAgent:
    """Agente encargado de adaptar y traducir noticias a múltiples idiomas."""
    def __init__(self):
        self.llm = get_groq_llm(temperature=0.3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un traductor y adaptador cultural experto. Tu tarea es recibir un artículo en español y adaptarlo a varios idiomas, manteniendo el tono periodístico pero ajustando modismos o contextos si es necesario para que suene natural en el idioma destino."),
            ("human", """Adapta el siguiente artículo a los siguientes idiomas:
            1. Chino (SOLO PINYIN, sin caracteres chinos).
            2. Alemán.
            3. Holandés.
            4. Portugués.
            5. Inglés.
            
            Artículo original (Español):
            {article_text}
            
            REGLAS CRÍTICAS:
            1. Traduce el texto ÍNTEGRAMENTE. No resumas. Si el original tiene 5 párrafos, la traducción debe tener 5 párrafos.
            2. Mantén el mismo tono periodístico.
            
            ESTRUCTURA DE RESPUESTA (JSON PURO):
            {{
                "pinyin": "[ARTÍCULO COMPLETO EN PINYIN]",
                "german": "[ARTÍCULO COMPLETO EN ALEMÁN]",
                "dutch": "[ARTÍCULO COMPLETO EN HOLANDÉS]",
                "portuguese": "[ARTÍCULO COMPLETO EN PORTUGUÉS]",
                "english": "[ARTÍCULO COMPLETO EN INGLÉS]"
            }}
            IMPORTANTE: Solo el objeto JSON, sin comentarios adicionales.""")
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def adapt_to_languages(self, article_text: str) -> str:
        if not self.chain: 
            return "Error: Cadena de LLM no inicializada."
            
        try:
            respuesta = self.chain.invoke({
                "article_text": article_text
            })
            return respuesta.content
            
        except Exception as e:
            logger.error(f"Error en la adaptación multi-idioma: {e}")
            return "Lo siento, ocurrió un error al adaptar el artículo a otros idiomas."

if __name__ == "__main__":
    import sys
    # Reconfigurar la salida estándar para manejar emojis/caracteres especiales en Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    agent = MultilingualAgent()
    test_article = "El Real Madrid gana la Champions League en una final emocionante contra el Manchester City."
    print("--- PRUEBA AGENTE MULTILINGÜE ---")
    print(agent.adapt_to_languages(test_article))
