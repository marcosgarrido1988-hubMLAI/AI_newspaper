# Usa una imagen oficial de Python ligera
FROM python:3.12-slim

# Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear un usuario no root para seguridad (Hugging Face usa el ID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copiar el archivo de requisitos e instalar dependencias
# Se usa --no-cache-dir para mantener la imagen ligera
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY --chown=user . .

# Exponer el puerto que usa Hugging Face Spaces por defecto
EXPOSE 7860

# Comando para arrancar la aplicación
# Usamos el puerto 7860 que es el estándar de Hugging Face
CMD ["python", "-m", "uvicorn", "api_main_brave:app", "--host", "0.0.0.0", "--port", "7860"]
