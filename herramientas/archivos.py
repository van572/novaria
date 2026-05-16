import os
import subprocess
import shutil
from datetime import datetime
from typing import Optional


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")

COMANDOS_PELIGROSOS = [
    "rm", "del", "rd", "format", "mkfs", "dd", "shutdown", "reboot",
    "init", "poweroff", "halt", ">", ">>", "|", "sudo", "su",
    "chmod", "chown", "kill", "pkill",
]


class ManejadorArchivos:

    def __init__(self):
        self.ruta_workspace = RUTA_BASE
        self.ruta_backups = os.path.join(RUTA_BASE, "backups")
        self._ensure_directories()

    def _ensure_directories(self):
        directorios = [
            self.ruta_workspace,
            self.ruta_backups,
            os.path.join(RUTA_BASE, "documentos"),
            os.path.join(RUTA_BASE, "codigo"),
            os.path.join(RUTA_BASE, "outputs"),
            os.path.join(RUTA_BASE, "memory_db"),
            os.path.join(RUTA_BASE, "plugins"),
        ]
        for d in directorios:
            os.makedirs(d, exist_ok=True)

    def _validar_ruta(self, ruta: str) -> Optional[str]:
        if ".." in ruta.split(os.sep):
            return None
        ruta_abs = os.path.abspath(os.path.join(self.ruta_workspace, ruta))
        if not ruta_abs.startswith(os.path.abspath(self.ruta_workspace)):
            return None
        return ruta_abs

    def listar_directorio(self, ruta: str = "") -> dict:
        ruta_valida = self._validar_ruta(ruta)
        if not ruta_valida:
            return {"exito": False, "mensaje": "Ruta no válida"}
        if not os.path.exists(ruta_valida):
            return {"exito": False, "mensaje": "La ruta no existe"}
        try:
            elementos = []
            for item in sorted(os.listdir(ruta_valida)):
                ruta_item = os.path.join(ruta_valida, item)
                info = {"nombre": item, "es_directorio": os.path.isdir(ruta_item)}
                if not os.path.isdir(ruta_item):
                    info["tamano"] = self._formatear_tamano(os.path.getsize(ruta_item))
                elementos.append(info)
            return {"exito": True, "elementos": elementos, "ruta": ruta_valida}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def leer_archivo(self, ruta: str) -> dict:
        ruta_valida = self._validar_ruta(ruta)
        if not ruta_valida:
            return {"exito": False, "mensaje": "Ruta no válida"}
        if not os.path.isfile(ruta_valida):
            return {"exito": False, "mensaje": "No es un archivo válido"}
        tamano = os.path.getsize(ruta_valida)
        if tamano > 10 * 1024 * 1024:
            return {"exito": False, "mensaje": "El archivo excede 10 MB"}
        try:
            with open(ruta_valida, "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read(5000)
            return {"exito": True, "contenido": contenido, "truncado": tamano > 5000}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def leer_archivo_completo(self, ruta: str) -> dict:
        ruta_valida = self._validar_ruta(ruta)
        if not ruta_valida:
            return {"exito": False, "mensaje": "Ruta no válida"}
        if not os.path.isfile(ruta_valida):
            return {"exito": False, "mensaje": "No es un archivo válido"}
        try:
            with open(ruta_valida, "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read()
            return {"exito": True, "contenido": contenido}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def escribir_archivo(self, ruta: str, contenido: str) -> dict:
        ruta_valida = self._validar_ruta(ruta)
        if not ruta_valida:
            return {"exito": False, "mensaje": "Ruta no válida"}
        try:
            os.makedirs(os.path.dirname(ruta_valida), exist_ok=True)
            if os.path.exists(ruta_valida):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = os.path.join(
                    self.ruta_backups,
                    f"{os.path.basename(ruta_valida)}.{timestamp}.bak",
                )
                shutil.copy2(ruta_valida, backup)
            with open(ruta_valida, "w", encoding="utf-8") as f:
                f.write(contenido)
            return {"exito": True, "mensaje": f"Archivo escrito: {ruta}"}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def ejecutar_comando(self, comando: str) -> dict:
        comando_bajo = comando.lower()
        for palabra in COMANDOS_PELIGROSOS:
            if palabra in comando_bajo.split():
                return {"exito": False, "mensaje": f"Comando no permitido: {palabra}"}
        try:
            resultado = subprocess.run(
                comando, shell=True, capture_output=True, text=True, timeout=30
            )
            salida = (resultado.stdout + resultado.stderr)[:2000]
            return {"exito": True, "salida": salida, "codigo": resultado.returncode}
        except subprocess.TimeoutExpired:
            return {"exito": False, "mensaje": "Comando agotó el tiempo de espera"}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def auto_reparar(self) -> dict:
        resultados = []
        for d in [self.ruta_workspace, self.ruta_backups]:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                resultados.append(f"Directorio creado: {d}")
        archivos_criticos = [
            os.path.join(RUTA_BASE, "README.md"),
        ]
        for a in archivos_criticos:
            if not os.path.exists(a):
                with open(a, "w") as f:
                    f.write("Workspace Novaria - Reparado automáticamente\n")
                resultados.append(f"Archivo creado: {a}")
        return {"exito": True, "reparaciones": resultados}

    def obtener_estado_sistema(self) -> dict:
        total, archivos, carpetas = 0, 0, 0
        if os.path.exists(RUTA_BASE):
            for dirpath, dirnames, filenames in os.walk(RUTA_BASE):
                if "__pycache__" in dirpath or ".git" in dirpath:
                    continue
                carpetas += len(dirnames)
                archivos += len(filenames)
                for f in filenames:
                    try:
                        total += os.path.getsize(os.path.join(dirpath, f))
                    except OSError:
                        pass
        return {
            "exito": True,
            "espacio_workspace": self._formatear_tamano(total),
            "archivos": archivos,
            "directorios": carpetas,
            "salud": "ok" if os.path.exists(RUTA_BASE) else "fallo",
        }

    @staticmethod
    def _formatear_tamano(tamano: int) -> str:
        for unidad in ["B", "KB", "MB", "GB"]:
            if tamano < 1024:
                return f"{tamano:.1f} {unidad}"
            tamano /= 1024
        return f"{tamano:.1f} TB"
