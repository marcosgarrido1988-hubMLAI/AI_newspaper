import os
import sys
from dotenv import load_dotenv

# Reconfigurar la salida estándar para manejar emojis/caracteres especiales en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Cargar variables de entorno (GROQ_API_KEY)
load_dotenv()

# 2. Importar el agente de interacción
from agents.reader_interaction_agent2 import ReaderInteractionAgent

def terminal_chatbot():
    """Lanza una interfaz de chat interactiva en la terminal."""
    
    print("===================================================================")
    print("   CHATBOT - PERIÓDICO LOCAL (GROQ)  ")
    print("   Escribe 'salir' para finalizar la conversación.")
    print("===================================================================\n")
    
    # 3. Comprobación de API key
    if not os.getenv("GROQ_API_KEY") or "gsk_" not in os.getenv("GROQ_API_KEY"):
        print("[!] Error: No se encontró GROQ_API_KEY en el archivo .env")
        return

    # 4. Inicializar Agente
    print("[*] Conectando con Groq...conexión establecida")
    chatbot = ReaderInteractionAgent()
    print("[+] Chatbot listo. Buenos días guapada, en qué puedo serte de ayuda hoy?.\n")

    # 5. Bucle de interacción
    session_id = "user_session_1"
    
    while True:
        try:
            user_input = input("Tú: ")
            
            if user_input.lower() in ["salir", "exit", "quit", "adios", "adiós"]:
                print("\nChatbot: ¡Hasta pronto! Que tengas un gran día.\n")
                break
                
            if not user_input.strip():
                continue
                
            # Obtener respuesta del chatbot
            response = chatbot.chat_with_reader(user_input, session_id=session_id)
            
            print(f"Chatbot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nChatbot: Interrupción detectada. ¡Por fin te vas. Adiós, y espero que para siempre!")
            break
        except Exception as e:
            print(f"\n[!] Ocurrió un error inesperado: {e}")
            break

if __name__ == "__main__":
    terminal_chatbot()
