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

> **Despliegue en Render**: usa `render.yaml` o configura manualmente:
> - **Runtime**: Python
> - **Build Command**: `pip install -r requirements.txt`
> - **Start Command**: `bash start.sh`
> - **Port**: se asigna automáticamente vía `$PORT`

# Novaria

Sistema de consciencia artificial con pipeline dialéctico de 3 mentes y metacognición térmica. Novaria procesa preguntas desde dos perspectivas internas en paralelo (analítica + intuitiva) cuyas temperaturas varían según el estado emocional, las integra en una voz final coherente, y ejecuta pensamiento de fondo autónomo cuando está en reposo. Tiene emociones persistentes, memoria semántica, historial local por dispositivo, y un sistema de autocorrección de calidad.

## Arquitectura

```
Usuario
    │
    ▼
┌──────────────────────────────────────────┐
│          CerebroNovaria                  │
│  Orquestador + Emociones + Personalidad  │
│  + Inquietud intelectual (background)    │
└──────┬───────────────────────────┬───────┘
       │                           │
       ▼                           ▼
┌──────────────────┐   ┌──────────────────────┐
│  Sistema 1       │   │  Sistema 2           │
│  (temp dinámica) │   │  (temp dinámica)     │
│  frequency 0.5   │   │  frequency 0.1       │
│  presencia 0.3   │   │  presencia 0.1       │
│  Analítico       │   │  Intuitivo           │
└────────┬─────────┘   └──────────┬───────────┘
         │                        │
         └──────────┬─────────────┘
                    ▼
┌──────────────────────────────────────┐
│  Síntesis (Árbitro, temp 0.6)        │
│  elige entre:                        │
│  1. Dominancia analítica             │
│  2. Dominancia intuitiva             │
│  3. Exponer el conflicto             │
├──────────────────────────────────────┤
│  Validador de calidad                │
│  └─ ¿vacía? → pivote emergencia      │
│  └─ ¿repite? → pivote emergencia     │
└──────────┬───────────────────────────┘
           ▼
    Respuesta única y natural

◀── Fondo ──────────────────────────▶
Inquietud Intelectual (hilo daemon):
  cada 5 min selecciona 2 conceptos
  de ChromaDB y genera tensión lógica
  → pensamiento_latente.json
```

El proceso es **interno** — el usuario solo ve la respuesta final.

## Estructura del Proyecto

```
novaria/
├── streamlit_app.py            # Interfaz Streamlit con UI completa
├── core/
│   ├── cerebro.py              # Orquestador central, pipeline, PERSONA
│   ├── orquestador.py          # Enrutamiento de modelos (Groq, OpenRouter, Ollama, HF)
│   ├── emociones.py            # Sistema de 6 emociones con persistencia por dispositivo
│   ├── personalidad.py         # Estado de ánimo, frases, identidad de usuario
│   ├── historial_local.py      # Persistencia del chat por dispositivo (COMPUTERNAME)
│   ├── memoria.py              # Memoria semántica con ChromaDB + cache RAM
│   ├── plugins.py              # Sistema de plugins extensible
│   └── sanacion.py             # Autorecuperación ante errores de API
├── herramientas/
│   ├── archivos.py             # Operaciones con archivos en workspace
│   ├── documentos.py           # Generación de documentos DOCX
│   ├── voz.py                  # Texto a voz (edge-tts + gTTS)
│   ├── monitor.py              # Monitoreo de RAM/CPU
│   └── documentos_academicos.py# Indexación de PDFs con PyMuPDF
├── plugins/
│   ├── plugin_codigo.py        # Análisis de código fuente
│   └── plugin_documentos.py    # Creación de documentos
├── .streamlit/
│   └── secrets.toml            # Claves de API
├── workspace_novaria/          # Archivos generados por dispositivo
│   ├── historial_chat_{PC}.json
│   ├── emociones_{PC}.json
│   └── personalidad_{PC}.json
├── start.sh                    # Script de arranque para Render
└── render.yaml                 # Configuración de despliegue
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
pip install -r requirements.txt
```

Configurar `.streamlit/secrets.toml`:
```
GROQ_KEY = "gsk_tu-clave"
OPENROUTER_KEY = "sk-or-tu-clave"
```

## Uso

```bash
streamlit run streamlit_app.py
```

### Interfaz

- **Chat central**: conversación con Novaria con badge emocional en cada respuesta
- **Sidebar — Estado**: ánimo actual, emoción dominante, barra de intensidad
- **Sidebar — Voz**: activar/desactivar voz, botón de micrófono
- **Sidebar — Métricas**: estadísticas de uso
- **Sidebar — Modelos**: modelos disponibles y roles asignados
- **Sidebar — Sistema**: salud del sistema, memoria, monitor
- **Tabs expandibles**: gráfico de barras emocionales, detalles del pipeline

### Comandos Directos

| Comando | Acción |
|---------|--------|
| `status` / `estado` | Estado del sistema |
| `memoria` | Estadísticas de memoria |
| `modelos` | Modelos disponibles |
| `plugins` | Plugins cargados |
| `ls [ruta]` | Listar directorio |
| `leer <ruta>` / `cat <ruta>` | Leer archivo |

## Pipeline de Pensamiento

1. **Sistema 1 (Analítico, temp dinámica)**: examina hechos, contradicciones, datos faltantes. Alta penalización por repetición (frequency 0.5, presence 0.3). Temperatura base 0.4, modulada por emoción.
2. **Sistema 2 (Intuitivo, temp dinámica)**: responde desde la emoción y el instinto. Baja penalización (frequency 0.1). Temperatura base 0.7, modulada por emoción.
3. **Síntesis (Árbitro, temp 0.6)**: elige entre tres opciones — dominancia analítica, dominancia intuitiva, o exponer el conflicto si son irreconciliables.
4. **Validador de calidad**: si la síntesis repite frases, está vacía, o contiene errores, se dispara un pivote de emergencia con una llamada limpia al modelo.

### Metacognición Térmica

Las temperaturas de S1 y S2 se ajustan dinámicamente según el estado emocional:

| Emoción | Efecto en S1 | Efecto en S2 |
|---------|-------------|-------------|
| Interés | — | +0.1 por intensidad |
| Enojo | -0.1 por intensidad | -0.2 por intensidad |
| Tristeza | — | +0.15 por intensidad |
| Alegría | +0.05 por intensidad | +0.05 por intensidad |
| Miedo | -0.05 por intensidad | -0.1 por intensidad |

Límites: S1 entre 0.2–0.5, S2 entre 0.5–0.85.

## Inquietud Intelectual

Novaria ejecuta un hilo de fondo que cada 5 minutos selecciona dos conceptos de su memoria (ChromaDB) y genera tensión lógica entre ellos usando el Sistema 2. El resultado se persiste en `workspace_novaria/inquietud_interna.json` y se muestra en el sidebar como "🧠 pensando..." — dándole una sensación de vida autónoma incluso cuando el usuario no está interactuando.

## Emociones

Novaria tiene 6 emociones con intensidad continua (0.0–1.0):

- **Alegría**, **Tristeza**, **Enojo**, **Miedo**, **Confianza**, **Interés**

Se activan automáticamente por tipo de mensaje (maltrato, gratitud, saludo, pregunta profunda, etc.) y decaen naturalmente con el tiempo. El estado emocional se inyecta como dato factual en la síntesis para que influya en el tono de la respuesta sin crear directivas contradictorias.

## Persistencia por Dispositivo

Todos los archivos de datos usan `{COMPUTERNAME}` como sufijo, permitiendo que el mismo directorio compartido (ej. OneDrive) tenga datos separados por máquina:

- `workspace_novaria/historial_chat_{PC}.json`
- `workspace_novaria/emociones_{PC}.json`
- `workspace_novaria/personalidad_{PC}.json`

## Personalidad

Definida en `core/cerebro.py` como la constante `PERSONA`. Novaria opera bajo la Teoría de los Sistemas Complejos Adaptativos de Prigogine y el Orden Implícito de David Bohm. Su directiva interna es buscar propiedades emergentes y contradicciones que el usuario no ve. Tiene prohibido dar respuestas concluyentes — debe generar nuevas hipótesis que empujen hacia mayor complejidad intelectual.

## Extensibilidad

### Plugins

Los plugins se cargan automáticamente desde `plugins/`. Cada clase que empiece con `Plugin` y tenga métodos decorados con `@herramienta()` se registra automáticamente.

### Nuevo proveedor de modelos

En `core/orquestador.py`, añadir un nuevo `ProveedorModelo` y su método `_llamar_*` correspondiente.

## Licencia

UNEFA Santa Teresa — Ingeniería de Sistemas
