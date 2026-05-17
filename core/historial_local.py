import os
import json
import time
import socket
import threading
from typing import Optional

_DISPOSITIVO = os.environ.get("COMPUTERNAME") or socket.gethostname() or "desconocido"

RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_HISTORIAL = os.path.join(RUTA_BASE, f"historial_chat_{_DISPOSITIVO}.json")
MAX_HISTORIAL_LOCAL = 200


class HistorialLocal:

    def __init__(self):
        self._lock = threading.Lock()
        self.ultimo_hash: str = ""
        os.makedirs(RUTA_BASE, exist_ok=True)

    def cargar(self) -> list[dict]:
        if not os.path.exists(RUTA_HISTORIAL):
            return []
        try:
            with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list):
                return datos[-MAX_HISTORIAL_LOCAL:]
        except (json.JSONDecodeError, OSError):
            return []
        return []

    def guardar(self, historial: list[dict]):
        with self._lock:
            try:
                with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
                    json.dump(historial[-MAX_HISTORIAL_LOCAL:], f, indent=2, ensure_ascii=False)
            except OSError:
                pass

    def guardar_si_cambio(self, historial: list[dict]):
        ultimo = historial[-1] if historial else {}
        hash_actual = json.dumps(ultimo, sort_keys=True, ensure_ascii=False)
        if hash_actual != self.ultimo_hash:
            self.guardar(historial)
            self.ultimo_hash = hash_actual
