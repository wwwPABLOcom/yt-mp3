import streamlit as st
import os
import tempfile
import yt_dlp
import shutil
import uuid

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y UX (SaaS Moderno)
# ==========================================
st.set_page_config(
    page_title="YT to MP3 Pro",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Fondo principal blanco/gris muy claro */
    .stApp { background-color: #F9FAFB; color: #111827; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 2rem 5rem 2rem; max-width: 750px; z-index: 1; }
    
    /* Títulos limpios */
    .hero-wrap { text-align: center; padding: 2rem 1rem 2rem 1rem; }
    .hero-title { font-size: 2.8rem; font-weight: 800; color: #111827; letter-spacing: -1px; margin-bottom: 0.5rem; }
    .hero-sub { color: #4B5563; max-width: 480px; margin: 0 auto; font-size: 1.1rem;}
    
    /* Tarjeta moderna con sombra suave */
    .glass-card { 
        background: #FFFFFF; 
        border: 1px solid #E5E7EB; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); 
        border-radius: 16px; 
        padding: 2rem; 
        margin-bottom: 1.5rem; 
    }
    
    /* Input de texto */
    .stTextInput > div > div > input { 
        background: #F3F4F6 !important; 
        border: 1px solid #D1D5DB !important; 
        border-radius: 8px !important; 
        color: #111827 !important; 
        padding: 0.75rem 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000 !important;
    }
    
    /* Botones estilo Apple/Vercel (Negro sólido y variantes) */
    .stButton > button { 
        width: 100%; 
        background: #F3F4F6 !important; 
        color: #111827 !important; 
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        padding: 0.4rem;
        transition: all 0.2s ease; 
    }
    .stButton > button:hover { background: #E5E7EB !important; }
    
    /* Botón principal (Submit / Descargar) */
    .primary-btn > div > .stButton > button, .stDownloadButton > button {
        background: #111827 !important; 
        color: #FFFFFF !important; 
        border: none !important;
        padding: 0.6rem;
    }
    .primary-btn > div > .stButton > button:hover, .stDownloadButton > button:hover {
        background: #374151 !important; 
        transform: translateY(-1px); 
    }
    
    /* Ajustes para la lista */
    .list-item { padding: 0.5rem 0; border-bottom: 1px solid #E5E7EB; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INICIALIZACIÓN DE ESTADO
# ==========================================
if 'playlist_data' not in st.session_state:
    st.session_state.playlist_data = None
if 'processed_audios' not in st.session_state:
    st.session_state.processed_audios = {}

# ==========================================
# 3. NÚCLEO DE LÓGICA (BACKEND)
# ==========================================

@st.cache_data(show_spinner=False, ttl=3600)
def extraer_metadatos(url):
    """Extrae la estructura de un video o playlist sin descargar nada."""
    ydl_opts_info = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if not info: 
            return {"error": "No se pudo extraer información del enlace."}
            
        resultados = []
        
        if 'entries' in info:
            for i, entry in enumerate(info['entries']):
                if entry and entry.get('id'):
                    resultados.append({
                        'index': i + 1,
                        'id': entry['id'],
                        'title': entry.get('title', f'Audio Desconocido {i+1}'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry['id']}"
                    })
        else:
            resultados.append({
                'index': 1,
                'id': info.get('id', uuid.uuid4().hex[:8]),
                'title': info.get('title', 'Audio_Desconocido'),
                'url': info.get('original_url', url)
            })
            
        return resultados
    except Exception as e:
        return {"error": str(e)}

def descargar_audio_individual(video_url):
    """Descarga y procesa un solo video con límite de hilos para CPU."""
    tmp_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    os.makedirs(tmp_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'}
        ],
        'postprocessor_args': [
            '-threads', '2'  # Límite estricto para no saturar los 4 cores
        ],
        'writethumbnail': True,
        'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        archivos = [f for f in os.listdir(tmp_dir) if f.endswith('.mp3')]
        if not archivos:
            raise Exception("Restricción de edad o copyright detectada.")
            
        filename = archivos[0]
        ruta = os.path.join(tmp_dir, filename)
        
        with open(ruta, "rb") as f:
            data = f.read()
            
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return data, filename, None
        
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return None, None, str(e)

# ==========================================
# 4. INTERFAZ (FRONTEND)
# ==========================================

st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">YT Audio Pro</div>
    <div class="hero-sub">Pega tu enlace para extraer la lista al instante y descargar individualmente lo que necesites, sin bloqueos.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

youtube_url = st.text_input("Enlace de YouTube:", placeholder="https://www.youtube.com/watch?v=... o &list=...")

st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
if st.button("Analizar Enlace"):
    if youtube_url:
        with st.spinner("Extraiendo estructura..."):
            datos = extraer_metadatos(youtube_url)
            
            if isinstance(datos, dict) and "error" in datos:
                st.error(f"❌ {datos['error']}")
            elif not datos:
                st.warning("⚠️ No se encontraron videos válidos.")
            else:
                st.session_state.playlist_data = datos
                st.session_state.processed_audios = {}
    else:
        st.warning("⚠️ Introduce un enlace válido.")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. RENDERIZADO DE RESULTADOS
# ==========================================

if st.session_state.playlist_data:
    st.markdown("### 📋 Resultados encontrados")
    st.markdown("<br>", unsafe_allow_html=True)
    
    for item in st.session_state.playlist_data:
        v_id = item['id']
        v_title = item['title']
        v_url = item['url']
        v_idx = item['index']
        
        col1, col2 = st.columns([3, 1], gap="medium", vertical_alignment="center")
        
        with col1:
            st.markdown(f"<div class='list-item'><strong>{v_idx}.</strong> {v_title}</div>", unsafe_allow_html=True)
            
        with col2:
            if v_id in st.session_state.processed_audios:
                estado = st.session_state.processed_audios[v_id]
                
                if estado.get("error"):
                    st.error("❌ Falló", icon="🚨")
                else:
                    st.download_button(
                        label="💾 Guardar",
                        data=estado["data"],
                        file_name=estado["filename"],
                        mime="audio/mpeg",
                        key=f"dl_{v_id}"
                    )
            else:
                if st.button("⬇️ Preparar", key=f"btn_{v_id}"):
                    with st.spinner("Descargando..."):
                        audio_data, filename, error = descargar_audio_individual(v_url)
                        
                        if error:
                            st.session_state.processed_audios[v_id] = {"error": error}
                            st.toast(f"Error procesando {v_title}", icon="⚠️")
                        else:
                            st.session_state.processed_audios[v_id] = {
                                "data": audio_data,
                                "filename": filename
                            }
                    st.rerun()
