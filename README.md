# 🎵 YT Audio Pro

Una aplicación web moderna para extraer y descargar audio en MP3 desde YouTube, compatible con vídeos individuales y playlists completas. Construida con Streamlit y yt-dlp, lista para desplegar con Docker.

---

## ✨ Características

- **Vídeos y playlists** — Pega cualquier enlace de YouTube: un vídeo suelto o una playlist de hasta 200 entradas.
- **Selección de calidad** — Elige entre 128, 192 o 320 kbps antes de descargar.
- **Descarga individual** — Prepara y descarga solo los audios que necesitas, sin procesar toda la lista.
- **Metadatos y miniatura** — Cada MP3 incluye título, artista y portada incrustada.
- **Reintentos** — Los vídeos que fallan muestran el motivo del error y un botón para reintentar.
- **Sin dependencias externas de pago** — 100 % open source.

---

## 🖥️ Capturas

> *Interfaz con tema oscuro, selector de calidad y lista de resultados con duración por pista.*
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1ae918fd-87f0-4b8c-a634-65f24a203f12" />

---

## 🚀 Despliegue rápido con Docker

La forma recomendada de ejecutar la app es con Docker, ya que incluye FFmpeg y todas las dependencias.

**1. Clona el repositorio**

```bash
git clone https://github.com/wwwPABLOcom/yt-mp3.git
cd yt-audio-pro
```

**2. Construye la imagen**

```bash
docker build -t yt-audio-pro .
```

**3. Ejecuta el contenedor**

```bash
docker run -p 8501:8501 yt-audio-pro
```

**4. Abre la app**

```
http://localhost:8501
```

---

## 🛠️ Desarrollo local (sin Docker)

### Requisitos previos

- Python 3.10+
- FFmpeg instalado y disponible en el `PATH`

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — descargar desde https://ffmpeg.org/download.html
```

### Instalación

```bash
# Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run app.py
```

---

## 📁 Estructura del proyecto

```
yt-audio-pro/
├── app.py              # Aplicación principal (lógica + interfaz)
├── requirements.txt    # Dependencias Python con versiones fijadas
├── Dockerfile          # Imagen Docker lista para producción
└── README.md
```

---

## ⚙️ Stack técnico

| Componente | Tecnología |
|---|---|
| Interfaz web | [Streamlit](https://streamlit.io) 1.57 |
| Extracción de audio | [yt-dlp](https://github.com/yt-dlp/yt-dlp) 2026.3.17 |
| Conversión a MP3 | FFmpeg (vía yt-dlp postprocessors) |
| Miniaturas | Pillow 12 + FFmpegThumbnailsConvertor |
| Contenedor | Docker (python:3.10-slim) |

---

## 🔒 Seguridad y buenas prácticas

- El contenedor Docker corre con un **usuario no-root** (`appuser`).
- Las URLs se validan antes de pasarlas al extractor.
- Los nombres de archivo se sanitizan eliminando caracteres ilegales en Windows y Linux.
- Los directorios temporales se limpian automáticamente tras cada descarga y al apagar el servidor.
- Todas las dependencias tienen **versiones fijadas** para builds reproducibles.

---

## ⚠️ Aviso legal

Esta herramienta es para uso **personal y educativo**. Descarga únicamente contenido sobre el que tengas derechos o que esté bajo una licencia que lo permita (Creative Commons, dominio público, etc.). El autor no se responsabiliza del uso indebido de la aplicación. Respeta los [Términos de Servicio de YouTube](https://www.youtube.com/t/terms).

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Abre un *issue* para reportar bugs o proponer mejoras, o envía directamente un *pull request*.

---

## 📄 Licencia

MIT License — consulta el archivo `LICENSE` para más detalles.
