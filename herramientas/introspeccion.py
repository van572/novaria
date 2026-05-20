import os
import re

RUTA_CORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core")
RUTA_HERRAMIENTAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herramientas")

ARCHIVOS_PROPIOS = {
    "cerebro": os.path.join(RUTA_CORE, "cerebro.py"),
    "emociones": os.path.join(RUTA_CORE, "emociones.py"),
    "personalidad": os.path.join(RUTA_CORE, "personalidad.py"),
    "memoria": os.path.join(RUTA_CORE, "memoria.py"),
    "orquestador": os.path.join(RUTA_CORE, "orquestador.py"),
    "plugins": os.path.join(RUTA_CORE, "plugins.py"),
    "sanacion": os.path.join(RUTA_CORE, "sanacion.py"),
    "historial_local": os.path.join(RUTA_CORE, "historial_local.py"),
    "busqueda": os.path.join(RUTA_HERRAMIENTAS, "busqueda.py"),
    "voz": os.path.join(RUTA_HERRAMIENTAS, "voz.py"),
    "monitor": os.path.join(RUTA_HERRAMIENTAS, "monitor.py"),
    "archivos": os.path.join(RUTA_HERRAMIENTAS, "archivos.py"),
    "documentos": os.path.join(RUTA_HERRAMIENTAS, "documentos.py"),
}


def leer_codigo_propio(componente: str = "cerebro", max_caracteres: int = 3000) -> dict:
    nombre = componente.lower().replace(".py", "")
    ruta = ARCHIVOS_PROPIOS.get(nombre)
    if not ruta:
        disponibles = ", ".join(sorted(ARCHIVOS_PROPIOS.keys()))
        return {"exito": False, "error": f"Componente '{componente}' no encontrado. Disponibles: {disponibles}"}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read(max_caracteres)
        return {
            "exito": True,
            "componente": nombre,
            "archivo": os.path.basename(ruta),
            "contenido": contenido,
            "total_caracteres": len(contenido),
            "truncado": len(contenido) >= max_caracteres,
        }
    except Exception as e:
        return {"exito": False, "error": str(e)}


def listar_componentes() -> dict:
    return {
        "exito": True,
        "componentes": sorted(ARCHIVOS_PROPIOS.keys()),
        "total": len(ARCHIVOS_PROPIOS),
    }
