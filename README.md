# Periódico Digital AI (Versión Groq)

Este proyecto utiliza **Groq** para la inferencia ultrarrápida de LLMs y **HuggingFace** para embeddings locales. Automatiza el ciclo de vida de las noticias con un sistema multi-agente.

## Características

- **Groq Inference**: Usa Llama 3 para una respuesta casi instantánea.
- **Local RAG**: Emplea `all-MiniLM-L6-v2` de HuggingFace, permitiendo que el sistema de búsqueda funcione localmente sin costes adicionales.
- **Multi-Agente**: Investigación, redacción, verificación, redes sociales y chat con el lector.

## Configuración

1. Crea un entorno virtual: `python -m venv .venv`
2. Activa el entorno:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - CMD: `.\.venv\Scripts\activate.bat`
3. Instala dependencias: `pip install -r requirements.txt`
4. Configura tu `.env` con tu `GROQ_API_KEY`.

## Ejecución

```bash
python main2.py
```
Arrancar backend introduce este comando en el terminal -> python -m uvicorn api_main:app --reload
