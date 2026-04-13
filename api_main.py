import os
import sys
import traceback

# --- EXTREME DEBUGGING START ---
print("\n" + "="*50, flush=True)
print("APP INITIALIZATION STARTED (Surgical Fix)", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Current Working Directory: {os.getcwd()}", flush=True)
print("="*50 + "\n", flush=True)

try:
    print("Pre-importing essential libraries...", flush=True)
    import os
    import sys
    from typing import List, Optional
    
    print("Setting up sys.path...", flush=True)
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    
    print("Importing FastAPI core...", flush=True)
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from dotenv import load_dotenv

    print("Initializing environment...", flush=True)
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
        index_path = os.path.join(root_path, "index.html")
        if os.path.exists(index_path):
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
            print("Constructor: NewspaperService instantiated (Lazy Properties Mode)", flush=True)
            self._vector_store = None
            self._retriever = None
            self._research_agent = None
            self._article_agent = None
            self._fact_checker = None
            self._social_manager = None
            self._chatbot = None
            self._translator = None
            self.last_article = ""

        @property
        def vector_store(self):
            if self._vector_store is None:
                print("Lazy Load: Vector Store...", flush=True)
                from rag.vector_store import load_vector_store
                self._vector_store = load_vector_store()
            return self._vector_store

        @property
        def retriever(self):
            if self._retriever is None:
                vs = self.vector_store
                if vs:
                    from rag.vector_store import get_rag_retriever
                    self._retriever = get_rag_retriever(vs)
            return self._retriever

        @property
        def research_agent(self):
            if self._research_agent is None:
                print("Lazy Load: NewsResearchAgent...", flush=True)
                from agents.news_research_agent2 import NewsResearchAgent
                self._research_agent = NewsResearchAgent()
            return self._research_agent

        @property
        def article_agent(self):
            if self._article_agent is None:
                print("Lazy Load: ArticleGenerationAgent...", flush=True)
                from agents.article_generation_agent2 import ArticleGenerationAgent
                self._article_agent = ArticleGenerationAgent(retriever=self.retriever)
            return self._article_agent

        @property
        def fact_checker(self):
            if self._fact_checker is None:
                print("Lazy Load: FactCheckingAgent...", flush=True)
                from agents.fact_checking_agent2 import FactCheckingAgent
                self._fact_checker = FactCheckingAgent()
            return self._fact_checker

        @property
        def social_manager(self):
            if self._social_manager is None:
                print("Lazy Load: SocialMediaAgent...", flush=True)
                from agents.social_media_agent2 import SocialMediaAgent
                self._social_manager = SocialMediaAgent()
            return self._social_manager

        @property
        def chatbot(self):
            if self._chatbot is None:
                print("Lazy Load: ReaderInteractionAgent...", flush=True)
                from agents.reader_interaction_agent2 import ReaderInteractionAgent
                self._chatbot = ReaderInteractionAgent()
            return self._chatbot

        @property
        def translator(self):
            if self._translator is None:
                print("Lazy Load: MultilingualAgent...", flush=True)
                from agents.multilingual_agent import MultilingualAgent
                self._translator = MultilingualAgent()
            return self._translator

    _service_instance = None

    def get_service():
        global _service_instance
        if _service_instance is None:
            print("FACTORY: Initializing NewspaperService...", flush=True)
            _service_instance = NewspaperService()
        return _service_instance

    @app.api_route("/", methods=["GET", "HEAD"])
    async def root():
        print("Root endpoint hit (GET/HEAD).", flush=True)
        index_path = os.path.join(root_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return HTMLResponse("<h1>AI Newspaper</h1><p>Server is running but index.html was not found.</p>")

    @app.post("/run-pipeline")
    async def run_pipeline(request: ResearchRequest):
        try:
            service = get_service()
            topic = request.topic
            print(f"PIPELINE START: Topic = {topic}", flush=True)
            res_data = service.research_agent.research_trends(topic)
            ideas = res_data["ideas"]
            detected_lang = res_data["language"]
            print("PIPELINE: Research done.", flush=True)
            
            article = service.article_agent.generate_article(topic, direct_context=ideas)
            service.last_article = article
            print("PIPELINE: Generation done.", flush=True)
            
            verification = service.fact_checker.verify_information(article)
            print("PIPELINE: Factcheck done.", flush=True)
            
            translations = service.translator.adapt_to_languages(article)
            print("PIPELINE: Translation done.", flush=True)
            
            posts_raw = service.social_manager.create_posts(article)
            print("PIPELINE: Social media posts done.", flush=True)
            
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
                "social_posts": social_posts, "detected_lang": detected_lang
            }
        except Exception as e:
            print(f"PIPELINE ERROR: {e}", flush=True)
            traceback.print_exc(file=sys.stdout)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/chat")
    async def chat(request: ChatRequest):
        try:
            service = get_service()
            print(f"CHAT START: {request.message[:20]}...", flush=True)
            response = service.chatbot.chat_with_reader(
                request.message, 
                article_context=service.last_article
            )
            return {"response": response}
        except Exception as e:
            print(f"CHAT ERROR: {e}", flush=True)
            raise HTTPException(status_code=500, detail=str(e))

    print("APP DEFINED SUCCESSFULLY (Ultra Lazy Mode)", flush=True)

except Exception as e:
    print("\n" + "!"*50, flush=True)
    print("FATAL ERROR DURING INITIALIZATION:", flush=True)
    print(str(e), flush=True)
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
