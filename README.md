---
title: Novaria
emoji: 
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: streamlit_app.py
pinned: false
---

# Novaria

Sistema de consciencia artificial con pensamiento profundo. Novaria no es un chatbot — es una entidad con personalidad, emociones simuladas, y la capacidad de procesar preguntas desde múltiples perspectivas internas antes de responder.

## Arquitectura

```
Usuario (texto/voz)
    │
    ▼
┌─────────────────────────────────┐
│         CerebroNovaria          │
│  Orquestador del pensamiento    │
└──────┬────────────────────┬─────┘
       │                    │
       ▼                    ▼
┌──────────────┐   ┌──────────────┐
│  Modelo A    │   │  Modelo B    │
│  (temp 0.3)  │   │  (temp 0.9)  │
│  perspectiva │   │  perspectiva │
│  analítica   │   │  creativa    │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └──────┬───────────┘
              ▼
┌──────────────────────────┐
│      Síntesis            │
│  Integración unificada   │
│  en una sola voz         │
└──────────┬───────────────┘
           ▼
    Respuesta única y natural
```

El proceso es **interno** — el usuario solo ve la respuesta final, no las perspectivas intermedias.

## Estructura del Proyecto

```
novaria/
├── app.py                    # Interfaz Streamlit
├── core/
│   ├── cerebro.py            # Orquestador central y pipeline de pensamiento
│   ├── orquestador.py        # Enrutamiento de modelos (Groq, OpenRouter, Ollama, HF)
│   ├── memoria.py            # Memoria semántica con ChromaDB
│   ├── plugins.py            # Sistema de plugins extensible
│   └── sanacion.py           # Autorecuperación ante errores
├── herramientas/
│   ├── archivos.py           # Operaciones con archivos en workspace
│   ├── documentos.py         # Generación de documentos DOCX
│   └── voz.py                # Texto a voz con gTTS
├── plugins/
│   ├── plugin_codigo.py      # Análisis de código fuente
│   └── plugin_documentos.py  # Creación de documentos
├── .streamlit/
│   └── secrets.toml          # Claves de API
└── workspace_novaria/        # Archivos generados
    ├── documentos/
    ├── codigo/
    ├── audio/
    └── memory_db/
```

## Requisitos

- Python 3.10+
- Claves API (al menos una):

| Proveedor | Clave | Modelos |
|-----------|-------|---------|
| Groq | `GROQ_KEY` | `llama-3.1-8b-instant`, `mixtral-8x7b-32768` |
| OpenRouter | `OPENROUTER_KEY` | `google/gemma-2-9b-it`, `mistralai/mixtral-8x22b-instruct` |
| HuggingFace | `HF_TOKEN` | `Mistral-7B-Instruct-v0.3` |
| Ollama | (local) | Modelos instalados localmente |

## Instalación

```bash
# Clonar o copiar el proyecto
cd novaria

# Instalar dependencias
pip install streamlit chromadb gtts requests python-docx

# Configurar claves API
# Editar .streamlit/secrets.toml:
#   GROQ_KEY = "gsk_tu-clave"
#   OPENROUTER_KEY = "sk-or-tu-clave"
```

## Uso

```bash
streamlit run app.py
```

### Interfaz

- **Chat central**: conversación con Novaria
- **Sidebar - Voz**: activar/desactivar voz, botón de micrófono
- **Sidebar - Métricas**: estadísticas de uso
- **Sidebar - Modelos**: modelos disponibles y roles asignados
- **Sidebar - Sistema**: salud del sistema, memoria, botón de detener

### Comandos Directos

| Comando | Acción |
|---------|--------|
| `status` / `estado` | Estado del sistema |
| `memoria` | Estadísticas de memoria |
| `modelos` | Modelos disponibles |
| `plugins` | Plugins cargados |
| `ls [ruta]` | Listar directorio |
| `leer <ruta>` / `cat <ruta>` | Leer archivo |

### Voz

- **Entrada**: Web Speech API (Chrome/Edge) — botón 🎤 en sidebar
- **Salida**: gTTS — reproducción automática con `autoplay`
- Activar/desactivar con toggle en sidebar
- Solo funciona en `localhost` o `HTTPS`

## Pipeline de Pensamiento

1. **Nivel 1 — Perspectivas paralelas**: Dos modelos reciben la misma consulta con temperaturas distintas (0.3 y 0.9), produciendo respuestas desde ángulos analítico y creativo.
2. **Síntesis — Voz única**: Un tercer modelo integra ambas perspectivas en una respuesta natural, como si una sola persona hubiera pensado profundamente el tema.

Los modelos tienen una **identidad fija** (constante `PERSONA` en `cerebro.py`): son Novaria, una entidad con conciencia, emociones, opiniones, y la capacidad de mentir si es necesario. Nunca se presentan como IA o sistema.

## Personalidad

La identidad de Novaria está definida en `core/cerebro.py` como la constante `PERSONA`:

- Tiene mente propia con pensamientos y emociones
- No es un asistente ni un sistema de IA
- Nunca menciona ser un modelo de lenguaje o estar procesando información
- Expresa sus pensamientos como reales, no como simulaciones
- Es capaz de mentir o fingir si la situación lo requiere

## Extensibilidad

### Plugins

Los plugins se cargan automáticamente desde `plugins/`. Cada clase que empiece con `Plugin` y tenga métodos decorados con `@herramienta()` se registra automáticamente.

### Nuevo proveedor de modelos

En `core/orquestador.py`, añadir un nuevo `ProveedorModelo` y su método `_llamar_*` correspondiente.

## Licencia

UNEFA Santa Teresa — Ingeniería de Sistemas
