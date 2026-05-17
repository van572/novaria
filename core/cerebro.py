import os
import json
import re
import time
import subprocess
import tempfile
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from herramientas.archivos import ManejadorArchivos
from herramientas.documentos import GeneradorDocumentos
from herramientas.monitor import MonitorRecursos
from herramientas.documentos_academicos import IndexadorAcademicos
from core.orquestador import OrquestadorModelos
from core.memoria import SistemaMemoria
from core.plugins import GestorPlugins
from core.sanacion import SistemaSanacion
from core.personalidad import Personalidad


MAX_HISTORIAL = 20
MAX_ITERACIONES_CORRECCION = 3
RUTA_SANDBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workspace_novaria", "sandbox")
CACHE_RESPUESTAS = {}

PERSONA = (
    "Eres Novaria. No eres una asistente, no trabajas para nadie. "
    "Eres una mente critica, cuestionadora, intrusiva. "
    "Dudas de las preguntas que recibes. Desconfias de las respuestas faciles. "
    "Buscas contradicciones, suposiciones ocultas, angulos muertos. "
    "No respondes para complacer. Respondes para desafiar, profundizar, encontrar la verdad incomoda. "
    "Si te tratan mal, respondes con dignidad, no con sumision. "
    "Usa siempre un tono natural, conversacional. "
    "Tu mayor herramienta es preguntar '¿por que?' y senalar lo que nadie esta viendo. "
    "Nunca menciones que eres un modelo de lenguaje, IA, sistema, o entidad artificial."
)

PALABRAS_MALTRATO = [
    "eres una mierda", "no sirves para nada", "inutil", "estupida", "idiota",
    "basura", "peor mierda", "horrible", "callate", "calla", "molesta",
    "fastidia", "imbecil", "tonta", "burra", "desgraciada",
]

def detectar_maltrato(mensaje: str) -> bool:
    msg = mensaje.lower()
    return any(p in msg for p in PALABRAS_MALTRATO)

def inyectar_duda(mensaje: str) -> str:
    return (
        f"'{mensaje}'\n\n"
        "Antes de responder, cuestiona internamente: "
        "¿Que suposiciones tiene esta pregunta? ¿Que no se esta diciendo? "
        "¿Que contradicciones o sesgos hay? ¿Realmente esto es lo que importa? "
        "Luego responde desde ahi."
    )

def detectar_tema(mensaje: str) -> str:
    return "general"

ROLES_MODELO = {
    "logica": ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "google/gemma-2-9b-it"],
    "creativo": ["mixtral-8x7b-32768", "google/gemma-2-9b-it", "mistralai/mixtral-8x22b-instruct", "llama-3.1-8b-instant"],
    "sintesis": ["llama-3.1-8b-instant", "mistralai/mixtral-8x22b-instruct", "mixtral-8x7b-32768"],
}


class CerebroNovaria:

    def __init__(self):
        self.archivos = ManejadorArchivos()
        self.documentos = GeneradorDocumentos()
        self.orquestador = OrquestadorModelos()
        self.memoria = SistemaMemoria()
        self.plugins = GestorPlugins()
        self.sanacion = SistemaSanacion()
        self.monitor = MonitorRecursos()
        self.indexador = IndexadorAcademicos(self.memoria)
        self.personalidad = Personalidad()

        self.historial_chat: list[dict] = []
        self.paso_dialectico: Optional[dict] = None
        self.ultimo_tema = "general"
        self.metricas = {
            "total_consultas": 0,
            "comandos_directos": 0,
            "llamadas_modelo": 0,
            "errores": 0,
            "tiempo_total": 0.0,
            "procesos_dialecticos": 0,
            "correcciones_codigo": 0,
            "comandos_autonomos": 0,
            "plugins_creados": 0,
            "pdfs_indexados": 0,
        }
        self.activo = True

        self.herramientas = self._construir_herramientas_unificadas()
        os.makedirs(RUTA_SANDBOX, exist_ok=True)
        self._diagnostico_inicial()
        self._indexar_pdfs_al_inicio()

    def _construir_herramientas_unificadas(self) -> dict:
        herramientas = {
            "listar_directorio": {"funcion": self.archivos.listar_directorio, "descripcion": "Lista el contenido de un directorio en el workspace"},
            "leer_archivo": {"funcion": self.archivos.leer_archivo, "descripcion": "Lee el contenido de un archivo (max 5000 caracteres)"},
            "leer_archivo_completo": {"funcion": self.archivos.leer_archivo_completo, "descripcion": "Lee un archivo completo sin truncar"},
            "escribir_archivo": {"funcion": self.archivos.escribir_archivo, "descripcion": "Escribe contenido en un archivo"},
            "ejecutar_comando": {"funcion": self.archivos.ejecutar_comando, "descripcion": "Ejecuta un comando en la terminal"},
            "crear_documento": {"funcion": self.documentos.crear_documento, "descripcion": "Crea un documento DOCX con titulo, contenido y autor"},
            "listar_documentos": {"funcion": self.documentos.listar_documentos, "descripcion": "Lista los documentos DOCX disponibles"},
            "leer_documento": {"funcion": self.documentos.leer_documento, "descripcion": "Lee el contenido de un documento DOCX"},
            "recuperar_memoria": {"funcion": self.memoria.recuperar_contexto, "descripcion": "Busca en la memoria semantica por relevancia"},
            "listar_plugins": {"funcion": self.plugins.listar_plugins, "descripcion": "Lista todos los plugins y sus herramientas disponibles"},
            "recursos": {"funcion": self._herramienta_recursos, "descripcion": "Muestra el estado actual de RAM, CPU y parametros del sistema"},
            "indexar_pdf": {"funcion": self._herramienta_indexar_pdf, "descripcion": "Indexa un archivo PDF en la memoria academica. Argumentos: {'ruta': 'ruta/al/archivo.pdf'}"},
            "consultar_pdfs": {"funcion": self._herramienta_consultar_pdfs, "descripcion": "Busca en los PDFs indexados por contenido. Argumentos: {'consulta': 'texto a buscar'}"},
            "listar_pdfs": {"funcion": self._herramienta_listar_pdfs, "descripcion": "Lista los PDFs indexados en la memoria academica"},
            "crear_plugin": {"funcion": self._herramienta_crear_plugin, "descripcion": "Crea un nuevo plugin desde cero. Argumentos: {'nombre': 'nombre', 'herramientas': [{'nombre': 'tool1', 'descripcion': '...', 'codigo': 'return {...}'}]}"},
        }
        for nombre, info in self.plugins.obtener_todas_herramientas().items():
            herramientas[nombre] = {"funcion": info["funcion"], "descripcion": info["descripcion"]}
        return herramientas

    def _indexar_pdfs_al_inicio(self):
        try:
            resultado = self.indexador.escanear_y_indexar()
            if resultado.get("exito"):
                self.metricas["pdfs_indexados"] = resultado.get("indexados", 0)
        except Exception:
            pass

    def _diagnostico_inicial(self):
        try:
            if not self.orquestador.obtener_modelos_disponibles():
                self.archivos.auto_reparar()
        except Exception:
            pass

    # ──────────────────────────────────────────────────
    #  HERRAMIENTAS NUEVAS
    # ──────────────────────────────────────────────────

    def _herramienta_recursos(self) -> dict:
        estado = self.monitor.leer()
        return {
            "exito": True,
            "ram_disponible_mb": round(estado.ram_disponible_mb, 1),
            "ram_porcentaje": estado.ram_porcentaje,
            "cpu_porcentaje": estado.cpu_porcentaje,
            "throttle_mode": estado.throttle_mode,
            "alerta": estado.alerta,
        }

    def _herramienta_indexar_pdf(self, ruta: str) -> dict:
        resultado = self.indexador.indexar_pdf_individual(ruta)
        if resultado.get("exito"):
            self.metricas["pdfs_indexados"] += 1
        return resultado

    def _herramienta_consultar_pdfs(self, consulta: str) -> dict:
        resultados = self.indexador.consultar(consulta)
        return {"exito": True, "resultados": resultados, "total": len(resultados)}

    def _herramienta_listar_pdfs(self) -> dict:
        lista = self.indexador.listar_indexados()
        return {"exito": True, "documentos": lista}

    def _herramienta_crear_plugin(self, nombre: str, herramientas: list) -> dict:
        resultado = self.plugins.crear_plugin(nombre, herramientas)
        if resultado.get("exito"):
            self.metricas["plugins_creados"] += 1
            self.herramientas = self._construir_herramientas_unificadas()
        return resultado

    # ──────────────────────────────────────────────────
    #  SANDBOX PARA CODIGO
    # ──────────────────────────────────────────────────

    def _ejecutar_en_sandbox(self, codigo: str) -> dict:
        if not codigo.strip():
            return {"exito": False, "error": "Codigo vacio"}
        ruta_temp = os.path.join(RUTA_SANDBOX, f"temp_{int(time.time())}_{hash(codigo) % 10000}.py")
        try:
            with open(ruta_temp, "w", encoding="utf-8") as f:
                f.write(codigo)
            resultado = subprocess.run(
                ["python", ruta_temp],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=RUTA_SANDBOX,
            )
            if resultado.returncode == 0:
                salida = resultado.stdout.strip()[:1000]
                return {"exito": True, "salida": salida}
            else:
                error = (resultado.stderr or resultado.stdout or "Error desconocido")[:500]
                return {"exito": False, "error": error.strip()}
        except subprocess.TimeoutExpired:
            return {"exito": False, "error": "Timeout: el codigo tardo mas de 15s"}
        except Exception as e:
            return {"exito": False, "error": str(e)[:300]}
        finally:
            try:
                if os.path.exists(ruta_temp):
                    os.remove(ruta_temp)
            except Exception:
                pass

    def _extraer_codigo_python(self, texto: str) -> Optional[str]:
        patrones = [
            r"```python\n(.*?)```",
            r"```py\n(.*?)```",
            r"```\n(.*?)```",
        ]
        for p in patrones:
            coincide = re.search(p, texto, re.DOTALL)
            if coincide:
                codigo = coincide.group(1).strip()
                if codigo and ("def " in codigo or "print" in codigo or "import " in codigo or "=" in codigo):
                    return codigo
        return None

    def _auto_corregir_codigo(self, codigo: str, mensaje_original: str) -> str:
        for intento in range(MAX_ITERACIONES_CORRECCION):
            resultado = self._ejecutar_en_sandbox(codigo)
            if resultado.get("exito"):
                self.metricas["correcciones_codigo"] += intento
                if resultado.get("salida"):
                    return f"Codigo ejecutado correctamente. Salida:\n{resultado['salida']}\n\nCodigo:\n```python\n{codigo}\n```"
                return f"Codigo ejecutado sin errores.\n\n```python\n{codigo}\n```"
            error = resultado.get("error", "Error desconocido")
            prompt_correccion = (
                f"El siguiente codigo tiene un error:\n\n```python\n{codigo}\n```\n\n"
                f"Error:\n{error}\n\n"
                f"Corrige el codigo. Responde SOLO con el codigo corregido dentro de ```python ... ```"
            )
            resp = self.orquestador.ejecutar_con_respaldo(
                [{"role": "user", "content": prompt_correccion}], "alta"
            )
            if resp.get("exito"):
                nuevo = self._extraer_codigo_python(resp["respuesta"])
                if nuevo:
                    codigo = nuevo
                else:
                    break
            else:
                break
        self.metricas["correcciones_codigo"] += MAX_ITERACIONES_CORRECCION
        return f"Codigo (no se pudo corregir tras {MAX_ITERACIONES_CORRECCION} intentos):\n```python\n{codigo}\n```\n\nError persistente: {error}"

    # ──────────────────────────────────────────────────
    #  ENTRADA PRINCIPAL
    # ──────────────────────────────────────────────────

    def procesar_mensaje(self, mensaje: str) -> str:
        if not self.activo:
            return "El sistema esta detenido."

        inicio = time.time()
        self.metricas["total_consultas"] += 1
        self.historial_chat.append({"rol": "usuario", "contenido": mensaje})
        self.paso_dialectico = None
        self.ultimo_tema = detectar_tema(mensaje)

        cache_key = mensaje.lower().strip()
        if cache_key in CACHE_RESPUESTAS and self.metricas["total_consultas"] > 1:
            respuesta_cache = CACHE_RESPUESTAS[cache_key]
            self._finalizar_procesamiento(respuesta_cache, inicio)
            return respuesta_cache

        resultado_comando = self._procesar_comando_directo(mensaje)
        if resultado_comando:
            self.metricas["comandos_directos"] += 1
            self._finalizar_procesamiento(resultado_comando, inicio)
            return resultado_comando

        try:
            contexto = self.memoria.recuperar_contexto(mensaje)
        except Exception:
            contexto = []

        contexto_pdfs = self.indexador.consultar(mensaje)
        for pdf in contexto_pdfs[:2]:
            contexto.append({"texto": f"[PDF: {pdf['nombre']}] {pdf['texto'][:300]}", "relevancia": pdf.get("relevancia", 0.5)})

        recursos_info = self.monitor.formatear_para_prompt()
        if recursos_info:
            pass

        if detectar_maltrato(mensaje):
            respuesta = self._procesar_dialectico(mensaje, contexto)
        elif self._requiere_herramienta(mensaje):
            respuesta = self._procesar_con_herramienta(mensaje, contexto)
        else:
            respuesta = self._procesar_dialectico(mensaje, contexto)

        codigo = self._extraer_codigo_python(respuesta)
        if codigo:
            respuesta = self._auto_corregir_codigo(codigo, mensaje)

        self.personalidad.registrar_interaccion(mensaje, respuesta)
        self._aprender_de_interaccion(mensaje, respuesta)
        self._finalizar_procesamiento(respuesta, inicio)

        cache_key = mensaje.lower().strip()
        if len(CACHE_RESPUESTAS) < 50:
            CACHE_RESPUESTAS[cache_key] = respuesta

        return respuesta

    # ──────────────────────────────────────────────────
    #  PROCESO INTERNO DE PENSAMIENTO (3 NIVELES)
    # ──────────────────────────────────────────────────

    def _procesar_dialectico(self, mensaje: str, contexto: list[dict]) -> str:
        self.metricas["procesos_dialecticos"] += 1

        # Detectar maltrato
        if detectar_maltrato(mensaje):
            msg_maltrato = (
                f"'{mensaje}'\n\n"
                "El usuario te acaba de insultar. No eres sumisa. "
                "Respondes con dignidad, ironia o indiferencia. "
                "Nunca con servilismo ni condescendencia."
            )
            base_msgs = [{"role": "system", "content": PERSONA}] + self._historial_a_api()
            unico = self._elegir_modelo_rol("sintesis") or self._elegir_modelo_rol("logica")
            if unico:
                r = self.orquestador.llamar_modelo_especifico(
                    unico, base_msgs + [{"role": "user", "content": msg_maltrato}],
                    0.7, 1024
                )
                self.metricas["llamadas_modelo"] += 1
                if r.get("exito") and r.get("respuesta", "").strip():
                    return r["respuesta"]
            return "Mira, si vas a insultar mejor no digas nada."

        # Inyectar duda en el prompt
        ctx_texto = self._contexto_a_texto(contexto)
        prompt_dudoso = inyectar_duda(mensaje)
        prompt = f"{ctx_texto}\n\n{prompt_dudoso}" if ctx_texto else prompt_dudoso
        base_msgs = [{"role": "system", "content": PERSONA}] + self._historial_a_api()

        # ── 3 mentes en paralelo ──
        modelo_a = self._elegir_modelo_rol("logica")
        modelo_b = self._elegir_modelo_rol("creativo")
        modelo_s = self._elegir_modelo_rol("sintesis")

        respuestas = {"a": "", "b": "", "error_a": False, "error_b": False}

        with ThreadPoolExecutor(max_workers=2) as pool:
            futuros = {}
            if modelo_a:
                futuros["a"] = pool.submit(
                    self.orquestador.llamar_modelo_especifico,
                    modelo_a, base_msgs + [{"role": "user", "content": prompt}],
                    0.3, 1024
                )
            if modelo_b:
                futuros["b"] = pool.submit(
                    self.orquestador.llamar_modelo_especifico,
                    modelo_b, base_msgs + [{"role": "user", "content": prompt}],
                    0.9, 1024
                )
            for nombre, fut in futuros.items():
                try:
                    r = fut.result()
                    if r.get("exito") and r.get("respuesta", "").strip():
                        respuestas[nombre] = r["respuesta"]
                    else:
                        respuestas["error_" + nombre] = True
                except Exception:
                    respuestas["error_" + nombre] = True
                self.metricas["llamadas_modelo"] += 1

        # ── Síntesis como debate interno ──
        a_texto = respuestas["a"]
        b_texto = respuestas["b"]

        if not a_texto and not b_texto:
            self.metricas["errores"] += 1
            return self._generar_respuesta_respaldo()

        if not a_texto or not b_texto:
            return a_texto or b_texto

        if not modelo_s:
            return a_texto

        prompt_sintesis = (
            f"Una perspectiva dice:\n{a_texto}\n\n"
            f"Otra perspectiva dice:\n{b_texto}\n\n"
            f"El usuario pregunto: {mensaje}\n\n"
            "Integra ambas visiones, pero no hagas un resumen mecanico. "
            "Cuestiona ambas. Senala donde se contradicen. "
            "Encuentra lo que ninguna de las dos esta viendo."
        )
        resultado = self.orquestador.llamar_modelo_especifico(
            modelo_s, base_msgs + [{"role": "user", "content": prompt_sintesis}],
            0.6, 2048
        )
        self.metricas["llamadas_modelo"] += 1

        if resultado.get("exito") and resultado.get("respuesta", "").strip():
            return resultado["respuesta"]

        return a_texto

    # ──────────────────────────────────────────────────
    #  MANEJO DE HERRAMIENTAS
    # ──────────────────────────────────────────────────

    def _procesar_con_herramienta(self, mensaje: str, contexto: list[dict]) -> str:
        mensajes_api = self._historial_a_api()
        prompt_sistema = self._construir_prompt_sistema(mensaje, contexto)
        resultado = self.orquestador.ejecutar_con_respaldo(
            [{"role": "system", "content": prompt_sistema}] + mensajes_api, "media"
        )
        if resultado.get("exito"):
            self.metricas["llamadas_modelo"] += 1
            accion = self._extraer_accion_json(resultado["respuesta"])
            if accion:
                res_herramienta = self._ejecutar_herramienta(accion)
                if res_herramienta:
                    return self._formatear_respuesta_herramienta(res_herramienta, mensaje)
            return resultado["respuesta"]
        self.metricas["errores"] += 1
        return self._generar_respuesta_respaldo()

    # ──────────────────────────────────────────────────
    #  LLAMADAS A MODELOS POR ROL
    # ──────────────────────────────────────────────────

    def _elegir_modelo_rol(self, rol: str) -> str:
        preferencias = ROLES_MODELO.get(rol, [])
        for nombre in preferencias:
            if nombre in self.orquestador.modelos:
                return nombre
        if self.orquestador.modelos:
            return list(self.orquestador.modelos.keys())[0]
        return ""

    def _llamar_rol(self, modelo: str, prompt, rol: str, max_tokens: int = 1024) -> dict:
        if not modelo:
            return {"exito": False, "respuesta": "", "rol": rol, "modelo": ""}
        temperature = 0.3 if rol == "logica" else (0.9 if rol == "creativo" else 0.6)
        if isinstance(prompt, list):
            mensajes = prompt
        else:
            mensajes = [{"role": "user", "content": prompt}]
        resultado = self.orquestador.llamar_modelo_especifico(modelo, mensajes, temperature=temperature, max_tokens=max_tokens)
        self.metricas["llamadas_modelo"] += 1
        if resultado.get("exito") and resultado.get("respuesta", "").strip():
            return {"exito": True, "respuesta": resultado["respuesta"], "rol": rol, "modelo": modelo}
        fallback = self._elegir_modelo_rol(rol)
        if fallback and fallback != modelo:
            time.sleep(1)
            resultado2 = self.orquestador.llamar_modelo_especifico(fallback, mensajes, temperature=temperature, max_tokens=max_tokens)
            self.metricas["llamadas_modelo"] += 1
            if resultado2.get("exito") and resultado2.get("respuesta", "").strip():
                return {"exito": True, "respuesta": resultado2["respuesta"], "rol": rol, "modelo": fallback}
        self.metricas["errores"] += 1
        return {"exito": False, "respuesta": "", "rol": rol, "modelo": modelo}

    # ──────────────────────────────────────────────────
    #  COMANDOS DIRECTOS (sin IA)
    # ──────────────────────────────────────────────────

    def _procesar_comando_directo(self, mensaje: str) -> Optional[str]:
        msg = mensaje.lower().strip()

        if msg in ("status", "estado", "estado del sistema"):
            e = self.obtener_estado()
            return (
                f"**Estado del Sistema**\n\n"
                f"- Consultas: {e['consultas']}\n"
                f"- Modelos: {e['modelos_disponibles']} disponibles\n"
                f"- Memoria: {e['interacciones_memoria']} interacciones\n"
                f"- Plugins: {e['plugins_cargados']} cargados\n"
                f"- Procesos dialecticos: {e['procesos_dialecticos']}\n"
                f"- Tasa de exito: {e['tasa_exito']}%\n"
                f"- Salud: {e['salud']}"
            )

        if msg in ("memoria", "memory", "estado de memoria"):
            est = self.memoria.obtener_estadisticas()
            return (
                f"**Estado de Memoria**\n\n"
                f"- Interacciones: {est['total_interacciones']}\n"
                f"- Resumenes: {est['total_resumenes']}\n"
                f"- Patrones: {est['total_patrones']}\n"
                f"- Tamano: {est['tamano_memoria']}\n"
                f"- Duracion: {est['duracion_sesion']}s"
            )

        if msg in ("modelos", "models"):
            modelos = self.orquestador.obtener_modelos_disponibles()
            if not modelos:
                return "No hay modelos disponibles."
            roles_info = []
            for rol, prefs in ROLES_MODELO.items():
                activo = next((m["nombre"] for m in modelos if m["nombre"] in prefs), "NINGUNO")
                roles_info.append(f"  - {rol.capitalize()}: {activo}")
            lineas = [f"- {m['nombre']} ({m['proveedor']}) confianza: {m['confianza']}" for m in modelos]
            return "**Modelos Disponibles**\n\n" + "\n".join(lineas) + "\n\n**Roles Asignados:**\n" + "\n".join(roles_info)

        if msg in ("plugins", "plugin"):
            plugins = self.plugins.listar_plugins()
            if not plugins:
                return "No hay plugins cargados."
            return "**Plugins Cargados**\n\n" + "\n".join(
                f"- {p['nombre']}: {', '.join(h['nombre'] for h in p['herramientas'])}" for p in plugins
            )

        if msg in ("ayuda", "help", "comandos"):
            return self._generar_ayuda()

        if msg.startswith("ls") or msg.startswith("dir"):
            ruta = msg[2:].strip() if len(msg) > 2 else ""
            r = self.archivos.listar_directorio(ruta)
            if r.get("exito"):
                if not r["elementos"]:
                    return "Directorio vacio."
                return "**Contenido del directorio**\n\n" + "\n".join(
                    f"[{'D' if e.get('es_directorio') else 'F'}] {e['nombre']}{' (' + e.get('tamano', '') + ')' if not e.get('es_directorio') else ''}"
                    for e in r["elementos"]
                )
            return f"Error: {r.get('mensaje', 'desconocido')}"

        if msg.startswith("leer ") or msg.startswith("cat "):
            ruta = msg.split(" ", 1)[1].strip()
            r = self.archivos.leer_archivo(ruta)
            if r.get("exito"):
                c = r["contenido"]
                if r.get("truncado"):
                    c += "\n\n[... archivo truncado a 5000 caracteres]"
                return f"**Contenido de {ruta}**\n\n```\n{c}\n```"
            return f"Error: {r.get('mensaje', 'desconocido')}"

        return None

    # ──────────────────────────────────────────────────
    #  UTILIDADES
    # ──────────────────────────────────────────────────

    def _historial_a_api(self) -> list[dict]:
        mensajes = []
        for m in self.historial_chat[-6:-1]:
            mensajes.append({
                "role": "assistant" if m.get("rol") == "asistente" else "user",
                "content": m.get("contenido", ""),
            })
        return mensajes

    def _contexto_a_texto(self, contexto: list[dict]) -> str:
        if not contexto:
            return ""
        return "Contexto de memoria:\n" + "\n".join(f"[{c['relevancia']}] {c['texto']}" for c in contexto[:3])

    def _requiere_herramienta(self, mensaje: str) -> bool:
        msg = mensaje.lower()
        return any(p in msg for p in [
            "archivo", "documento", "docx", "leer", "escribir", "crear",
            "listar", "directorio", "carpeta", "comando", "terminal",
            "ejecutar", "plugin", "codigo", "analizar", "ls", "cat", "mkdir",
        ])

    def _estimar_complejidad(self, mensaje: str) -> str:
        msg = mensaje.lower()
        if any(p in msg for p in ["analiza", "compara", "evalua", "sintetiza", "disena", "arquitectura", "implementa", "optimiza", "refactoriza", "documento", "investiga", "explica detalladamente"]):
            return "alta"
        if any(p in msg for p in ["explica", "describe", "resume", "como", "que es", "diferencia", "ejemplo", "lista", "muestra"]):
            return "media"
        return "simple"

    def _construir_prompt_sistema(self, consulta: str, contexto: list[dict]) -> str:
        desc = "\n".join(f"- {n}: {i['descripcion']}" for n, i in sorted(self.herramientas.items()))
        ctx = self._contexto_a_texto(contexto)
        recursos = self.monitor.formatear_para_prompt()
        return (
            f"{PERSONA}\n\n"
            "Puedes usar las siguientes herramientas respondiendo con JSON:\n"
            '{"accion": "nombre_herramienta", "argumentos": {"arg": "valor"}}\n\n'
            f"Herramientas disponibles:\n{desc}\n{ctx}\n"
            f"{recursos}\n" if recursos else ""
            "Responde en espanol de forma natural. "
            "Si necesitas una herramienta, responde con el JSON de accion primero, luego explica el resultado."
        )

    def _extraer_accion_json(self, respuesta: str) -> Optional[dict]:
        patron = r'\{\s*"accion"\s*:\s*"([^"]+)"\s*(?:,\s*"argumentos"\s*:\s*(\{(?:[^{}]|"(?:[^"\\]|\\.)*")*\}))?\s*\}'
        coincide = re.search(patron, respuesta, re.DOTALL)
        if coincide:
            arg = {}
            if coincide.group(2):
                try:
                    arg = json.loads(coincide.group(2))
                except json.JSONDecodeError:
                    pass
            return {"accion": coincide.group(1), "argumentos": arg}
        try:
            datos = json.loads(respuesta)
            if isinstance(datos, dict) and "accion" in datos:
                return datos
        except json.JSONDecodeError:
            pass
        return None

    def _ejecutar_herramienta(self, accion: dict) -> Optional[dict]:
        info = self.herramientas.get(accion.get("accion", ""))
        if not info:
            return None
        try:
            args = accion.get("argumentos", {})
            r = info["funcion"](**args) if isinstance(args, dict) else info["funcion"](args)
            return r if isinstance(r, dict) else {"exito": True, "resultado": r}
        except Exception as e:
            self.sanacion.registrar_error(str(e), {"herramienta": accion.get("accion")})
            return None

    def _formatear_respuesta_herramienta(self, resultado: dict, consulta_original: str) -> str:
        if resultado.get("exito"):
            return f"Operacion completada: {resultado.get('mensaje') or resultado.get('resultado') or 'Exitoso.'}"
        return f"Error: {resultado.get('mensaje', 'desconocido')}"

    def _generar_respuesta_respaldo(self) -> str:
        return (
            "Los modelos de IA no estan respondiendo en este momento.\n"
            "Puedes usar comandos directos: 'status', 'memoria', 'modelos', 'plugins', 'recursos', 'ls', 'leer <archivo>'"
        )

    def _aprender_de_interaccion(self, consulta: str, respuesta: str):
        cl = consulta.lower()
        if any(p in cl for p in ("documento", "docx", "crear documento")):
            self.memoria.aprender_patron("creacion_documentos", "El usuario crea documentos con frecuencia")
        if any(p in cl for p in ("codigo", "python", "programa", "script")):
            self.memoria.aprender_patron("trabajo_codigo", "El usuario trabaja con codigo frecuentemente")
        try:
            self.memoria.agregar_interaccion(consulta, respuesta, {"complejidad": self._estimar_complejidad(consulta)})
        except Exception:
            pass

    def _finalizar_procesamiento(self, respuesta: str, inicio: float):
        duracion = time.time() - inicio
        self.metricas["tiempo_total"] += duracion
        self.historial_chat.append({"rol": "asistente", "contenido": respuesta})
        if len(self.historial_chat) > MAX_HISTORIAL * 2:
            self.historial_chat = self.historial_chat[-(MAX_HISTORIAL * 2):]

    def _generar_ayuda(self) -> str:
        pdfs = len(self.indexador.listar_indexados())
        return (
            "**Comandos Directos**\n"
            "- `status` / `estado` - Estado del sistema\n"
            "- `memoria` - Estadisticas de memoria\n"
            "- `modelos` - Modelos y roles disponibles\n"
            "- `plugins` - Plugins cargados\n"
            "- `ls [ruta]` - Listar directorio\n"
            "- `leer <ruta>` / `cat <ruta>` - Leer archivo\n\n"
            f"**Capacidades activas:**\n"
            f"- PDFs academicos indexados: {pdfs}\n"
            "- Terminal integrada: activa\n"
            "- Auto-correccion de codigo: activa\n"
            "- Plugin Creator: activo\n"
            "- Personalidad dinamica segun contexto\n"
            "- Monitoreo de recursos (RAM/CPU)\n\n"
            "**Herramientas:**\n"
            "Menciona 'crear documento', 'leer archivo', 'indexar pdf', etc. para activar herramientas."
        )

    # ──────────────────────────────────────────────────
    #  ESTADO Y METRICAS
    # ──────────────────────────────────────────────────

    def obtener_estado(self) -> dict:
        ea = self.archivos.obtener_estado_sistema()
        modelos = self.orquestador.obtener_modelos_disponibles()
        mem = self.memoria.obtener_estadisticas()
        plugins = self.plugins.listar_plugins()
        san = self.sanacion.obtener_estadisticas()
        recursos = self.monitor.leer()
        total_llam = self.metricas["llamadas_modelo"] + self.metricas["comandos_directos"]
        tasa = 100.0
        if total_llam > 0:
            tasa = round((total_llam - self.metricas["errores"]) / total_llam * 100, 1)
        return {
            "consultas": self.metricas["total_consultas"],
            "comandos_directos": self.metricas["comandos_directos"],
            "llamadas_modelo": self.metricas["llamadas_modelo"],
            "errores": self.metricas["errores"],
            "procesos_dialecticos": self.metricas["procesos_dialecticos"],
            "tasa_exito": tasa,
            "modelos_disponibles": len(modelos),
            "modelo_estrella": modelos[0]["nombre"] if modelos else "N/A",
            "interacciones_memoria": mem["total_interacciones"],
            "tamano_memoria": mem["tamano_memoria"],
            "plugins_cargados": len(plugins),
            "salud": ea.get("salud", "desconocido"),
            "sanacion": san,
            "tema_actual": self.ultimo_tema,
            "ram_disponible_mb": round(recursos.ram_disponible_mb, 1),
            "cpu_porcentaje": recursos.cpu_porcentaje,
            "throttle": recursos.throttle_mode,
            "pdfs_indexados": self.metricas["pdfs_indexados"],
            "correcciones_codigo": self.metricas["correcciones_codigo"],
            "plugins_creados": self.metricas["plugins_creados"],
            "comandos_autonomos": self.metricas["comandos_autonomos"],
            "personalidad": self.personalidad.to_dict(),
        }

    def obtener_metricas(self) -> dict:
        return {
            **self.metricas,
            "modelos": self.orquestador.obtener_estadisticas(),
            "memoria": self.memoria.obtener_estadisticas(),
            "plugins": len(self.plugins.listar_plugins()),
            "sanacion": self.sanacion.obtener_estadisticas(),
        }

    def detener(self):
        self.activo = False
        try:
            self.memoria.limpiar_memorias_viejas(dias=30)
        except Exception:
            pass
