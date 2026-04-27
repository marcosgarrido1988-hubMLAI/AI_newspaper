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
        self.llm = get_groq_llm(temperature=0.4)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un traductor y adaptador cultural experto. Tu tarea es recibir un artículo y adaptarlo al idioma solicitado.
            
            REGLAS CRÍTICAS Y ABSOLUTAS:
            1. Traduce el texto ÍNTEGRAMENTE de forma natural y fluida. No resumas.
            2. Mantén el mismo tono y estructura.
            3. Tu salida debe ser EXCLUSIVAMENTE y ÚNICAMENTE un objeto JSON válido con las claves "title" y "body".
            4. ESTÁ ESTRICTAMENTE PROHIBIDO generar texto conversacional antes o después del JSON. Solo devuelve el JSON puro.
            5. MUY IMPORTANTE: EVITA LA REPETICIÓN. Asegúrate de que tu traducción tenga sentido y no repitas las mismas palabras o frases de forma infinita. Escribe oraciones coherentes.
            """),
            ("human", """Adapta el siguiente artículo al idioma: {target_lang}.
            
            Artículo original:
            {article_text}
            
            ESTRUCTURA DE RESPUESTA REQUERIDA (JSON):
            {{
                "title": "...",
                "body": "..."
            }}
            """)
        ])
        
        self.chain = prompt | self.llm if self.llm else None
    
    def translate_article_to(self, article_text: str, target_lang: str) -> str:
        """Traduce un artículo a un único idioma específico."""
        if not self.chain: 
            return '{"error": "LLM no inicializado"}'
            
        try:
            respuesta = self.chain.invoke({
                "article_text": article_text,
                "target_lang": target_lang
            })
            content = respuesta.content.strip()
            
            # Buscamos el inicio y fin del objeto JSON de forma robusta
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                logger.info("JSON block extracted successfully.")
                return content[start:end]
                
            return content
            
        except Exception as e:
            logger.error(f"Error en la adaptación multi-idioma: {e}")
            return '{"error": "Ocurrió un error en la traducción"}'

if __name__ == "__main__":
    # Reconfigurar la salida estándar para manejar emojis/caracteres especiales en Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    agent = MultilingualAgent()
    test_article = "El Real Madrid gana la Champions League en una final emocionante."
    print("--- PRUEBA AGENTE MULTILINGÜE ---")
    print(agent.translate_article_to(test_article, "English"))
