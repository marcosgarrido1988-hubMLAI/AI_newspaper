import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Cargar variables de entorno (como GROQ_API_KEY)
load_dotenv()

def get_groq_llm(model_name=None, temperature=0.7):
    """
    Inicializa y devuelve el modelo de Groq a través de LangChain.
    Usa el MODEL_NAME del .env por defecto (llama-3.3-70b-versatile).
    """
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    
    try:
        llm = ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        return llm
    except Exception as e:
        print(f"Error al inicializar el modelo Groq ({model_name}): {e}")
        return None
