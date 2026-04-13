import os
import sys
from dotenv import load_dotenv

# Reconfigurar la salida estándar para manejar emojis/caracteres especiales en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Cargar variables de entorno PRIMERO
load_dotenv()

# Importar agentes
from agents.news_research_agent2 import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2 import FactCheckingAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.multilingual_agent import MultilingualAgent

# Importar herramientas RAG
from rag.vector_store import build_vector_store, get_rag_retriever

def mock_execution():
    """Ejecuta una simulación en la consola en caso de no tener API key disponible."""
    print("Ejecutando en MODO SIMULACIÓN (Coloca tu GROQ_API_KEY en .env para ejecución real)\n")
    print("--- 1. INVESTIGACIÓN DE NOTICIAS ---")
    print("Agente: Te sugiero escribir sobre 'Impacto de la tecnología en el comercio local' y su evolución.\n")
    print("--- 2. GENERACIÓN DE ARTÍCULO (Usando RAG local) ---")
    print("Agente: Redactando con información de archivos locales...\n'El comercio ha cambiado. Los datos de 2021 muestran un crecimiento en ventas online...'\n")
    print("--- 3. FACT-CHECKING ---")
    print("Agente: Verificación automatizada lista. La coherencia de datos es alta.\n")
    print("--- 4. REDES SOCIALES ---")
    print("Agente: 📈 ¡El comercio local se transforma! ¿Estás listo para el cambio? #Groq #ComercioLocal\n")
    print("--- 5. INTERACCIÓN CON EL LECTOR ---")
    print("Lector: ¿Tenéis tienda física?\nChatbot: ¡Claro! Estamos en la calle Mayor. ¡Ven a visitarnos!\n")


def main():
    print("===================================================================")
    print("   PLATAFORMA AI - MODERNIZACIÓN DEL PERIÓDICO LOCAL (GROQ)  ")
    print("===================================================================\n")
    
    # 2. Comprobación de API key
    if not os.getenv("GROQ_API_KEY") or "gsk_" not in os.getenv("GROQ_API_KEY"):
        mock_execution()
        return

    # Si hay API Key, ejecutamos el pipeline real:
    try:
        # 1. Preparar RAG (Híbrido: Archivos Locales + Búsqueda en Vivo)
        print("[*] Inicializando Sistema de Conocimiento Híbrido...")
        
        # Intentar cargar índice persistente, si no, construir desde carpeta
        from rag.vector_store import load_vector_store, load_from_directory, save_vector_store
        
        DATA_DIR = "archive_data"
        vector_store = load_vector_store()
        
        if not vector_store:
            print(f"[*] No se encontró índice previo. Indexando archivos de '{DATA_DIR}'...")
            vector_store = load_from_directory(DATA_DIR)
            if vector_store:
                save_vector_store(vector_store)
        
        retriever = get_rag_retriever(vector_store)
        
        if retriever:
            print("[+] Base de conocimientos local lista (RAG persistente).")
        else:
            print("[!] Aviso: No hay archivos locales indexados. Se usará solo búsqueda en vivo.")

        print("[+] Buscador en vivo (Internet) activado para el Agente de Investigación.\n")

        # 2. Inicializar Agentes
        print("[*] Levantando sistema multi-agente con Groq (Llama 3)...")
        research_agent = NewsResearchAgent()
        article_agent = ArticleGenerationAgent(retriever=retriever)
        fact_checker = FactCheckingAgent()
        social_manager = SocialMediaAgent()
        chatbot = ReaderInteractionAgent()
        translator = MultilingualAgent()
        print("[+] Agentes listos.\n")

        # 3. Pipeline Colaborativo
        tema_investigacion = "Noticias más importantes de hoy a nivel nacional e internacional."
        
        print("--- 1. INVESTIGACIÓN DE NOTICIAS (News Research Agent) ---")
        ideas = research_agent.research_trends(tema_investigacion)
        print(ideas, "\n")

        print("--- 2. GENERACIÓN DE ARTÍCULO (Article Generation Agent + RAG + Internet Research) ---")
        # Ahora pasamos los resultados de la investigación en vivo como contexto directo
        articulo = article_agent.generate_article(tema_investigacion, direct_context=ideas)
        print(articulo, "\n")

        print("--- 3. FACT-CHECKING (Fact Checking Agent + Live Search) ---")
        verificacion = fact_checker.verify_information(articulo)
        print(verificacion, "\n")
        
        print("--- 4. ADAPTACIÓN MULTILINGÜE (Multilingual Agent) ---")
        traducciones = translator.adapt_to_languages(articulo)
        print(traducciones, "\n")
        
        print("--- 5. REDES SOCIALES (Social Media Agent) ---")
        posts_raw = social_manager.create_posts(articulo)
        
        # Intentar parsear el JSON de redes sociales para una mejor visualización de una manera más robusta
        import json
        try:
            # Encontrar el bloque JSON si hay texto extra
            start = posts_raw.find('{')
            end = posts_raw.rfind('}') + 1
            if start != -1 and end != 0:
                posts_data = json.loads(posts_raw[start:end])
                print(f"🐦 TWEET (Twitter): {posts_data.get('tweet', 'N/A')}")
                print(f"📸 INSTAGRAM: {posts_data.get('instagram', 'N/A')}")
            else:
                print(posts_raw)
        except Exception:
            print(posts_raw)
        print("\n")

        print("--- 6. INTERACCIÓN CON EL LECTOR DIGITAL (Reader Interaction Agent) ---")
        mensaje_lector = "¿Cómo puedo participar en los talleres de teatro mencionados?"
        print(f"Lector dice: '{mensaje_lector}'")
        chat_response = chatbot.chat_with_reader(mensaje_lector)
        print(f"Respuesta del Chatbot: {chat_response}\n")

        print("=== Pipeline automatizado Groq completado con éxito ===")

    except Exception as e:
        print(f"\n[!] Ocurrió un error durante la ejecución del pipeline: {e}")

if __name__ == "__main__":
    main()