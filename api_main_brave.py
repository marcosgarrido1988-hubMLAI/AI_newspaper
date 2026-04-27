import os
import sys
import traceback
import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import List, Optional

# --- CONFIGURACIÓN DE LOGS ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajuste de path para importaciones locales
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)

import mimetypes
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Importaciones de Agentes y RAG (Versión Brave para búsqueda)
from rag.vector_store import load_vector_store, get_rag_retriever
from agents.news_research_agent2_brave import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2_brave import FactCheckingAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.multilingual_agent import MultilingualAgent

load_dotenv()

class NewspaperService:
    def __init__(self):
        logger.info("Initializing NewspaperService (Brave Search Mode)...")
        
        # 1. Cargar RAG
        self.vector_store = load_vector_store()
        self.retriever = get_rag_retriever(self.vector_store) if self.vector_store else None
        
        # 2. Inicializar Agentes (Usando versiones Brave)
        self.research_agent = NewsResearchAgent()
        self.article_agent = ArticleGenerationAgent(retriever=self.retriever)
        self.fact_checker = FactCheckingAgent()
        self.social_manager = SocialMediaAgent()
        self.chatbot = ReaderInteractionAgent()
        self.translator = MultilingualAgent()
        
        self.last_article = ""
        logger.info("NewspaperService successfully initialized with Brave Search.")

# Instancia global (será inicializada en el lifespan)
service: Optional[NewspaperService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    try:
        service = NewspaperService()
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        traceback.print_exc()
    yield

app = FastAPI(title="AI Newspaper API (Brave)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir estáticos
index_path = os.path.join(root_path, "index.html")
style_path = os.path.join(root_path, "style.css")
script_path = os.path.join(root_path, "script.js")

@app.get("/style.css")
async def get_css():
    if os.path.exists(style_path):
        return FileResponse(style_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")

@app.get("/script.js")
async def get_js():
    if os.path.exists(script_path):
        return FileResponse(script_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")

class ResearchRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str

class TranslationRequest(BaseModel):
    article: str
    target_lang: str

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AI Newspaper (Brave)</h1><p>Server is running but index.html was not found.</p>")

@app.post("/run-pipeline")
async def run_pipeline(request: ResearchRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        topic = request.topic
        logger.info(f"PIPELINE START (BRAVE): Topic = {topic}")
        
        res_data = service.research_agent.research_trends(topic)
        ideas = res_data["ideas"]
        detected_lang = res_data["language"]
        
        article = service.article_agent.generate_article(topic, direct_context=ideas, target_lang=detected_lang)
        service.last_article = article
        
        verification = service.fact_checker.verify_information(article)
        
        return {
            "topic": topic, 
            "ideas": ideas, 
            "article": article,
            "verification": verification, 
            "detected_lang": detected_lang
        }
    except Exception as e:
        logger.error(f"PIPELINE ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        response = service.chatbot.chat_with_reader(request.message, article_context=service.last_article)
        return {"response": response}
    except Exception as e:
        logger.error(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

LANG_KEY_TO_NAME = {
    "spanish":    "Spanish",
    "english":    "English",
    "german":     "German",
    "pinyin":     "Mandarin Chinese written in Pinyin romanization",
    "dutch":      "Dutch",
    "portuguese": "Portuguese",
    "italian":    "Italian",
}

@app.post("/translate")
async def translate(request: TranslationRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    import json, re
    try:
        raw_key = request.target_lang.lower().strip()
        lang_name = LANG_KEY_TO_NAME.get(raw_key, request.target_lang)
        translation_json = service.translator.translate_article_to(request.article, lang_name)
        
        clean = re.sub(r'```[a-z]*', '', translation_json).strip()
        start = clean.find('{')
        end = clean.rfind('}') + 1
        
        if start != -1:
            json_str = clean[start:end] if end > start else clean[start:]
            parsed_result = json.loads(json_str)
        else:
            parsed_result = {"title": f"[{lang_name}]", "body": translation_json}
            
        return {"title": parsed_result.get('title', ''), "body": parsed_result.get('body', '')}
    except Exception as e:
        logger.error(f"TRANSLATION ERROR: {e}")
        return {"title": f"Traducción a {request.target_lang}", "body": "Error en traducción"}

@app.post("/social-posts")
async def social_posts(request: ResearchRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        posts_raw = service.social_manager.create_posts(request.topic)
        import json
        return json.loads(posts_raw)
    except Exception as e:
        return {"tweet": "N/A", "instagram": "N/A"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
