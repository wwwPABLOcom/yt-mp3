import streamlit as st
import os
import re
import tempfile
import yt_dlp
import shutil
import uuid
import glob
import atexit

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y UX
# ==========================================
st.set_page_config(
    page_title="YT to MP3 Pro",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    
    .stApp { background-color: #0D0D0D; color: #F0EDE6; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 2rem 5rem 2rem; max-width: 780px; }
    
    .hero-wrap { text-align: center; padding: 3rem 1rem 2.5rem 1rem; }
    .hero-title { 
        font-family: 'Syne', sans-serif;
        font-size: 3.2rem; font-weight: 800; 
        color: #F0EDE6; letter-spacing: -2px; 
        margin-bottom: 0.6rem;
        background: linear-gradient(135deg, #F0EDE6 40%, #C8B8A2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub { color: #7A7570; max-width: 480px; margin: 0 auto; font-size: 1rem; font-weight: 300; line-height: 1.6; }
    
    .glass-card { 
        background: #1A1A1A; 
        border: 1px solid #2A2A2A; 
        border-radius: 16px; 
        padding: 1.75rem; 
        margin-bottom: 1.5rem; 
    }
    
    /* Input */
    .stTextInput > div > div > input { 
        background: #111111 !important; 
        border: 1px solid #333333 !important; 
        border-radius: 10px !important; 
        color: #F0EDE6 !important; 
        padding: 0.8rem 1rem;
        font-family: 'DM Sans', sans-serif;
    }
    .stTextInput > div > div > input::placeholder { color: #555 !important; }
    .stTextInput > div > div > input:focus {
        border-color: #C8B8A2 !important;
        box-shadow: 0 0 0 1px #C8B8A2 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div { 
        background: #111111 !important; 
        border: 1px solid #333333 !important; 
        border-radius: 10px !important;
        color: #F0EDE6 !important;
    }
    
    /* Botón secundario */
    .stButton > button { 
        width: 100%; 
        background: #222222 !important; 
        color: #F0EDE6 !important; 
        border: 1px solid #333333 !important;
        border-radius: 10px !important; 
        font-weight: 500 !important; 
        font-family: 'DM Sans', sans-serif !important;
        padding: 0.45rem;
        transition: all 0.2s ease; 
    }
    .stButton > button:hover { background: #2D2D2D !important; border-color: #555 !important; }
    
    /* Botón principal */
    .primary-btn .stButton > button, .stDownloadButton > button {
        background: #C8B8A2 !important; 
        color: #0D0D0D !important; 
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem;
    }
    .primary-btn .stButton > button:hover, .stDownloadButton > button:hover {
        background: #D4C4AE !important; 
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(200, 184, 162, 0.25);
    }

    /* Botón de reintento */
    .retry-btn .stButton > button {
        background: #2A1A1A !important;
        border-color: #5A2A2A !important;
        color: #E07070 !important;
        font-size: 0.82rem !important;
    }
    .retry-btn .stButton > button:hover { background: #3A2020 !important; }
    
    /* Lista items */
    .list-item { 
        padding: 0.6rem 0; 
        border-bottom: 1px solid #1F1F1F; 
        color: #D0CCC5;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .list-item strong { color: #7A7570; font-weight: 400; margin-right: 0.3rem; }
    
    /* Badge de calidad */
    .quality-badge {
        display: inline-block;
        background: #1F1F1F;
        border: 1px solid #2D2D2D;
        border-radius: 6px;
        padding: 0.1rem 0.5rem;
        font-size: 0.75rem;
        color: #7A7570;
        margin-left: 0.4rem;
    }

    /* Warning / error ajustados al tema oscuro */
    .stAlert { border-radius: 10px !important; }

    /* Sección de resultados */
    .results-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #F0EDE6;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    .results-meta { font-size: 0.85rem; color: #555; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTES
# ==========================================
MAX_PLAYLIST_ITEMS = 200
QUALITY_OPTIONS = {"128 kbps": "128", "192 kbps": "192", "320 kbps": "320"}
TMP_ROOT = os.path.join(tempfile.gettempdir(), "yt_mp3_pro")
os.makedirs(TMP_ROOT, exist_ok=True)

# Limpieza de directorios temporales huérfanos al iniciar y al salir
def _limpiar_tmp():
    for d in glob.glob(os.path.join(TMP_ROOT, "*")):
        shutil.rmtree(d, ignore_errors=True)

atexit.register(_limpiar_tmp)

# ==========================================
# 3. INICIALIZACIÓN DE ESTADO
# ==========================================
if 'playlist_data' not in st.session_state:
    st.session_state.playlist_data = None
if 'processed_audios' not in st.session_state:
    st.session_state.processed_audios = {}
if 'last_url' not in st.session_state:
    st.session_state.last_url = ""

# ==========================================
# 4. UTILIDADES
# ==========================================

def validar_url(url: str) -> bool:
    """Valida que sea una URL de YouTube mínimamente correcta."""
    url = url.strip()
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return bool(re.match(pattern, url))

def sanitizar_nombre(nombre: str) -> str:
    """Elimina caracteres ilegales en nombres de archivo."""
    # Elimina caracteres problemáticos en Windows/Linux
    nombre = re.sub(r'[\\/*?:"<>|]', '', nombre)
    # Normaliza espacios y puntos múltiples
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    nombre = nombre[:180]  # Límite razonable de longitud
    return nombre or "audio_descargado"

# ==========================================
# 5. NÚCLEO DE LÓGICA (BACKEND)
# ==========================================

@st.cache_data(show_spinner=False, ttl=3600)
def extraer_metadatos(url: str) -> tuple[list, str | None]:
    """
    Extrae la estructura de un video o playlist sin descargar nada.
    Devuelve (lista_de_items, mensaje_de_error_o_None).
    Separar el tipo de retorno del error evita isinstance checks frágiles.
    """
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'socket_timeout': 15,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return [], "No se pudo extraer información del enlace. Comprueba que es público y accesible."

        resultados = []

        if 'entries' in info:
            entries = list(info['entries'])[:MAX_PLAYLIST_ITEMS]
            for i, entry in enumerate(entries):
                if entry and entry.get('id'):
                    # Siempre construir la URL desde el ID para evitar URLs relativas rotas
                    resultados.append({
                        'index': i + 1,
                        'id': entry['id'],
                        'title': entry.get('title', f'Audio Desconocido {i + 1}'),
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                        'duration': entry.get('duration'),
                    })
        else:
            video_id = info.get('id', uuid.uuid4().hex[:8])
            resultados.append({
                'index': 1,
                'id': video_id,
                'title': info.get('title', 'Audio_Desconocido'),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'duration': info.get('duration'),
            })

        return resultados, None

    except Exception as e:
        return [], str(e)

def descargar_audio_individual(video_url: str, calidad: str = "192") -> tuple:
    """
    Descarga y convierte un video a MP3.
    Devuelve (bytes, nombre_archivo, error_o_None).
    """
    tmp_dir = os.path.join(TMP_ROOT, uuid.uuid4().hex)
    os.makedirs(tmp_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': calidad,
            },
            # Convierte la miniatura a JPEG antes de intentar incrustarla
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        # postprocessor_args correcto: dict con nombre del postprocesador como clave
        'postprocessor_args': {
            'ffmpegextractaudio': ['-threads', '2'],
        },
        'writethumbnail': True,
        'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        # Evita errores de certificado en algunos entornos
        'nocheckcertificate': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        archivos_mp3 = glob.glob(os.path.join(tmp_dir, '*.mp3'))
        if not archivos_mp3:
            raise FileNotFoundError(
                "No se generó el MP3. El vídeo puede tener restricción de edad, "
                "copyright o estar en una región bloqueada."
            )

        ruta = archivos_mp3[0]
        nombre_limpio = sanitizar_nombre(os.path.splitext(os.path.basename(ruta))[0])
        nombre_final = f"{nombre_limpio}.mp3"

        with open(ruta, "rb") as f:
            data = f.read()

        return data, nombre_final, None

    except Exception as e:
        return None, None, str(e)

    finally:
        # Limpieza garantizada tanto en éxito como en error
        shutil.rmtree(tmp_dir, ignore_errors=True)

# ==========================================
# 6. HELPERS DE UI
# ==========================================

def _formatear_duracion(segundos) -> str:
    """Convierte segundos a mm:ss o h:mm:ss."""
    if not segundos:
        return ""
    segundos = int(segundos)
    h, rem = divmod(segundos, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

# ==========================================
# 7. INTERFAZ (FRONTEND)
# ==========================================

st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">YT Audio Pro</div>
    <div class="hero-sub">
        Pega tu enlace, elige la calidad y descarga lo que necesitas — sin bloqueos, sin límites artificiales.
    </div>
</div>
""", unsafe_allow_html=True)

# — Tarjeta principal de entrada —
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

youtube_url = st.text_input(
    "Enlace de YouTube:",
    placeholder="https://www.youtube.com/watch?v=... o &list=...",
    value=st.session_state.last_url,
)

col_q, col_btn = st.columns([1, 2], gap="medium")

with col_q:
    calidad_label = st.selectbox(
        "Calidad MP3",
        options=list(QUALITY_OPTIONS.keys()),
        index=1,  # 192 kbps por defecto
    )
    calidad_valor = QUALITY_OPTIONS[calidad_label]

with col_btn:
    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)  # alinear verticalmente
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    analizar = st.button("Analizar enlace →")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# — Lógica del botón Analizar —
if analizar:
    url_limpia = youtube_url.strip()
    if not url_limpia:
        st.warning("⚠️ Introduce un enlace antes de continuar.")
    elif not validar_url(url_limpia):
        st.error("❌ El enlace no parece ser una URL válida de YouTube (youtube.com / youtu.be).")
    else:
        st.session_state.last_url = url_limpia
        # Resetear resultados si cambia la URL
        if url_limpia != st.session_state.get('_analyzed_url'):
            st.session_state.playlist_data = None
            st.session_state.processed_audios = {}
            st.session_state['_analyzed_url'] = url_limpia

        with st.spinner("Extrayendo información del enlace…"):
            items, error = extraer_metadatos(url_limpia)

        if error:
            st.error(f"❌ {error}")
        elif not items:
            st.warning("⚠️ No se encontraron vídeos válidos en ese enlace.")
        else:
            st.session_state.playlist_data = items
            st.session_state['_calidad'] = calidad_valor

# ==========================================
# 8. RENDERIZADO DE RESULTADOS
# ==========================================

if st.session_state.playlist_data:
    items = st.session_state.playlist_data
    calidad_activa = st.session_state.get('_calidad', calidad_valor)
    total = len(items)
    descargados = sum(
        1 for v in st.session_state.processed_audios.values() if not v.get("error")
    )

    st.markdown(
        f'<div class="results-header">📋 {total} elemento{"s" if total != 1 else ""} encontrado{"s" if total != 1 else ""}</div>'
        f'<div class="results-meta">{descargados} descargado{"s" if descargados != 1 else ""} · Calidad: {calidad_activa} kbps</div>',
        unsafe_allow_html=True,
    )

    if total == MAX_PLAYLIST_ITEMS:
        st.info(
            f"ℹ️ La playlist tiene más de {MAX_PLAYLIST_ITEMS} vídeos. "
            f"Se muestran los primeros {MAX_PLAYLIST_ITEMS}.",
            icon="📌",
        )

    for item in items:
        v_id = item['id']
        v_title = item['title']
        v_url = item['url']
        v_idx = item['index']
        v_dur = _formatear_duracion(item.get('duration'))

        col1, col2 = st.columns([3, 1], gap="medium", vertical_alignment="center")

        with col1:
            dur_html = f'<span class="quality-badge">{v_dur}</span>' if v_dur else ''
            st.markdown(
                f"<div class='list-item'><strong>{v_idx}.</strong> {v_title}{dur_html}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            estado = st.session_state.processed_audios.get(v_id)

            if estado is None:
                # Estado inicial: botón de preparar
                if st.button("⬇ Preparar", key=f"btn_{v_id}"):
                    with st.spinner(f'Descargando "{v_title[:40]}..."'):
                        audio_data, filename, error = descargar_audio_individual(
                            v_url, calidad=calidad_activa
                        )
                    if error:
                        st.session_state.processed_audios[v_id] = {"error": error}
                        st.toast(f"Error: {v_title[:30]}…", icon="⚠️")
                    else:
                        st.session_state.processed_audios[v_id] = {
                            "data": audio_data,
                            "filename": filename,
                        }
                    st.rerun()

            elif estado.get("error"):
                # Estado de error: muestra mensaje y botón de reintento
                st.markdown('<div class="retry-btn">', unsafe_allow_html=True)
                if st.button("↺ Reintentar", key=f"retry_{v_id}", help=estado["error"]):
                    del st.session_state.processed_audios[v_id]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                # Estado de éxito: botón de descarga
                st.download_button(
                    label="💾 Guardar",
                    data=estado["data"],
                    file_name=estado["filename"],
                    mime="audio/mpeg",
                    key=f"dl_{v_id}",
                )
