import os
import sys
from dotenv import load_dotenv

# Reconfigurar la salida estándar para manejar emojis/caracteres especiales en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Cargar variables de entorno PRIMERO
load_dotenv()

# Importar agentes (Versión Brave)
from agents.news_research_agent2_brave import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2_brave import FactCheckingAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.multilingual_agent import MultilingualAgent

# Importar herramientas RAG
from rag.vector_store import build_vector_store, get_rag_retriever

def main():
    print("===================================================================")
    print("   PLATAFORMA AI - MODERNIZACIÓN DEL PERIÓDICO (BRAVE SEARCH)  ")
    print("===================================================================\n")
    
    if not os.getenv("GROQ_API_KEY") or "gsk_" not in os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY no configurada.")
        return

    if not os.getenv("BRAVE_SEARCH_API_KEY"):
        print("Aviso: BRAVE_SEARCH_API_KEY no configurada. La búsqueda fallará.")

    try:
        # Preparar RAG
        from rag.vector_store import load_vector_store, load_from_directory, save_vector_store
        DATA_DIR = "archive_data"
        vector_store = load_vector_store()
        if not vector_store:
            vector_store = load_from_directory(DATA_DIR)
            if vector_store: save_vector_store(vector_store)
        
        retriever = get_rag_retriever(vector_store)

        # Inicializar Agentes
        research_agent = NewsResearchAgent()
        article_agent = ArticleGenerationAgent(retriever=retriever)
        fact_checker = FactCheckingAgent()
        social_manager = SocialMediaAgent()
        chatbot = ReaderInteractionAgent()
        translator = MultilingualAgent()
        print("[+] Agentes con Brave Search listos.\n")

        tema_investigacion = "Noticias más importantes de hoy a nivel nacional e internacional."
        
        print("--- 1. INVESTIGACIÓN DE NOTICIAS (Brave) ---")
        ideas = research_agent.research_trends(tema_investigacion)
        print(ideas, "\n")

        print("--- 2. GENERACIÓN DE ARTÍCULO ---")
        articulo = article_agent.generate_article(tema_investigacion, direct_context=ideas)
        print(articulo, "\n")

        print("--- 3. FACT-CHECKING (Brave) ---")
        verificacion = fact_checker.verify_information(articulo)
        print(verificacion, "\n")
        
        print("=== Pipeline automatizado con Brave completado ===")

    except Exception as e:
        print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()
