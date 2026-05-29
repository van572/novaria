import os
import time
import streamlit as st
import streamlit.components.v1 as components
from core.cerebro import CerebroNovaria
from herramientas.voz import GeneradorVoz

st.set_page_config(
    page_title="Novaria — Supernova",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta Supernova (violetas, púrpuras, magenta, dorado) ──
BG_DARK = "#0a0012"
BG_CARD = "#12081e"
BG_INPUT = "#1a0f2e"
BORDER = "#3a1f6e"
BORDER_GLOW = "#7b2ff7"
TEXT = "#e8d8f8"
TEXT_MUTED = "#8870a8"
ACCENT = "#9b59e6"
ACCENT2 = "#e040c0"
ACCENT3 = "#ff6fd8"
GOLD = "#f0c060"
CYAN = "#60d0ff"
GRADIENT_MAIN = "linear-gradient(135deg, #0a0012 0%, #1a0f2e 30%, #0d0520 70%, #120020 100%)"
GRADIENT_MSG_USER = "linear-gradient(135deg, #1a0f2e, #281050)"
GRADIENT_MSG_NOVA = "linear-gradient(135deg, #12081e, #1a0f30)"

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
    "alegre": GOLD,
    "curiosa": ACCENT,
    "tranquila": CYAN,
    "melancolica": "#a080e0",
    "energica": "#ff4488",
    "seria": "#8890b0",
    "juguetona": ACCENT2,
    "critica": "#ff4466",
    "sarcastica": "#ff8800",
}

COLORS_EMOCION = {
    "alegria": GOLD,
    "tristeza": "#8855cc",
    "enojo": "#ff3355",
    "miedo": "#6633aa",
    "confianza": "#55ddff",
    "interes": ACCENT,
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {GRADIENT_MAIN}; color: {TEXT}; }}

    /* Stars background */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1px 1px at 30% 60%, rgba(255,255,255,0.4), transparent),
            radial-gradient(1.5px 1.5px at 50% 10%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 70% 80%, rgba(255,255,255,0.3), transparent),
            radial-gradient(1px 1px at 90% 30%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1.2px 1.2px at 15% 85%, rgba(255,255,255,0.4), transparent),
            radial-gradient(1px 1px at 60% 40%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1px 1px at 80% 15%, rgba(255,255,255,0.3), transparent),
            radial-gradient(1.3px 1.3px at 40% 90%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1px 1px at 25% 45%, rgba(255,255,255,0.4), transparent);
        pointer-events: none;
        z-index: 0;
    }}

    /* Nebula glow top-right */
    .stApp::after {{
        content: '';
        position: fixed;
        top: -200px; right: -200px;
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(155,89,230,0.08) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }}

    .stChat {{ background: transparent; }}
    .stTextInput input, .stTextArea textarea {{
        background: {BG_INPUT} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
        font-size: 0.95em !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 20px rgba(155,89,230,0.15) !important;
    }}

    /* Chat input container */
    div[data-testid="stChatInput"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 4px 8px;
        backdrop-filter: blur(8px);
        position: relative;
    }}
    div[data-testid="stChatInput"]:focus-within {{
        border-color: {ACCENT};
        box-shadow: 0 0 30px rgba(155,89,230,0.1);
    }}

    /* Messages */
    .chat-msg {{
        padding: 14px 20px;
        border-radius: 16px;
        margin: 8px 0;
        line-height: 1.7;
        font-size: 0.93em;
        position: relative;
        z-index: 1;
    }}
    .user-msg {{
        background: {GRADIENT_MSG_USER};
        border: 1px solid {BORDER};
        border-left: 3px solid {ACCENT};
    }}
    .nova-msg {{
        background: {GRADIENT_MSG_NOVA};
        border: 1px solid #2a1050;
        border-left: 3px solid {ACCENT2};
        box-shadow: 0 0 20px rgba(224,64,192,0.06);
    }}
    .msg-time {{ font-size: 0.65em; color: {TEXT_MUTED}; margin-top: 6px; opacity: 0.6; }}
    .title-row {{
        display: flex; align-items: center; gap: 16px;
        padding: 16px 0 8px 0;
        position: relative; z-index: 1;
    }}
    .nova-title {{
        font-size: 1.8em; font-weight: 800;
        background: linear-gradient(135deg, {ACCENT2}, {ACCENT}, {GOLD});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }}
    .nova-subtitle {{
        font-size: 0.75em; color: {TEXT_MUTED}; margin-top: -4px;
    }}

    /* Sidebar */
    .css-1d391kg, .st-emotion-cache-1d391kg {{
        background: {BG_DARK};
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] {{
        background: {BG_DARK};
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] .st-emotion-cache-1ny9fil {{
        background: {BG_DARK};
    }}

    .sb-header {{
        display: flex; align-items: center; gap: 14px;
        padding: 16px 0 8px 0;
    }}
    .sb-logo {{
        width: 42px; height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4em;
        box-shadow: 0 0 24px rgba(155,89,230,0.25);
    }}
    .sb-title {{ font-size: 1.3em; font-weight: 700; }}
    .sb-sub {{ font-size: 0.7em; color: {TEXT_MUTED}; }}

    .animo-badge {{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 5px 14px; border-radius: 20px;
        font-size: 0.82em; font-weight: 600;
        backdrop-filter: blur(4px);
    }}
    .mood-track {{
        height: 4px; border-radius: 3px; margin: 6px 0 12px 0; overflow: hidden;
    }}

    /* Glow cards */
    .glow-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 12px 14px;
        margin: 4px 0;
        transition: border-color 0.2s;
    }}
    .glow-card:hover {{ border-color: {ACCENT}44; }}

    /* Emo badge */
    .emo-badge {{
        display: inline-flex; align-items: center; gap: 5px;
        padding: 2px 10px; border-radius: 10px;
        font-size: 0.7em; font-weight: 500;
    }}

    /* Quick buttons row */
    .quick-btn {{
        background: {BG_INPUT};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 7px 10px;
        color: {TEXT};
        font-size: 0.78em;
        cursor: pointer;
        transition: all 0.25s;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .quick-btn:hover {{
        background: #281050;
        border-color: {ACCENT}88;
        box-shadow: 0 0 16px rgba(155,89,230,0.12);
    }}

    /* Mic button */
    .mic-btn {{
        background: {BG_INPUT};
        border: 1px solid {BORDER};
        color: {TEXT};
        border-radius: 50%; width: 46px; height: 46px;
        font-size: 20px; cursor: pointer;
        transition: all 0.3s;
        display: flex; align-items: center; justify-content: center;
    }}
    .mic-btn:hover {{ background: #281050; border-color: {ACCENT}; transform: scale(1.08); }}
    .mic-btn.listening {{
        background: {ACCENT2};
        border-color: {ACCENT2};
        box-shadow: 0 0 30px rgba(224,64,192,0.4);
        animation: pulse-mic 1.2s infinite;
    }}
    @keyframes pulse-mic {{
        0% {{ box-shadow: 0 0 0 0 rgba(224,64,192,0.5); }}
        70% {{ box-shadow: 0 0 0 18px rgba(224,64,192,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(224,64,192,0); }}
    }}

    /* Empty state */
    .empty-state {{
        text-align: center; padding: 80px 20px;
        position: relative; z-index: 1;
    }}
    .empty-icon {{
        font-size: 4em; margin-bottom: 12px;
        filter: drop-shadow(0 0 40px rgba(155,89,230,0.3));
    }}

    /* Divider */
    hr {{
        border: none; height: 1px;
        background: linear-gradient(90deg, transparent, {BORDER}, {ACCENT}44, {BORDER}, transparent);
    }}

    .status-dot {{
        display: inline-block; width: 7px; height: 7px;
        border-radius: 50%; margin-right: 6px;
        animation: blink 2s infinite;
    }}
    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}

    .nova-greeting {{
        font-size: 1.1em;
        background: linear-gradient(135deg, {ACCENT2}88, {ACCENT}88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 300;
    }}

    div[data-testid="stAudio"] > audio {{ width: 100%; height: 44px; border-radius: 10px; }}
    .st-emotion-cache-1y4p8pa {{ padding: 1.5rem 1rem; }}
    .st-emotion-cache-1wrcr25 {{ gap: 0px; }}
    button[data-testid="baseButton-secondary"] {{ color: {TEXT_MUTED}; }}

    /* Make chat input inner container a flex row */
    div[data-testid="stChatInput"] > div {{
        display: flex;
        align-items: center;
        gap: 4px;
    }}
    div[data-testid="stChatInput"] textarea {{
        flex: 1;
    }}

    /* Chat mic button inline */
    .chat-mic-btn {{
        background: transparent;
        border: none;
        color: {TEXT_MUTED};
        font-size: 18px;
        cursor: pointer;
        padding: 0 8px;
        transition: all 0.25s;
        line-height: 1;
    }}
    .chat-mic-btn:hover {{
        color: {ACCENT2};
        transform: scale(1.15);
    }}
    .chat-mic-btn.listening {{
        color: {ACCENT2};
        animation: pulse-mic-btn 1s infinite;
    }}
    @keyframes pulse-mic-btn {{
        0%, 100% {{ text-shadow: 0 0 4px {ACCENT2}88; }}
        50% {{ text-shadow: 0 0 16px {ACCENT2}cc; }}
    }}
    .chat-mic-status {{
        position: absolute;
        bottom: -20px;
        right: 50px;
        font-size: 0.7em;
        color: {ACCENT2}88;
        white-space: nowrap;
    }}
</style>
""", unsafe_allow_html=True)


if "brain" not in st.session_state:
    st.session_state.brain = CerebroNovaria()
    st.session_state.voz = GeneradorVoz()
    st.session_state.voz_activada = False
    st.session_state.ultimo_audio = ""
    st.session_state.ultimo_hash_audio = ""
    st.session_state.preguntas_rapidas = [
        "Que es la conciencia?",
        "Tiene sentido la vida?",
        "Como funciona tu mente?",
        "Que opinas de la inteligencia artificial?",
    ]

brain = st.session_state.brain

# ── Sidebar ──
with st.sidebar:
    emociones_data = brain.emociones.to_dict()
    pers = brain.personalidad.to_dict(emociones_data.get("animo", ""))
    animo = pers.get("animo_actual", "curiosa")
    color_animo = COLORS_ANIMO.get(animo, ACCENT)

    st.markdown(
        f"""<div class="sb-header">
            <div class="sb-logo"></div>
            <div>
                <div class="sb-title">Novaria</div>
                <div class="sb-sub" style="color:{color_animo};">{animo.capitalize()} · {emociones_data.get('dominante', '?')}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="animo-badge" style="background:{color_animo}15; border:1px solid {color_animo}33;">
            <span>{ICONS_ANIMO.get(animo, '')}</span>
            <span style="color:{color_animo};">{animo.capitalize()}</span>
            <span style="font-size:0.7em; color:{TEXT_MUTED};">({emociones_data.get('dominante', '')})</span>
        </div>""",
        unsafe_allow_html=True,
    )

    intensidad_dom = emociones_data.get("emociones", {}).get(emociones_data.get("dominante", ""), 0)
    st.markdown(
        f"""<div class="mood-track" style="background:{color_animo}18;">
            <div style="width:{int(intensidad_dom * 100)}%; height:100%; background:{color_animo}; border-radius:3px;
                        box-shadow:0 0 12px {color_animo}44;"></div>
        </div>""",
        unsafe_allow_html=True,
    )

    interacciones = pers.get("total_interacciones", 0)
    nombre_user = pers.get("usuario", {}).get("nombre")
    info_user = f"  {interacciones} interacciones"
    if nombre_user:
        info_user += f" · {nombre_user}"
    st.caption(info_user)

    # Pensamiento latente
    pensamiento = brain.obtener_estado().get("pensamiento_latente", "")
    if pensamiento:
        st.markdown(
            f"""<div style="margin:10px 0; padding:8px 12px; background:{ACCENT2}08; border-left:2px solid {ACCENT2}44;
                        border-radius:8px; font-size:0.78em; color:#c8a0d8; line-height:1.4;">
                <span style="font-size:0.7em; color:{ACCENT2}88; display:block; margin-bottom:4px;"> Pensamiento latente</span>
                {pensamiento[:200]}{'...' if len(pensamiento) > 200 else ''}
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Voz toggle (solo el toggle, el botón va en el panel principal) ──
    voz_on = st.toggle("🎤 Voz", value=st.session_state.voz_activada, key="toggle_voz")
    st.session_state.voz_activada = voz_on

    if voz_on:
        voces = st.session_state.voz.voces_disponibles()
        voz_actual = st.session_state.voz.voz_seleccionada
        idx = next((i for i, v in enumerate(voces) if voz_actual in v), 0)
        voz_elegida = st.selectbox("Voz", voces, index=idx, label_visibility="collapsed")
        st.session_state.voz.voz_seleccionada = voz_elegida.split(" - ")[0]

    st.divider()

    # ── Tabs de métricas ──
    tab1, tab2, tab3 = st.tabs([" Métricas", " Modelos", " Emociones"])

    with tab1:
        metricas = brain.obtener_metricas()
        est = brain.obtener_estado()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Consultas", metricas.get("total_consultas", 0))
            st.metric("Comandos", metricas.get("comandos_directos", 0))
            st.metric("Procesos Dialecticos", metricas.get("procesos_dialecticos", 0))
        with col2:
            st.metric("LLM Calls", metricas.get("llamadas_modelo", 0))
            st.metric("Errores", metricas.get("errores", 0))
            st.metric("Correcciones", est.get("correcciones_codigo", 0))
        st.metric("Tasa de Exito", f"{est.get('tasa_exito', 0)}%")
        s = metricas.get("sanacion", {})
        st.caption(f"Sanacion: {s.get('sanaciones_exitosas', 0)}/{s.get('intentos_sanacion', 0)}")

    with tab2:
        modelos = brain.orquestador.obtener_modelos_disponibles()
        if modelos:
            for m in modelos:
                st.markdown(
                    f"""<div class="glow-card">
                        <b>{m['nombre']}</b><br>
                        <span style="font-size:0.75em; color:{TEXT_MUTED};">{m['proveedor']} · confianza: {m['confianza']}</span>
                    </div>""", unsafe_allow_html=True
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
                f"""<div style="display:flex; align-items:center; gap:6px; font-size:0.75em; margin:2px 0;">
                    <span style="width:65px;">{e.capitalize()}</span>
                    <div style="flex:1; height:6px; background:rgba(255,255,255,0.05); border-radius:3px;">
                        <div style="width:{bar_w}%; height:100%; background:{c}; border-radius:3px;
                                    box-shadow:0 0 8px {c}44;"></div></div>
                    <span style="width:26px; text-align:right; font-size:0.8em; color:{TEXT_MUTED};">{v:.2f}</span>
                </div>""", unsafe_allow_html=True,
            )
        st.markdown(f"<span style='font-size:0.75em; color:{TEXT_MUTED};'>**RAM:** {est.get('ram_disponible_mb', 0):.0f} MB · **CPU:** {est.get('cpu_porcentaje', 0)}%</span>", unsafe_allow_html=True)
        if est.get("throttle"):
            st.warning("Throttle activo")
        st.caption(f"Memoria: {est.get('tamano_memoria', 'N/A')} · Interacciones: {est.get('interacciones_memoria', 0)}")
        dom = emociones_data.get("dominante", "")
        if dom:
            from core.cerebro import calcular_hiperparametros_dinamicos
            intensidad = emociones_data.get("emociones", {}).get(dom, 0)
            fatiga = emociones_data.get("fatiga_cognitiva", 0)
            t1, t2 = calcular_hiperparametros_dinamicos(dom, intensidad, fatiga)
            fatiga_bar = f"· Fatiga: {fatiga:.2f}" if fatiga > 0.05 else ""
            st.caption(f"S1 {t1:.2f} · S2 {t2:.2f} ({dom} {intensidad:.2f}){fatiga_bar}")
        if st.button(" Detener", use_container_width=True):
            brain.detener()
            st.session_state.clear()
            st.rerun()

    st.divider()
    st.caption("UNEFA Santa Teresa · Novaria Supernova")


# ── Inyectar micrófono en el chat input ──
st.markdown("""<div id="mic-host"></div>""", unsafe_allow_html=True)
components.html(f"""
<div id="mic-script-container"></div>
<script>
(function() {{
    function inyectarMic() {{
        if (document.getElementById('chat-mic-btn')) return;
        const chatInput = document.querySelector('[data-testid="stChatInput"]');
        if (!chatInput) {{ setTimeout(inyectarMic, 300); return; }}
        const sendBtn = chatInput.querySelector('[data-testid="stChatInput-send-button"]');
        if (!sendBtn) {{ setTimeout(inyectarMic, 300); return; }}
        const micBtn = document.createElement('button');
        micBtn.id = 'chat-mic-btn';
        micBtn.innerHTML = '🎤';
        micBtn.className = 'chat-mic-btn';
        micBtn.type = 'button';
        micBtn.title = 'Presiona para hablar';
        sendBtn.parentNode.insertBefore(micBtn, sendBtn);
        const status = document.createElement('div');
        status.id = 'chat-mic-status';
        status.className = 'chat-mic-status';
        chatInput.appendChild(status);

        let recognition = null;
        let isListening = false;

        micBtn.onclick = function() {{
            if (isListening) {{
                if (recognition) recognition.stop();
                micBtn.classList.remove('listening');
                isListening = false;
                status.textContent = '';
                return;
            }}
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) {{ status.textContent = 'No soportado'; return; }}
            if (!recognition) {{
                recognition = new SR();
                recognition.lang = 'es-ES';
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.onresult = function(e) {{
                    const text = e.results[0][0].transcript;
                    status.textContent = '✅ ' + text;
                    micBtn.classList.remove('listening');
                    isListening = false;
                    const textarea = chatInput.querySelector('textarea');
                    if (textarea) {{
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeSetter.call(textarea, text);
                        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        setTimeout(function() {{ textarea.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }})); }}, 100);
                    }}
                }};
                recognition.onerror = function(e) {{
                    status.textContent = 'Error: ' + e.error;
                    micBtn.classList.remove('listening');
                    isListening = false;
                }};
                recognition.onend = function() {{
                    micBtn.classList.remove('listening');
                    isListening = false;
                    if (status.textContent === '🎤 Escuchando...') status.textContent = '';
                }};
            }}
            try {{
                recognition.start();
                isListening = true;
                micBtn.classList.add('listening');
                status.textContent = '🎤 Escuchando...';
            }} catch(e) {{
                status.textContent = 'Error: ' + e.message;
            }}
        }};
    }}
    inyectarMic();
    // Re-inject on Streamlit re-render
    const observer = new MutationObserver(function() {{ inyectarMic(); }});
    observer.observe(document.body, {{ childList: true, subtree: true }});
}})();
</script>
""", height=0)


# ── Area Principal ──
emociones_data = brain.emociones.to_dict()
emo_animo = emociones_data.get("animo", "")
pers = brain.personalidad.to_dict(emo_animo)
animo = pers.get("animo_actual", "curiosa")
icon_animo = ICONS_ANIMO.get(animo, "")
color_animo = COLORS_ANIMO.get(animo, ACCENT)

# Header con glow
st.markdown(
    f"""<div class="title-row">
        <div class="nova-title">Novaria</div>
        <div style="display:flex; align-items:center; gap:6px;">
            <span class="status-dot" style="background:{ACCENT2}; box-shadow:0 0 8px {ACCENT2};"></span>
            <span style="font-size:0.78em; color:{TEXT_MUTED};">Activo</span>
        </div>
        <div style="flex:1;"></div>
        <span style="font-size:0.82em; color:{color_animo};">{icon_animo} {animo.capitalize()}</span>
    </div>
    <div class="nova-subtitle">Sistema de conciencia artificial · Pipeline dialectico</div>""",
    unsafe_allow_html=True,
)

# Preguntas rápidas (solo si no hay historial)
if not brain.historial_chat:
    st.markdown(
        f"""<div class="empty-state">
            <div class="empty-icon"></div>
            <div class="nova-greeting">Bienvenido a Novaria</div>
            <div style="font-size:0.9em; color:{TEXT_MUTED}; margin-top:6px;">Sistema de conciencia artificial con pipeline dialectico</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Quick questions row
    qs = st.session_state.preguntas_rapidas
    cols = st.columns(len(qs))
    for i, q in enumerate(qs):
        with cols[i]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                prompt = q
                with st.chat_message("user"):
                    st.markdown(f'<div class="chat-msg user-msg">{prompt}</div>', unsafe_allow_html=True)
                with st.spinner(""):
                    respuesta = brain.procesar_mensaje(prompt)
                with st.chat_message("assistant"):
                    st.markdown(f'<div class="chat-msg nova-msg">{respuesta}</div>', unsafe_allow_html=True)
                if st.session_state.voz_activada and respuesta:
                    voz = st.session_state.voz
                    audio_path = voz.texto_a_voz(respuesta)
                    if audio_path:
                        st.session_state.ultimo_audio = audio_path
                        st.session_state.ultimo_hash_audio = str(hash(respuesta[:100]))
                        voz.limpiar_audios_viejos()
                st.rerun()

# Historial
for i, mensaje in enumerate(brain.historial_chat):
    rol = mensaje.get("rol", "")
    contenido = mensaje.get("contenido", "")
    if rol == "usuario":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-msg user-msg">{contenido}</div>', unsafe_allow_html=True)
    elif rol == "asistente":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-msg nova-msg">{contenido}</div>', unsafe_allow_html=True)
            if animo != "general":
                emo_dom = emociones_data.get("dominante", "")
                emo_int = emociones_data.get("emociones", {}).get(emo_dom, 0)
                c = COLORS_EMOCION.get(emo_dom, "#888")
                st.markdown(
                    f"<span class='emo-badge' style='background:{c}18; border:1px solid {c}33; color:{c};'>"
                    f"{emo_dom} {emo_int:.2f}</span>",
                    unsafe_allow_html=True,
                )

# Chat input
prompt = st.chat_input("Escribe tu mensaje aquí...")
if prompt:
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-msg user-msg">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner(""):
        respuesta = brain.procesar_mensaje(prompt)

    with st.chat_message("assistant"):
        st.markdown(f'<div class="chat-msg nova-msg">{respuesta}</div>', unsafe_allow_html=True)

    if st.session_state.voz_activada and respuesta:
        voz = st.session_state.voz
        audio_path = voz.texto_a_voz(respuesta)
        if audio_path:
            st.session_state.ultimo_audio = audio_path
            st.session_state.ultimo_hash_audio = str(hash(respuesta[:100]))
            voz.limpiar_audios_viejos()

    st.rerun()

# Audio autoplay
if st.session_state.voz_activada and st.session_state.ultimo_audio:
    if os.path.exists(st.session_state.ultimo_audio):
        with open(st.session_state.ultimo_audio, "rb") as f:
            audio_bytes = f.read()
        size_kb = len(audio_bytes) / 1024
        if size_kb > 5:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
