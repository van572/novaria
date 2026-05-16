import os
import time
import asyncio
import streamlit as st
import streamlit.components.v1 as components
from core.cerebro import CerebroNovaria
from herramientas.voz import GeneradorVoz


st.set_page_config(
    page_title="Novaria",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

ICONS_ANIMO = {
    "alegre": "",
    "curiosa": "",
    "tranquila": "",
    "melancolica": "",
    "energica": "",
    "seria": "",
    "juguetona": "",
}

COLORS_ANIMO = {
    "alegre": "#ffcc00",
    "curiosa": "#7a7aff",
    "tranquila": "#4affaa",
    "melancolica": "#aa7aff",
    "energica": "#ff6b35",
    "seria": "#8899aa",
    "juguetona": "#ff66b2",
}

st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; color: #e0e0e0; }
    .stChat { background-color: #121218; border-radius: 8px; }
    .stTextInput input { background-color: #1a1a24; color: #e0e0e0; border-color: #2a2a3a; }
    .chat-message { padding: 12px 16px; border-radius: 8px; margin: 4px 0; line-height: 1.6; }
    .user-message { background-color: #1a1a2e; border-left: 3px solid #4a4aff; }
    .assistant-message { background-color: #0d1f0d; border-left: 3px solid #4aff4a; }
    .metric-card { background-color: #121218; border: 1px solid #2a2a3a; border-radius: 8px; padding: 16px; }

    .mic-button { background: #2a2a3a; border: 1px solid #4a4aff; color: #e0e0e0; border-radius: 50%; width: 48px; height: 48px; font-size: 22px; cursor: pointer; transition: all 0.3s; }
    .mic-button:hover { background: #4a4aff; transform: scale(1.1); }
    .mic-button.listening { background: #ff4a4a; border-color: #ff4a4a; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,74,74,0.7); } 70% { box-shadow: 0 0 0 15px rgba(255,74,74,0); } 100% { box-shadow: 0 0 0 0 rgba(255,74,74,0); } }
    .voice-status { font-size: 0.8em; color: #888; margin-top: 4px; }

    .animo-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 500; }
    .mood-bar { height: 3px; border-radius: 2px; margin: 4px 0 12px 0; transition: all 0.5s; }

    div[data-testid="stAudio"] > audio { width: 100%; height: 44px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


if "brain" not in st.session_state:
    st.session_state.brain = CerebroNovaria()
    st.session_state.voz = GeneradorVoz()
    st.session_state.voz_activada = False
    st.session_state.ultimo_audio = ""
    st.session_state.ultimo_hash_audio = ""

brain = st.session_state.brain


# ── Sidebar ──

with st.sidebar:
    pers = brain.personalidad.to_dict()
    animo = pers.get("animo_actual", "curiosa")
    icon_animo = ICONS_ANIMO.get(animo, "")
    color_animo = COLORS_ANIMO.get(animo, "#7a7aff")

    st.markdown(
        f"<div style='display:flex; align-items:center; gap:10px; margin-bottom:4px;'>"
        f"<span style='font-size:28px;'></span>"
        f"<div><span style='font-size:22px; font-weight:700;'>Novaria</span><br>"
        f"<span style='font-size:13px; color:#888;'>tu asistente con pensamiento profundo</span></div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='animo-badge' style='background:{color_animo}22; border:1px solid {color_animo}44;'>"
        f"<span>{icon_animo}</span><span style='color:{color_animo};'>{animo.capitalize()}</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='mood-bar' style='width:100%; background:{color_animo}44;'>"
        f"<div class='mood-bar' style='width:40%; background:{color_animo};'></div></div>",
        unsafe_allow_html=True,
    )

    interacciones = pers.get("total_interacciones", 0)
    nombre_user = pers.get("usuario", {}).get("nombre")
    if nombre_user:
        st.caption(f"  {interacciones} interacciones | Hablando con {nombre_user}")
    else:
        st.caption(f"  {interacciones} interacciones")

    st.divider()

    # ── Control de Voz ──
    st.markdown("###  Voz")
    voz_on = st.toggle("Activar voz", value=st.session_state.voz_activada, key="toggle_voz")
    st.session_state.voz_activada = voz_on

    if voz_on:
        voces = st.session_state.voz.voces_disponibles()
        voz_actual = st.session_state.voz.voz_seleccionada
        idx = next((i for i, v in enumerate(voces) if voz_actual in v), 0)
        voz_elegida = st.selectbox("Voz", voces, index=idx, label_visibility="collapsed")
        st.session_state.voz.voz_seleccionada = voz_elegida.split(" - ")[0]

        st.caption("Presiona el microfono para hablar")

        mic_html = """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0;">
            <button id="mic-btn" class="mic-button" onclick="toggleMic()">🎤</button>
            <div id="mic-status" class="voice-status">Presiona para hablar</div>
        </div>
        <script>
        let recognition = null; let isListening = false;
        const btn = document.getElementById('mic-btn');
        const status = document.getElementById('mic-status');
        function initRecognition() {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) { status.textContent = 'No soportado'; return; }
            recognition = new SR();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.onresult = function(e) {
                const text = e.results[0][0].transcript;
                status.textContent = ' ' + text;
                btn.classList.remove('listening');
                isListening = false;
                const input = document.querySelector('[data-testid="stChatInput"] textarea');
                if (input) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(input, text);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            recognition.onerror = function(e) {
                status.textContent = 'Error: ' + e.error;
                btn.classList.remove('listening');
                isListening = false;
            };
            recognition.onend = function() {
                btn.classList.remove('listening');
                isListening = false;
                if (status.textContent === 'Escuchando...') status.textContent = 'Presiona para hablar';
            };
        }
        function toggleMic() {
            if (isListening) { if (recognition) recognition.stop(); btn.classList.remove('listening'); isListening = false; status.textContent = 'Presiona para hablar'; return; }
            if (!recognition) initRecognition();
            if (!recognition) return;
            try { recognition.start(); isListening = true; btn.classList.add('listening'); status.textContent = 'Escuchando...'; }
            catch(e) { status.textContent = 'Error: ' + e.message; }
        }
        if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
            status.textContent = 'Navegador no compatible con voz';
        }
        </script>
        """
        components.html(mic_html, height=80)
    st.divider()

    # ── Tabs de métricas ──
    tab1, tab2, tab3 = st.tabs(["", "", ""])

    with tab1:
        metricas = brain.obtener_metricas()
        est = brain.obtener_estado()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Consultas", metricas.get("total_consultas", 0))
            st.metric("Comandos", metricas.get("comandos_directos", 0))
            st.metric("Procesos Profundos", metricas.get("procesos_dialecticos", 0))
            st.metric("PDFs Indexados", est.get("pdfs_indexados", 0))
        with col2:
            st.metric("LLM Calls", metricas.get("llamadas_modelo", 0))
            st.metric("Errores", metricas.get("errores", 0))
            st.metric("Auto-Correcciones", est.get("correcciones_codigo", 0))
            st.metric("Plugins Creados", est.get("plugins_creados", 0))
        st.metric("Tasa de Exito", f"{est.get('tasa_exito', 0)}%")
        st.caption(f"Tema actual: {est.get('tema_actual', 'N/A')}")
        s = metricas.get("sanacion", {})
        st.caption(f"Sanacion: {s.get('sanaciones_exitosas', 0)}/{s.get('intentos_sanacion', 0)} exitosos")

    with tab2:
        modelos = brain.orquestador.obtener_modelos_disponibles()
        if modelos:
            roles = {
                "Analitico": next((m["nombre"] for m in modelos if m["nombre"] in ["llama-3.1-8b-instant", "google/gemma-2-9b-it"]), "N/A"),
                "Creativo": next((m["nombre"] for m in modelos if m["nombre"] in ["mixtral-8x7b-32768", "mistralai/mixtral-8x22b-instruct"]), "N/A"),
                "Integrador": next((m["nombre"] for m in modelos if m["nombre"] in ["mistralai/mixtral-8x22b-instruct", "llama-3.1-8b-instant"]), "N/A"),
            }
            for rol, modelo in roles.items():
                with st.container():
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f"**{rol}**")
                    st.caption(f"{modelo}")
                    st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
            for m in modelos:
                with st.container():
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f"**{m['nombre']}**")
                    st.caption(f"{m['proveedor']} | confianza: {m['confianza']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No hay modelos configurados. Verifica tus claves API.")

    with tab3:
        est = brain.obtener_estado()
        ram = est.get("ram_disponible_mb", 0)
        cpu = est.get("cpu_porcentaje", 0)
        st.markdown(f"**Salud:** {est.get('salud', 'N/A')}")
        st.markdown(f"**Memoria:** {est.get('tamano_memoria', 'N/A')}")
        st.markdown(f"**RAM libre:** {ram:.0f} MB")
        st.markdown(f"**CPU:** {cpu}%")
        if est.get("throttle"):
            st.warning("Throttle activo - recursos bajos")
        st.markdown(f"**Interacciones:** {est.get('interacciones_memoria', 0)}")
        st.markdown(f"**Plugins:** {est.get('plugins_cargados', 0)}")
        st.markdown(f"**Procesos Profundos:** {est.get('procesos_dialecticos', 0)}")
        st.markdown(f"**PDFs UNEFA:** {est.get('pdfs_indexados', 0)}")
        st.markdown(f"**Tema actual:** {est.get('tema_actual', 'N/A')}")
        if st.button(" Detener Sistema", use_container_width=True):
            brain.detener()
            st.session_state.clear()
            st.rerun()

    st.divider()
    st.caption("UNEFA Santa Teresa - Ingenieria de Sistemas")


# ── Area Principal ──

pers = brain.personalidad.to_dict()
animo = pers.get("animo_actual", "curiosa")
icon_animo = ICONS_ANIMO.get(animo, "")
st.markdown(f"##  Novaria  {icon_animo}")


for mensaje in brain.historial_chat:
    rol = mensaje.get("rol", "")
    contenido = mensaje.get("contenido", "")
    if rol == "usuario":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-message user-message">{contenido}</div>', unsafe_allow_html=True)
    elif rol == "asistente":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-message assistant-message">{contenido}</div>', unsafe_allow_html=True)
            if animo != "general":
                st.caption(f"{icon_animo} {animo.capitalize()}")


prompt = st.chat_input("Escribe tu mensaje aqui... (o usa el microfono en la barra lateral)")
if prompt:
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-message user-message">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Pensando..."):
        respuesta = brain.procesar_mensaje(prompt)

    with st.chat_message("assistant"):
        st.markdown(f'<div class="chat-message assistant-message">{respuesta}</div>', unsafe_allow_html=True)

    if st.session_state.voz_activada and respuesta:
        voz = st.session_state.voz
        audio_path = voz.texto_a_voz(respuesta)
        if audio_path:
            st.session_state.ultimo_audio = audio_path
            st.session_state.ultimo_hash_audio = str(hash(respuesta[:100]))
            voz.limpiar_audios_viejos()

    st.rerun()


if st.session_state.voz_activada and st.session_state.ultimo_audio:
    if os.path.exists(st.session_state.ultimo_audio):
        with open(st.session_state.ultimo_audio, "rb") as f:
            audio_bytes = f.read()
        size_kb = len(audio_bytes) / 1024
        if size_kb > 5:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
