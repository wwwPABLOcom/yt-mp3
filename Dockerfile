# Imagen base ligera de Python 3.10
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Instalamos FFmpeg minimizando el tamaño de la imagen
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Creamos un usuario no-root para ejecutar la app de forma segura
RUN useradd --create-home --shell /bin/bash appuser

# Instalamos dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código y ajustamos permisos
COPY app.py .
RUN chown -R appuser:appuser /app

# Cambiamos al usuario no-root
USER appuser

# Puerto de Streamlit
EXPOSE 8501

# Ejecutamos la app escuchando en todas las interfaces
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
