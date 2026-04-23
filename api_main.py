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

# Importaciones de Agentes y RAG (Sin carga perezosa)
from rag.vector_store import load_vector_store, get_rag_retriever
from agents.news_research_agent2 import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2 import FactCheckingAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.multilingual_agent import MultilingualAgent

load_dotenv()

class NewspaperService:
    def __init__(self):
        logger.info("Initializing NewspaperService (Full Load Mode)...")
        
        # 1. Cargar RAG
        self.vector_store = load_vector_store()
        self.retriever = get_rag_retriever(self.vector_store) if self.vector_store else None
        
        # 2. Inicializar Agentes
        self.research_agent = NewsResearchAgent()
        self.article_agent = ArticleGenerationAgent(retriever=self.retriever)
        self.fact_checker = FactCheckingAgent()
        self.social_manager = SocialMediaAgent()
        self.chatbot = ReaderInteractionAgent()
        self.translator = MultilingualAgent()
        
        self.last_article = ""
        logger.info("NewspaperService successfully initialized.")

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
    # Limpieza si fuera necesaria

app = FastAPI(title="AI Newspaper API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir estáticos directamente para evadir fallos de IFrame y Proxy en HuggingFace
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

# Modelos
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
    return HTMLResponse("<h1>AI Newspaper</h1><p>Server is running but index.html was not found.</p>")

@app.post("/run-pipeline")
async def run_pipeline(request: ResearchRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        topic = request.topic
        logger.info(f"PIPELINE START: Topic = {topic}")
        
        # 1. Investigación
        res_data = service.research_agent.research_trends(topic)
        ideas = res_data["ideas"]
        detected_lang = res_data["language"]
        logger.info("PIPELINE: Research done.")
        
        # 2. Generación
        article = service.article_agent.generate_article(topic, direct_context=ideas, target_lang=detected_lang)
        service.last_article = article
        logger.info("PIPELINE: Generation done.")
        
        # 3. Verificación (Hacemos esperar al usuario por esto como se pidió)
        verification = service.fact_checker.verify_information(article)
        logger.info("PIPELINE: Factcheck done.")
        
        # 4. Redes Sociales (Opcional: se puede llamar aparte para fluidez)
        # Por ahora lo mantenemos disponible pero el frontend decidirá si lo usa
        
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
        response = service.chatbot.chat_with_reader(
            request.message, 
            article_context=service.last_article
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mapeo de claves internas del frontend a nombres de idioma reales para el LLM
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
        # Convertir clave interna ('german') al nombre real ('German')
        raw_key = request.target_lang.lower().strip()
        lang_name = LANG_KEY_TO_NAME.get(raw_key, request.target_lang)
        logger.info(f"TRANSLATE: key='{raw_key}' → lang_name='{lang_name}'")
        
        translation_json = service.translator.translate_article_to(
            request.article, 
            lang_name
        )
        logger.info(f"TRANSLATE raw response (first 200 chars): {translation_json[:200]}")
        
        clean = re.sub(r'```[a-z]*', '', translation_json).strip()
        start = clean.find('{')
        end = clean.rfind('}') + 1
        
        import codecs
        
        parsed_result = None
        
        if start != -1:
            json_str = clean[start:end] if end > start else clean[start:]
            try:
                parsed_result = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("JSON parser failed, attempting regex salvage...")
                title_match = re.search(r'"title"\s*:\s*"([^"]*)', json_str)
                body_match = re.search(r'"body"\s*:\s*"(.*)', json_str, re.DOTALL)
                salvaged_title = title_match.group(1) if title_match else f"[{lang_name}] Traducción"
                salvaged_body = body_match.group(1).rstrip('}').rstrip('"').strip() if body_match else json_str
                salvaged_body = salvaged_body.replace('\\n', '\n')
                parsed_result = {"title": salvaged_title, "body": salvaged_body}
        else:
            logger.warning("TRANSLATE: No JSON object found, returning raw text.")
            parsed_result = {"title": f"[{lang_name}]", "body": translation_json}
            
        final_title = parsed_result.get('title', '')
        final_body = parsed_result.get('body', '')
        
        return {"title": final_title, "body": final_body}
        
    except Exception as e:
        logger.error(f"TRANSLATION ERROR: {e}")
        import traceback; traceback.print_exc()
        return {"title": f"Traducción a {request.target_lang}", "body": translation_json}

@app.post("/social-posts")
async def social_posts(request: ResearchRequest): # Reusamos modelo topic o creamos uno nuevo
    # En este caso esperamos 'topic' pero realmente necesitamos el artículo
    # Para simplificar, asumimos que el frontend envía el artículo en el campo 'topic' 
    # o mejor creamos un modelo específico.
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
