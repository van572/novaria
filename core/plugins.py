import os
import re
import sys
import importlib
import importlib.util
import inspect
from typing import Any, Callable


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_PLUGINS = os.path.join(RUTA_BASE, "plugins")
RUTA_HERRAMIENTAS = os.path.join(RUTA_BASE, "herramientas")


def herramienta(nombre: str = "", descripcion: str = ""):
    def decorador(func: Callable) -> Callable:
        func._es_herramienta = True
        func._nombre_herramienta = nombre or func.__name__
        func._descripcion_herramienta = descripcion or (func.__doc__ or "").strip()
        return func
    return decorador


class GestorPlugins:

    def __init__(self):
        self.plugins: dict[str, Any] = {}
        self.herramientas: dict[str, dict] = {}
        if RUTA_PLUGINS not in sys.path:
            sys.path.insert(0, RUTA_BASE)
        self._asegurar_plugins_por_defecto()
        self._descubrir_y_cargar()

    def _asegurar_plugins_por_defecto(self):
        os.makedirs(RUTA_PLUGINS, exist_ok=True)
        init = os.path.join(RUTA_PLUGINS, "__init__.py")
        if not os.path.exists(init):
            with open(init, "w") as f:
                f.write("")

        plugin_docs = os.path.join(RUTA_PLUGINS, "plugin_documentos.py")
        if not os.path.exists(plugin_docs):
            self._escribir_plugin(
                plugin_docs,
                "PluginDocumentos",
                "herramientas.documentos",
                "GeneradorDocumentos",
                [
                    ("crear_documento", "Crea un documento DOCX con título y contenido"),
                    ("listar_documentos", "Lista los documentos DOCX disponibles"),
                ],
            )
        plugin_codigo = os.path.join(RUTA_PLUGINS, "plugin_codigo.py")
        if not os.path.exists(plugin_codigo):
            self._escribir_plugin_codigo(plugin_codigo)

    def _escribir_plugin(self, ruta: str, clase: str, importe_mod: str, importe_clase: str, herramientas_def: list[tuple[str, str]]):
        lines = [
            "import os",
            f"from {importe_mod} import {importe_clase}",
            "from core.plugins import herramienta",
            "",
            "",
            f"class {clase}:",
            "",
            "    def __init__(self):",
            f"        self.{importe_clase.lower()} = {importe_clase}()",
            "",
        ]
        for nombre_metodo, desc in herramientas_def:
            lines.extend([
                "    @herramienta(nombre=" + repr(f"{clase.lower()}.{nombre_metodo}") + ", descripcion=" + repr(desc) + ")",
                f"    def {nombre_metodo}(self, *args, **kwargs):",
                f"        return self.{importe_clase.lower()}.{nombre_metodo}(*args, **kwargs)",
                "",
            ])
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _escribir_plugin_codigo(self, ruta: str):
        contenido = r"""import os
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
"""
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido.strip() + "\n")

    def _descubrir_y_cargar(self):
        for archivo in sorted(os.listdir(RUTA_PLUGINS)):
            if not archivo.endswith(".py") or archivo == "__init__.py":
                continue
            nombre_modulo = archivo[:-3]
            try:
                modulo = importlib.import_module(f"plugins.{nombre_modulo}")
                self._cargar_plugin(modulo)
            except Exception as e:
                print(f"Error cargando plugin {nombre_modulo}: {e}")

    def _cargar_plugin(self, modulo):
        for nombre, obj in inspect.getmembers(modulo, inspect.isclass):
            if nombre.startswith("Plugin"):
                instancia = obj()
                self.plugins[nombre] = instancia
                for met_nombre, met in inspect.getmembers(instancia, inspect.ismethod):
                    if hasattr(met, "_es_herramienta") and met._es_herramienta:
                        self.herramientas[met._nombre_herramienta] = {
                            "funcion": met,
                            "descripcion": met._descripcion_herramienta,
                            "plugin": nombre,
                        }

    def obtener_todas_herramientas(self) -> dict[str, dict]:
        return dict(self.herramientas)

    def obtener_info_herramienta(self, nombre: str) -> dict:
        return self.herramientas.get(nombre, {})

    def ejecutar_herramienta(self, nombre: str, *args, **kwargs) -> dict:
        info = self.herramientas.get(nombre)
        if not info:
            return {"exito": False, "mensaje": f"Herramienta no encontrada: {nombre}"}
        try:
            resultado = info["funcion"](*args, **kwargs)
            return resultado if isinstance(resultado, dict) else {"exito": True, "resultado": resultado}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def listar_plugins(self) -> list[dict]:
        return [
            {
                "nombre": nombre,
                "herramientas": [
                    {"nombre": k, "descripcion": v["descripcion"]}
                    for k, v in self.herramientas.items()
                    if v["plugin"] == nombre
                ],
            }
            for nombre in sorted(self.plugins.keys())
        ]

    def crear_plugin(self, nombre: str, herramientas_def: list[dict]) -> dict:
        if not nombre or not herramientas_def:
            return {"exito": False, "mensaje": "Nombre y herramientas son obligatorios"}
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", nombre):
            return {"exito": False, "mensaje": "Nombre de plugin no valido (solo letras, numeros, _)"}

        nombre_clase = f"Plugin{nombre[0].upper()}{nombre[1:]}"
        nombre_archivo = f"plugin_{nombre.lower()}.py"
        ruta = os.path.join(RUTA_PLUGINS, nombre_archivo)

        lineas = [
            'import os',
            'from typing import Any',
            'from core.plugins import herramienta',
            '',
            '',
            f'class {nombre_clase}:',
            '',
            '    def __init__(self):',
            '        pass',
            '',
        ]
        for h in herramientas_def:
            h_nombre = h.get("nombre", "")
            h_desc = h.get("descripcion", "")
            h_codigo = h.get("codigo", "pass")
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', h_nombre)
            lineas.extend([
                '    @herramienta(nombre=' + repr(f"plugin_{nombre}.{h_nombre}") + ', descripcion=' + repr(h_desc) + ')',
                f'    def {safe_name}(self, *args, **kwargs) -> Any:',
                f'        {h_codigo}',
                '',
            ])

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas) + "\n")
        except Exception as e:
            return {"exito": False, "mensaje": f"Error escribiendo plugin: {e}"}

        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{nombre_archivo[:-3]}", ruta)
            if spec and spec.loader:
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                self._cargar_plugin(modulo)
        except Exception as e:
            return {"exito": False, "mensaje": f"Plugin creado pero error al cargar: {e}", "ruta": ruta}

        return {"exito": True, "mensaje": f"Plugin '{nombre}' creado y cargado", "ruta": ruta, "herramientas": len(herramientas_def)}
