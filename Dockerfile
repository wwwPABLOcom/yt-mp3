# Usamos una imagen base de Python ligera
FROM python:3.10-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos FFmpeg (vital para que yt-dlp pueda extraer el mp3)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la app
COPY app.py .

# Exponemos el puerto por defecto de Streamlit
EXPOSE 8501

# Ejecutamos Streamlit obligándolo a escuchar en todas las interfaces (0.0.0.0)
# Esto es clave para que sea accesible desde fuera del contenedor y de tu host
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
