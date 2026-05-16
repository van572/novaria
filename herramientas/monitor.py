import os
import threading
import time
from dataclasses import dataclass, field


try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


MAX_WORKERS = 4
RAM_MINIMO_MB = 512
CPU_MAX_PORCENTAJE = 90


@dataclass
class EstadoRecursos:
    ram_disponible_mb: float = 0
    ram_porcentaje: float = 0
    cpu_porcentaje: float = 0
    workers_recomendados: int = MAX_WORKERS
    throttle_mode: bool = False
    alerta: str = ""


class MonitorRecursos:

    def __init__(self):
        self.ultima_lectura = 0.0
        self.cache = EstadoRecursos()
        self.intervalo = 2.0
        self._lock = threading.Lock()

    def leer(self) -> EstadoRecursos:
        ahora = time.time()
        if ahora - self.ultima_lectura < self.intervalo:
            return self.cache
        self.ultima_lectura = ahora
        estado = EstadoRecursos()
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                estado.ram_disponible_mb = mem.available / (1024 * 1024)
                estado.ram_porcentaje = mem.percent
                estado.cpu_porcentaje = psutil.cpu_percent(interval=0.3)
                if estado.ram_disponible_mb < RAM_MINIMO_MB:
                    estado.throttle_mode = True
                    estado.workers_recomendados = 1
                    estado.alerta = f"RAM baja: {estado.ram_disponible_mb:.0f}MB"
                elif estado.cpu_porcentaje > CPU_MAX_PORCENTAJE:
                    estado.throttle_mode = True
                    estado.workers_recomendados = max(1, MAX_WORKERS // 2)
                    estado.alerta = f"CPU alta: {estado.cpu_porcentaje}%"
                else:
                    estado.workers_recomendados = MAX_WORKERS
            except Exception:
                pass
        with self._lock:
            self.cache = estado
        return estado

    def obtener_parametros_adaptados(self) -> dict:
        estado = self.leer()
        params = {
            "max_workers": estado.workers_recomendados,
            "max_tokens": 512 if estado.throttle_mode else 2048,
            "temperature_range": (0.2, 0.7) if estado.throttle_mode else (0.3, 0.9),
        }
        return params

    def formatear_para_prompt(self) -> str:
        estado = self.leer()
        if not HAS_PSUTIL:
            return ""
        return (
            f"[Recursos: RAM {estado.ram_disponible_mb:.0f}MB libre "
            f"({estado.ram_porcentaje}%), "
            f"CPU {estado.cpu_porcentaje}%]"
            + (f" | {estado.alerta}" if estado.alerta else "")
        )
