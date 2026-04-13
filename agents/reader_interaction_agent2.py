import logging
import os
import sys

# Ajuste de path para permitir ejecución independiente de los agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from llm_config import get_groq_llm

logger = logging.getLogger(__name__)

class ReaderInteractionAgent:
    """Chatbot con memoria para interactuar con lectores usando Groq."""
    def __init__(self):
        self.llm = get_groq_llm(temperature=0.7)
        self.store = {}

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres el asistente virtual oficial de nuestro periódico local. 
            Tu personalidad es útil, moderna, empática y amigable. 
            Mantén tus respuestas claras, conversacionales y basadas en el contexto de la conversación.
            
            Si el lector hace preguntas sobre la noticia actual, utiliza la siguiente información para responder:
            --- NOTICIA ACTUAL ---
            {article_context}
            ----------------------"""),
            MessagesPlaceholder(variable_name="history"), 
            ("human", "{message}")
        ])

        if self.llm:
            chain = prompt | self.llm
            self.with_message_history = RunnableWithMessageHistory(
                chain,
                self.get_session_history,
                input_messages_key="message",
                history_messages_key="history",
            )
        else:
            self.with_message_history = None
    
    def get_session_history(self, session_id: str):
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def chat_with_reader(self, user_message: str, article_context: str = "", session_id: str = "default_user") -> str:
        if not self.with_message_history: 
            return "Error: LLM o cadena con memoria no inicializados."

        context = article_context if article_context else "(No hay noticias recientes generadas aún)."

        try:
            response = self.with_message_history.invoke(
                {
                    "message": user_message,
                    "article_context": context
                },
                config={"configurable": {"session_id": session_id}}
            )
            return response.content
        except Exception as e:
            logger.error(f"Error en la interacción con memoria: {e}")
            return "Lo siento, tuve un problema al recordar nuestra conversación."

if __name__ == "__main__":
    agent = ReaderInteractionAgent()
    print(agent.chat_with_reader("Hola, ¿qué tipo de noticias cubren?"))
