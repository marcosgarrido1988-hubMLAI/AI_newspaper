import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Importaciones locales (en local no necesitamos lazy loading agresivo)
from agents.news_research_agent2 import NewsResearchAgent
from agents.article_generation_agent2 import ArticleGenerationAgent
from agents.fact_checking_agent2 import FactCheckingAgent
from agents.reader_interaction_agent2 import ReaderInteractionAgent
from agents.social_media_agent2 import SocialMediaAgent
from agents.multilingual_agent import MultilingualAgent
from rag.vector_store import load_vector_store, get_rag_retriever

load_dotenv()

app = FastAPI(title="AI Newspaper - Versión Local")

# CORS para permitir el desarrollo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del directorio actual
app.mount("/static", StaticFiles(directory="."), name="static")

# Modelos
class ResearchRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str

class NewspaperService:
    def __init__(self):
        print("--- Inicilizando AI Newspaper (Modo Local) ---")
        self.vector_store = load_vector_store()
        self.retriever = get_rag_retriever(self.vector_store) if self.vector_store else None
        
        self.research_agent = NewsResearchAgent()
        self.article_agent = ArticleGenerationAgent(retriever=self.retriever)
        self.fact_checker = FactCheckingAgent()
        self.social_manager = SocialMediaAgent()
        self.chatbot = ReaderInteractionAgent()
        self.translator = MultilingualAgent()
        
        self.last_article = ""
        print("--- Sistema Listo ---")

# Instancia única del servicio
service = NewspaperService()

@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("index.html")

@app.post("/run-pipeline")
async def run_pipeline(request: ResearchRequest):
    try:
        topic = request.topic
        print(f"Ejecutando pipeline para: {topic}")
        
        ideas = service.research_agent.research_trends(topic)
        article = service.article_agent.generate_article(topic, direct_context=ideas)
        service.last_article = article
        verification = service.fact_checker.verify_information(article)
        translations = service.translator.adapt_to_languages(article)
        posts_raw = service.social_manager.create_posts(article)
        
        # Parseo simple de posts sociales
        import json
        social_posts = {"tweet": "N/A", "instagram": "N/A"}
        try:
            start = posts_raw.find('{')
            end = posts_raw.rfind('}') + 1
            if start != -1 and end != 0:
                social_posts = json.loads(posts_raw[start:end])
        except: pass
            
        return {
            "topic": topic, "ideas": ideas, "article": article,
            "verification": verification, "translations": translations,
            "social_posts": social_posts
        }
    except Exception as e:
        print(f"Error: {e}")
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
    # Puerto 8000 por defecto para local
    print("Iniciando servidor local en http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
