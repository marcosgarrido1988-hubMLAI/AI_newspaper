import os
import sys
import logging
import json
from dotenv import load_dotenv

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SynergyTest")

# Cargar entorno
load_dotenv()

# Ajustar path
sys.path.append(os.getcwd())

from agents.news_research_agent2 import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2 import FactCheckingAgent
from agents.multilingual_agent import MultilingualAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from rag.vector_store import load_vector_store, get_rag_retriever

def test_synergy():
    logger.info("=== STARTING SYNERGY TEST ===")
    
    # 1. Init RAG
    logger.info("Testing RAG loading...")
    vs = load_vector_store()
    retriever = get_rag_retriever(vs)
    if retriever:
        logger.info("[OK] Retriever loaded.")
    else:
        logger.warning("[!] No vector store found, proceeding without RAG context.")

    # 2. Init Agents
    logger.info("Initializing all agents...")
    researcher = NewsResearchAgent()
    writer = ArticleGenerationAgent(retriever=retriever)
    checker = FactCheckingAgent()
    translator = MultilingualAgent()
    social = SocialMediaAgent()
    chatbot = ReaderInteractionAgent()
    logger.info("[OK] All agents initialized.")

    # 3. Execution Pipeline
    topic = "El futuro de la inteligencia artificial en los periódicos locales"
    
    logger.info(f"Step 1: Researching topic: {topic}")
    res_data = researcher.research_trends(topic)
    logger.info(f"[OK] Research results (lang: {res_data['language']})")
    
    logger.info("Step 2: Generating article...")
    article = writer.generate_article(topic, direct_context=res_data['ideas'])
    logger.info(f"[OK] Article generated ({len(article)} chars).")
    
    logger.info("Step 3: Fact-checking...")
    verification = checker.verify_information(article)
    logger.info("[OK] Fact-check complete.")
    
    logger.info("Step 4: Multilingual adaptation...")
    translations_raw = translator.adapt_to_languages(article)
    try:
        translations = json.loads(translations_raw)
        logger.info(f"[OK] Translations generated for {list(translations.keys())}")
    except:
        logger.error(f"[FAIL] Could not parse translations JSON. Raw output: {translations_raw[:100]}...")

    logger.info("Step 5: Social media posts...")
    posts_raw = social.create_posts(article)
    try:
        posts = json.loads(posts_raw)
        logger.info(f"[OK] Social posts generated: {list(posts.keys())}")
    except:
        logger.error(f"[FAIL] Could not parse social posts JSON. Raw output: {posts_raw[:100]}...")

    logger.info("Step 6: Chatbot interaction...")
    chat_resp = chatbot.chat_with_reader("¿Cómo afecta la IA a los periodistas?", article_context=article)
    logger.info(f"[OK] Chatbot responded: {chat_resp[:50]}...")

    logger.info("=== SYNERGY TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY not found in environment. Please check .env")
        sys.exit(1)
    
    try:
        test_synergy()
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
