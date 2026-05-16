import os
from typing import Any
from core.plugins import herramienta


RUTA_CODIGO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria", "codigo")


class PluginCodigo:

    def __init__(self):
        os.makedirs(RUTA_CODIGO, exist_ok=True)

    @herramienta(nombre="plugincodigo.analizar", descripcion="Analiza un archivo de código: líneas, funciones, clases")
    def analizar_archivo_codigo(self, ruta: str) -> dict:
        ruta_completa = os.path.join(RUTA_CODIGO, ruta)
        if not os.path.isfile(ruta_completa):
            return {"exito": False, "mensaje": f"No se encontró: {ruta}"}
        try:
            with open(ruta_completa, "r", encoding="utf-8", errors="replace") as f:
                lineas = f.readlines()
            total_lineas = len(lineas)
            funciones = sum(1 for l in lineas if l.strip().startswith("def "))
            clases = sum(1 for l in lineas if l.strip().startswith("class "))
            return {
                "exito": True,
                "archivo": ruta,
                "lineas_totales": total_lineas,
                "funciones": funciones,
                "clases": clases,
            }
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    @herramienta(nombre="plugincodigo.listar", descripcion="Lista los archivos de código disponibles")
    def listar_archivos_codigo(self) -> dict:
        if not os.path.exists(RUTA_CODIGO):
            return {"exito": True, "archivos": []}
        archivos = sorted(
            f for f in os.listdir(RUTA_CODIGO)
            if f.endswith((".py", ".js", ".ts", ".html", ".css", ".json", ".md"))
        )
        return {"exito": True, "archivos": archivos, "ruta": RUTA_CODIGO}
