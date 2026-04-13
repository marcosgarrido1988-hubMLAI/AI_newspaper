import os
import sys
import traceback

# --- EXTREME DEBUGGING START ---
print("\n" + "="*50, flush=True)
print("APP INITIALIZATION STARTED", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Current Working Directory: {os.getcwd()}", flush=True)
print(f"Files in root: {os.listdir('.')}", flush=True)
print("="*50 + "\n", flush=True)

try:
    print("Pre-importing standard libraries...", flush=True)
    import os
    import sys
    from typing import List, Optional
    
    print("Setting up sys.path...", flush=True)
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    print(f"Root path: {root_path}", flush=True)
    
    print("Importing FastAPI and core modules...", flush=True)
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from dotenv import load_dotenv

    print("Importing custom agents and RAG...", flush=True)
    # Importar agentes
    from agents.news_research_agent2 import NewsResearchAgent
    from agents.article_generation_agent2 import ArticleGenerationAgent
    from agents.fact_checking_agent2 import FactCheckingAgent
    from agents.reader_interaction_agent2 import ReaderInteractionAgent
    from agents.social_media_agent2 import SocialMediaAgent
    from agents.multilingual_agent import MultilingualAgent

    # Importar herramientas RAG
    from rag.vector_store import load_vector_store, get_rag_retriever
    
    print("Imports complete. Initializing app...", flush=True)
    load_dotenv()
    
    app = FastAPI(title="AI Newspaper API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Servir archivos estáticos
    try:
        if os.path.exists("index.html"):
            app.mount("/static", StaticFiles(directory="."), name="static")
            print("Static files mounted.", flush=True)
    except Exception as e:
        print(f"Static mounting warning: {e}", flush=True)

    # Modelos
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

    class NewspaperService:
        def __init__(self):
            print("Constructor: Loading vector store...", flush=True)
            self.vector_store = load_vector_store()
            self.retriever = get_rag_retriever(self.vector_store) if self.vector_store else None
            self.last_article = ""
            
            print("Constructor: Initializing agents...", flush=True)
            self.research_agent = NewsResearchAgent()
            self.article_agent = ArticleGenerationAgent(retriever=self.retriever)
            self.fact_checker = FactCheckingAgent()
            self.social_manager = SocialMediaAgent()
            self.chatbot = ReaderInteractionAgent()
            self.translator = MultilingualAgent()

    _service_instance = None

    def get_service():
        global _service_instance
        if _service_instance is None:
            print("FACTORY: Initializing NewspaperService...", flush=True)
            _service_instance = NewspaperService()
        return _service_instance

    @app.get("/")
    async def root():
        print("GET / triggered", flush=True)
        if os.path.exists("index.html"):
            return FileResponse("index.html")
        return {"message": "Server running, index.html missing"}

    @app.post("/run-pipeline", response_model=PipelineResponse)
    async def run_pipeline(request: ResearchRequest):
        try:
            service = get_service()
            topic = request.topic
            print(f"PIPELINE: Topic = {topic}", flush=True)
            
            ideas = service.research_agent.research_trends(topic)
            article = service.article_agent.generate_article(topic, direct_context=ideas)
            service.last_article = article
            verification = service.fact_checker.verify_information(article)
            translations = service.translator.adapt_to_languages(article)
            posts_raw = service.social_manager.create_posts(article)
            
            import json
            social_posts = {"tweet": "N/A", "instagram": "N/A"}
            try:
                start = posts_raw.find('{')
                end = posts_raw.rfind('}') + 1
                if start != -1 and end != 0:
                    social_posts = json.loads(posts_raw[start:end])
            except: pass
                
            return PipelineResponse(
                topic=topic, ideas=ideas, article=article,
                verification=verification, translations=translations,
                social_posts=social_posts
            )
        except Exception as e:
            print(f"PIPELINE ERROR: {e}", flush=True)
            traceback.print_exc(file=sys.stdout)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/chat")
    async def chat(request: ChatRequest):
        try:
            service = get_service()
            response = service.chatbot.chat_with_reader(
                request.message, 
                article_context=service.last_article
            )
            return {"response": response}
        except Exception as e:
            print(f"CHAT ERROR: {e}", flush=True)
            raise HTTPException(status_code=500, detail=str(e))

    print("APP DEFINED SUCCESSFULLY", flush=True)

except Exception as e:
    print("\n" + "!"*50, flush=True)
    print("FATAL ERROR DURING INITIALIZATION:", flush=True)
    print(str(e), flush=True)
    traceback.print_exc(file=sys.stdout)
    print("!"*50 + "\n", flush=True)
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
