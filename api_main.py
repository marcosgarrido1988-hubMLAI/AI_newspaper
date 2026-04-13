import os
import sys

# Forzar inclusión del directorio raíz en el PATH para evitar ModuleNotFoundError en Render
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Importar agentes
from agents.news_research_agent2 import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2 import FactCheckingAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.multilingual_agent import MultilingualAgent

# Importar herramientas RAG
from rag.vector_store import load_vector_store, get_rag_retriever

load_dotenv()

app = FastAPI(title="AI Newspaper API")

# Configurar CORS para permitir peticiones desde el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, limita esto al dominio de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (CSS, JS, imágenes)
# El primer argumento es la ruta en la URL, el segundo es la carpeta física
app.mount("/static", StaticFiles(directory="."), name="static")

# Modelos de datos
class ResearchRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str

class PipelineResponse(BaseModel):
    topic: str
    ideas: str
    article: str
    verification: str
    translations: str
    social_posts: dict

# Inicializar componentes (Singleton pattern para los agentes)
class NewspaperService:
    def __init__(self):
        self.vector_store = load_vector_store()
        self.retriever = get_rag_retriever(self.vector_store) if self.vector_store else None
        self.last_article = "" # Almacenar la última noticia generada
        
        self.research_agent = NewsResearchAgent()
        self.article_agent = ArticleGenerationAgent(retriever=self.retriever)
        self.fact_checker = FactCheckingAgent()
        self.social_manager = SocialMediaAgent()
        self.chatbot = ReaderInteractionAgent()
        self.translator = MultilingualAgent()

service = NewspaperService()

@app.get("/")
async def root():
    # Servir el index.html como la página principal
    return FileResponse("index.html")

@app.post("/run-pipeline", response_model=PipelineResponse)
async def run_pipeline(request: ResearchRequest):
    try:
        topic = request.topic
        
        # 1. Investigación
        ideas = service.research_agent.research_trends(topic)
        
        # 2. Generación
        article = service.article_agent.generate_article(topic, direct_context=ideas)
        service.last_article = article # Guardar contexto para el chat
        
        # 3. Fact-Checking
        verification = service.fact_checker.verify_information(article)
        
        # 4. Traducción
        translations = service.translator.adapt_to_languages(article)
        
        # 5. Redes Sociales
        posts_raw = service.social_manager.create_posts(article)
        
        # Parsear JSON de redes sociales
        import json
        social_posts = {"tweet": "N/A", "instagram": "N/A"}
        try:
            start = posts_raw.find('{')
            end = posts_raw.rfind('}') + 1
            if start != -1 and end != 0:
                social_posts = json.loads(posts_raw[start:end])
        except:
            pass
            
        return PipelineResponse(
            topic=topic,
            ideas=ideas,
            article=article,
            verification=verification,
            translations=translations,
            social_posts=social_posts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = service.chatbot.chat_with_reader(
            request.message, 
            article_context=service.last_article
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
