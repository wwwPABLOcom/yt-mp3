import streamlit as st
import os
import tempfile
import yt_dlp
import zipfile
import shutil
import uuid

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(
    page_title="YouTube MP3 Downloader",
    page_icon="🎵",
    layout="centered"
)

# ==========================================
# CSS ADAPTADO (Oculto por brevedad, mantén el tuyo)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #07071a; color: #e8e6f0; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 5rem 2rem; max-width: 800px; z-index: 1; }
    .hero-wrap { text-align: center; padding: 3rem 1rem 2.5rem 1rem; }
    .hero-title { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #e0d7ff 10%, #a78bfa 45%, #7c3aed 70%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.6rem; }
    .hero-sub { color: #8b88a8; max-width: 480px; margin: 0 auto; }
    .glass-card { background: rgba(255, 255, 255, 0.035); backdrop-filter: blur(12px); border: 1px solid rgba(167, 139, 250, 0.14); border-radius: 20px; padding: 1.75rem 2rem; margin-bottom: 1.25rem; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(167, 139, 250, 0.22) !important; border-radius: 12px !important; color: #e8e6f0 !important; }
    .stButton > button, .stDownloadButton > button { width: 100%; background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 50%, #5b21b6 100%) !important; color: #f3f0ff !important; border-radius: 12px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MANEJO DE ESTADO
# ==========================================
if 'file_data' not in st.session_state:
    st.session_state.file_data = None
    st.session_state.file_name = None
    st.session_state.mime_type = None

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">Downloader MP3</div>
    <div class="hero-sub">
        Pega un enlace de YouTube. ¡Soporta videos individuales y Playlists enteras!
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# LÓGICA DE DESCARGA (VIDEOS Y PLAYLISTS)
# ==========================================
def descargar_audio_youtube(url):
    # Creamos una carpeta temporal única para esta descarga para evitar conflictos
    run_id = uuid.uuid4().hex
    tmp_dir = os.path.join(tempfile.gettempdir(), run_id)
    os.makedirs(tmp_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'mp3', 
            'preferredquality': '192'
        }],
        # Nombramos los archivos con su índice de playlist (si aplica) y título
        'outtmpl': os.path.join(tmp_dir, '%(playlist_index)s_%(title)s.%(ext)s'), 
        'quiet': True, 
        'no_warnings': True,
        'ignoreerrors': True, # Si un video de la playlist está borrado, lo salta y sigue
    }
    
    with st.spinner("⬇️ Extrayendo y convirtiendo... (Si es una playlist, ve a hacerte un café ☕)"):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                titulo_principal = info_dict.get('title', 'YouTube_Audio')

            # Revisamos qué se ha descargado en nuestra carpeta temporal
            archivos_descargados = [f for f in os.listdir(tmp_dir) if f.endswith('.mp3')]
            
            if not archivos_descargados:
                return None, None, None

            # CASO 1: Es un solo video
            if len(archivos_descargados) == 1:
                ruta_mp3 = os.path.join(tmp_dir, archivos_descargados[0])
                with open(ruta_mp3, "rb") as file:
                    data = file.read()
                
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return data, f"{titulo_principal}.mp3", "audio/mpeg"
                
            # CASO 2: Es una Playlist (Múltiples archivos) -> Comprimimos en ZIP
            else:
                zip_filename = f"{titulo_principal}_playlist.zip"
                zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for archivo in archivos_descargados:
                        ruta_archivo = os.path.join(tmp_dir, archivo)
                        # Limpiamos el "NA_" del nombre si yt-dlp no encontró índice
                        nombre_limpio = archivo.replace("NA_", "") 
                        zipf.write(ruta_archivo, arcname=nombre_limpio)
                
                with open(zip_path, "rb") as file:
                    data = file.read()
                
                # Limpieza de temporales
                shutil.rmtree(tmp_dir, ignore_errors=True)
                os.remove(zip_path)
                
                return data, zip_filename, "application/zip"

        except Exception as e:
            st.error(f"❌ Error en la descarga: {e}")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return None, None, None

# ==========================================
# INTERFAZ DE ENTRADA
# ==========================================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

youtube_url = st.text_input("Enlace del vídeo o Playlist", placeholder="https://www.youtube.com/watch?v=... o &list=...")

if st.button("🎵 Preparar Descarga"):
    if youtube_url:
        st.session_state.file_data = None  
        data, filename, mime = descargar_audio_youtube(youtube_url)
        
        if data:
            st.session_state.file_data = data
            st.session_state.file_name = filename
            st.session_state.mime_type = mime
            st.success("✅ ¡Procesamiento completado!")
    else:
        st.warning("⚠️ Por favor, introduce un enlace de YouTube válido.")

# Botón de descarga adaptativo (MP3 o ZIP)
if st.session_state.file_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label=f"💾 Guardar: {st.session_state.file_name}",
        data=st.session_state.file_data,
        file_name=st.session_state.file_name,
        mime=st.session_state.mime_type
    )

st.markdown('</div>', unsafe_allow_html=True)
