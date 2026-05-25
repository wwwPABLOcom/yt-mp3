import streamlit as st
import os
import tempfile
import yt_dlp

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(
    page_title="YouTube MP3 Downloader",
    page_icon="🎵",
    layout="centered"
)

# ==========================================
# CSS ADAPTADO
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* === FONDO PRINCIPAL === */
    .stApp {
        background-color: #07071a;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(120, 60, 255, 0.25) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 110%, rgba(30, 180, 255, 0.12) 0%, transparent 55%),
            radial-gradient(ellipse 50% 50% at 50% 50%, rgba(180, 60, 120, 0.06) 0%, transparent 70%);
        min-height: 100vh;
        color: #e8e6f0;
    }

    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(120, 60, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(120, 60, 255, 0.04) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding: 1.5rem 2rem 5rem 2rem;
        max-width: 800px;
        position: relative;
        z-index: 1;
    }

    /* === HERO / HEADER === */
    .hero-wrap {
        text-align: center;
        padding: 3rem 1rem 2.5rem 1rem;
        position: relative;
    }

    .vinyl-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 320px;
        height: 320px;
        border-radius: 50%;
        background: conic-gradient(
            from 0deg,
            rgba(120, 60, 255, 0.06),
            rgba(180, 80, 255, 0.03),
            rgba(60, 180, 255, 0.06),
            rgba(120, 60, 255, 0.06)
        );
        animation: spin 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes spin {
        to { transform: translate(-50%, -50%) rotate(360deg); }
    }

    .hero-badge {
        display: inline-block;
        background: rgba(124, 58, 237, 0.12);
        border: 1px solid rgba(167, 139, 250, 0.3);
        color: #c4b5fd;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 999px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e0d7ff 10%, #a78bfa 45%, #7c3aed 70%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1.5px;
        line-height: 1.1;
        margin-bottom: 0.6rem;
        position: relative;
        z-index: 1;
    }
    .hero-sub {
        font-size: 1rem;
        color: #8b88a8;
        font-weight: 400;
        line-height: 1.6;
        max-width: 480px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }

    /* === TARJETAS GLASSMORPHISM === */
    .glass-card {
        background: rgba(255, 255, 255, 0.035);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(167, 139, 250, 0.14);
        border-radius: 20px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.25rem;
        position: relative;
        overflow: hidden;
    }

    /* === INPUT DE TEXTO === */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(167, 139, 250, 0.22) !important;
        border-radius: 12px !important;
        color: #e8e6f0 !important;
        padding: 0.7rem 1.1rem !important;
        font-size: 0.9rem !important;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(167, 139, 250, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.12), 0 0 20px rgba(124, 58, 237, 0.08) !important;
        background: rgba(255,255,255,0.07) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #4f4c6b !important; }

    /* === BOTONES === */
    .stButton > button, .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 50%, #5b21b6 100%) !important;
        color: #f3f0ff !important;
        border: 1px solid rgba(167,139,250,0.3) !important;
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.4px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.45), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }

    /* === MENSAJES === */
    .stAlert {
        border-radius: 12px !important;
        backdrop-filter: blur(8px) !important;
    }
    
    /* Footer */
    .site-footer {
        text-align: center;
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(167,139,250,0.08);
        color: #3d3b57;
        font-size: 0.78rem;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MANEJO DE ESTADO
# ==========================================
if 'mp3_data' not in st.session_state:
    st.session_state.mp3_data = None
    st.session_state.mp3_title = None

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="hero-wrap">
    <div class="vinyl-bg"></div>
    <div class="hero-badge">⚡ YT-DLP + FFmpeg</div>
    <div class="hero-title">Downloader MP3</div>
    <div class="hero-sub">
        Pega un enlace de YouTube para extraer la música en alta calidad.<br>
        El procesamiento se realiza de manera local.
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# LÓGICA DE DESCARGA YOUTUBE
# ==========================================
def descargar_audio_youtube(url):
    tmp_dir = tempfile.gettempdir()
    # Usamos %(title)s para obtener el nombre real del vídeo de YouTube
    ruta_salida = os.path.join(tmp_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'mp3', 
            'preferredquality': '192'
        }],
        'outtmpl': ruta_salida, 
        'quiet': True, 
        'no_warnings': True
    }
    
    with st.spinner("⬇️ Extrayendo y convirtiendo audio..."):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                titulo = info_dict.get('title', 'audio_yt')
                # yt_dlp cambia la extensión a .mp3 tras pasar por FFmpeg
                ruta_final = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'
                return ruta_final, titulo
        except Exception as e:
            st.error(f"❌ Error en la descarga. Asegúrate de tener FFmpeg instalado. Detalle: {e}")
            return None, None

# ==========================================
# INTERFAZ DE ENTRADA
# ==========================================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

youtube_url = st.text_input("Enlace del vídeo", placeholder="https://www.youtube.com/watch?v=...")

# Botón para iniciar el proceso
if st.button("🎵 Preparar MP3"):
    if youtube_url:
        st.session_state.mp3_data = None  # Resetear descargas anteriores
        ruta_tmp, titulo = descargar_audio_youtube(youtube_url)
        
        if ruta_tmp and os.path.exists(ruta_tmp):
            # Leemos el archivo a memoria para servirlo por el navegador local
            with open(ruta_tmp, "rb") as file:
                st.session_state.mp3_data = file.read()
                st.session_state.mp3_title = titulo
            
            # Limpiamos el archivo temporal del disco duro
            try:
                os.remove(ruta_tmp)
            except:
                pass
            
            st.success("✅ ¡Conversión completada con éxito!")
    else:
        st.warning("⚠️ Por favor, introduce un enlace de YouTube válido.")

# Si hay datos en memoria, mostramos el botón nativo de descarga
if st.session_state.mp3_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label=f"💾 Guardar: {st.session_state.mp3_title}.mp3",
        data=st.session_state.mp3_data,
        file_name=f"{st.session_state.mp3_title}.mp3",
        mime="audio/mpeg"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="site-footer">
    <span>Ejecutándose en entorno local · Desarrollado con Streamlit</span><br>
    YouTube to MP3 Downloader
</div>
""", unsafe_allow_html=True)