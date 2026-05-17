import os
import time
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
    "critica": "",
    "sarcastica": "",
}

COLORS_ANIMO = {
    "alegre": "#ffcc00",
    "curiosa": "#7a7aff",
    "tranquila": "#4affaa",
    "melancolica": "#aa7aff",
    "energica": "#ff6b35",
    "seria": "#8899aa",
    "juguetona": "#ff66b2",
    "critica": "#ff4444",
    "sarcastica": "#ff8800",
}

COLORS_EMOCION = {
    "alegria": "#ffcc00",
    "tristeza": "#7a5aff",
    "enojo": "#ff4444",
    "miedo": "#aa7aff",
    "confianza": "#4affaa",
    "interes": "#7a7aff",
}

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #12121a 100%); color: #e0e0e0; }
    .stChat { background-color: #121218; border-radius: 8px; }
    .stTextInput input { background-color: #1a1a24; color: #e0e0e0; border-color: #2a2a3a; }

    .chat-message { padding: 14px 18px; border-radius: 10px; margin: 6px 0; line-height: 1.7; font-size: 0.95em; }
    .user-message { background: linear-gradient(135deg, #1a1a2e, #16162a); border-left: 3px solid #4a4aff; }
    .assistant-message { background: linear-gradient(135deg, #0d1f0d, #0a1a0a); border-left: 3px solid #4aff4a; }
    .message-time { font-size: 0.7em; color: #555; margin-top: 4px; }

    .emo-badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 500; margin-top: 6px; }

    .metric-card { background: #121218; border: 1px solid #2a2a3a; border-radius: 10px; padding: 14px; margin: 4px 0; }
    .metric-card:hover { border-color: #4a4aff44; }

    .animo-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 24px; font-size: 0.9em; font-weight: 600; }
    .mood-track { height: 4px; border-radius: 2px; margin: 6px 0 14px 0; overflow: hidden; }

    .sidebar-header { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
    .sidebar-header .title { font-size: 1.4em; font-weight: 700; line-height: 1.2; }
    .sidebar-header .subtitle { font-size: 0.75em; color: #888; }

    .quick-btn { background: #1a1a24; border: 1px solid #2a2a3a; border-radius: 8px; padding: 8px 12px; color: #ccc; font-size: 0.85em; cursor: pointer; transition: all 0.2s; text-align: center; }
    .quick-btn:hover { background: #2a2a3a; border-color: #4a4aff66; }

    .mic-button { background: #2a2a3a; border: 1px solid #4a4aff; color: #e0e0e0; border-radius: 50%; width: 48px; height: 48px; font-size: 22px; cursor: pointer; transition: all 0.3s; }
    .mic-button:hover { background: #4a4aff; transform: scale(1.1); }
    .mic-button.listening { background: #ff4a4a; border-color: #ff4a4a; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,74,74,0.7); } 70% { box-shadow: 0 0 0 15px rgba(255,74,74,0); } 100% { box-shadow: 0 0 0 0 rgba(255,74,74,0); } }
    .voice-status { font-size: 0.8em; color: #888; margin-top: 4px; }

    div[data-testid="stAudio"] > audio { width: 100%; height: 44px; border-radius: 8px; }
    .st-emotion-cache-1y4p8pa { padding: 2rem 1rem; }
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
    emociones_data = brain.emociones.to_dict()
    pers = brain.personalidad.to_dict(emociones_data.get("animo", ""))
    animo = pers.get("animo_actual", "curiosa")
    color_animo = COLORS_ANIMO.get(animo, "#7a7aff")

    st.markdown(
        f"<div class='sidebar-header'>"
        f"<span style='font-size:2em;'></span>"
        f"<div><div class='title'>Novaria</div>"
        f"<div class='subtitle' style='color:{color_animo};'>{animo.capitalize()} · {emociones_data.get('dominante', '?')}</div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='animo-badge' style='background:{color_animo}22; border:1px solid {color_animo}44;'>"
        f"<span>{ICONS_ANIMO.get(animo, '')}</span>"
        f"<span style='color:{color_animo};'>{animo.capitalize()}</span>"
        f"<span style='font-size:0.7em; color:#888;'>({emociones_data.get('dominante', '')})</span></div>",
        unsafe_allow_html=True,
    )

    intensidad_dom = emociones_data.get("emociones", {}).get(emociones_data.get("dominante", ""), 0)
    st.markdown(
        f"<div class='mood-track' style='background:{color_animo}22;'>"
        f"<div class='mood-track' style='width:{int(intensidad_dom * 100)}%; background:{color_animo};'></div></div>",
        unsafe_allow_html=True,
    )

    interacciones = pers.get("total_interacciones", 0)
    nombre_user = pers.get("usuario", {}).get("nombre")
    if nombre_user:
        st.caption(f"  {interacciones} interacciones · {nombre_user}")
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
                btn.classList.remove('listening'); isListening = false;
            };
            recognition.onend = function() {
                btn.classList.remove('listening'); isListening = false;
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
            st.metric("Procesos", metricas.get("procesos_dialecticos", 0))
            st.metric("PDFs", est.get("pdfs_indexados", 0))
        with col2:
            st.metric("LLM Calls", metricas.get("llamadas_modelo", 0))
            st.metric("Errores", metricas.get("errores", 0))
            st.metric("Correcciones", est.get("correcciones_codigo", 0))
            st.metric("Plugins", est.get("plugins_creados", 0))
        st.metric("Tasa de Exito", f"{est.get('tasa_exito', 0)}%")
        s = metricas.get("sanacion", {})
        crit = metricas.get("critico", {})
        st.caption(f"Sanacion: {s.get('sanaciones_exitosas', 0)}/{s.get('intentos_sanacion', 0)}")
        st.caption(f"Critico: {crit.get('total_reescrituras', 0)}/{crit.get('total_revisiones', 0)} reescritas")

    with tab2:
        modelos = brain.orquestador.obtener_modelos_disponibles()
        if modelos:
            for m in modelos:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<b>{m['nombre']}</b><br>"
                    f"<span style='font-size:0.8em; color:#888;'>{m['proveedor']} · confianza: {m['confianza']}</span>"
                    f"</div>", unsafe_allow_html=True
                )
        else:
            st.info("No hay modelos configurados.")

    with tab3:
        est = brain.obtener_estado()
        emo = est.get("emociones", {})
        emos = emo.get("emociones", {})
        for e, v in sorted(emos.items(), key=lambda x: -x[1]):
            bar_w = max(int(v * 100), 4)
            c = COLORS_EMOCION.get(e, "#888")
            st.markdown(
                f"<div style='display:flex; align-items:center; gap:6px; font-size:0.8em; margin:3px 0;'>"
                f"<span style='width:70px;'>{e.capitalize()}</span>"
                f"<div style='flex:1; height:7px; background:#2a2a3a; border-radius:4px;'>"
                f"<div style='width:{bar_w}%; height:100%; background:{c}; border-radius:4px;'></div></div>"
                f"<span style='width:28px; text-align:right; font-size:0.85em;'>{v:.2f}</span></div>",
                unsafe_allow_html=True,
            )
        st.markdown(f"**RAM:** {est.get('ram_disponible_mb', 0):.0f} MB · **CPU:** {est.get('cpu_porcentaje', 0)}%")
        if est.get("throttle"):
            st.warning("Throttle activo")
        st.caption(f"Memoria: {est.get('tamano_memoria', 'N/A')} · Interacciones: {est.get('interacciones_memoria', 0)}")
        if st.button(" Detener", use_container_width=True):
            brain.detener()
            st.session_state.clear()
            st.rerun()

    st.divider()
    st.caption("UNEFA Santa Teresa")


# ── Area Principal ──

emociones_data = brain.emociones.to_dict()
emo_animo = emociones_data.get("animo", "")
pers = brain.personalidad.to_dict(emo_animo)
animo = pers.get("animo_actual", "curiosa")
icon_animo = ICONS_ANIMO.get(animo, "")
color_animo = COLORS_ANIMO.get(animo, "#7a7aff")

st.markdown(
    f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>"
    f"<span style='font-size:2em;'></span>"
    f"<div>"
    f"<span style='font-size:1.6em; font-weight:700;'>Novaria</span>"
    f"<span style='font-size:0.9em; margin-left:10px; color:{color_animo};'>{icon_animo} {animo.capitalize()}</span>"
    f"</div></div>",
    unsafe_allow_html=True,
)


if not brain.historial_chat:
    st.markdown(
        f"<div style='text-align:center; padding:60px 20px; color:#555;'>"
        f"<div style='font-size:3em; margin-bottom:16px;'></div>"
        f"<div style='font-size:1.1em; color:#888;'>No hay conversaciones guardadas en este dispositivo.</div>"
        f"<div style='font-size:0.9em; color:#555; margin-top:8px;'>Escribe algo para empezar</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

for i, mensaje in enumerate(brain.historial_chat):
    rol = mensaje.get("rol", "")
    contenido = mensaje.get("contenido", "")
    if rol == "usuario":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-message user-message">{contenido}</div>', unsafe_allow_html=True)
    elif rol == "asistente":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-message assistant-message">{contenido}</div>', unsafe_allow_html=True)
            if animo != "general":
                emo_dom = emociones_data.get("dominante", "")
                emo_int = emociones_data.get("emociones", {}).get(emo_dom, 0)
                c = COLORS_EMOCION.get(emo_dom, "#888")
                st.markdown(
                    f"<span class='emo-badge' style='background:{c}22; border:1px solid {c}44; color:{c};'>"
                    f"{emo_dom} {emo_int:.2f}</span>",
                    unsafe_allow_html=True,
                )


prompt = st.chat_input("Escribe tu mensaje aqui... (o usa el microfono en la barra lateral)")
if prompt:
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-message user-message">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner(""):
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
