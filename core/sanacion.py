import time
import json
import traceback
from typing import Any, Callable, Optional
from functools import wraps


MANEJADORES_ERROR = {
    "rate_limit": "limite_tasa",
    "timeout": "tiempo_agotado",
    "context_length": "longitud_contexto",
    "model_not_found": "modelo_no_encontrado",
    "authentication": "autenticacion",
    "file_not_found": "archivo_no_encontrado",
    "permission": "permiso",
    "connection": "conexion",
}


class SistemaSanacion:

    def __init__(self):
        self.bitacora_errores: list[dict] = []
        self.intentos_sanacion = 0
        self.sanaciones_exitosas = 0

    def registrar_error(self, error: str, contexto: Optional[dict] = None) -> dict:
        entrada = {
            "timestamp": time.time(),
            "error": str(error)[:500],
            "traceback": traceback.format_exc()[:1000],
            "contexto": contexto or {},
        }
        self.bitacora_errores.append(entrada)
        return self._intentar_sanacion(entrada)

    def _intentar_sanacion(self, entrada: dict) -> dict:
        self.intentos_sanacion += 1
        mensaje = entrada["error"].lower()

        if "rate" in mensaje or "429" in mensaje or "too many" in mensaje:
            return self._sanar_limite_tasa()
        elif "timeout" in mensaje or "timed out" in mensaje:
            return self._sanar_tiempo_agotado()
        elif "context" in mensaje or "length" in mensaje or "token" in mensaje:
            return self._sanar_longitud_contexto()
        elif "model" in mensaje and "not" in mensaje:
            return self._sanar_modelo()
        elif "file" in mensaje or "not found" in mensaje:
            return self._sanar_archivo()
        elif "connection" in mensaje or "refused" in mensaje or "reset" in mensaje:
            return self._sanar_conexion()
        elif "auth" in mensaje or "unauthorized" in mensaje or "401" in mensaje or "403" in mensaje:
            return self._sanar_autenticacion()

        return {
            "accion": "reportar",
            "mensaje": "No se reconoció el tipo de error. Reportando para revisión manual.",
        }

    def _sanar_limite_tasa(self) -> dict:
        self.sanaciones_exitosas += 1
        return {
            "accion": "esperar",
            "mensaje": "Límite de tasa detectado. Aplicando retroceso exponencial.",
            "espera": 5,
        }

    def _sanar_tiempo_agotado(self) -> dict:
        return {
            "accion": "reintentar",
            "mensaje": "Tiempo agotado. Reintentando con timeout extendido.",
            "timeout": 90,
        }

    def _sanar_longitud_contexto(self) -> dict:
        return {
            "accion": "reducir_contexto",
            "mensaje": "Contexto demasiado largo. Reduciendo ventana a 4 mensajes.",
            "max_mensajes": 4,
        }

    def _sanar_modelo(self) -> dict:
        return {
            "accion": "cambiar_modelo",
            "mensaje": "Modelo no disponible. Cambiando a modelo de respaldo.",
            "modelo_sugerido": "llama-3.1-8b-instant",
        }

    def _sanar_archivo(self) -> dict:
        return {
            "accion": "revisar_ruta",
            "mensaje": "Archivo no encontrado. Verificando ruta y respaldo.",
        }

    def _sanar_conexion(self) -> dict:
        return {
            "accion": "reintentar_conexion",
            "mensaje": "Error de conexión. Reintentando...",
            "espera": 3,
        }

    def _sanar_autenticacion(self) -> dict:
        return {
            "accion": "verificar_credenciales",
            "mensaje": "Error de autenticación. Verificando credenciales de API.",
        }

    def obtener_estadisticas(self) -> dict:
        total = len(self.bitacora_errores)
        tasa_exito = (self.sanaciones_exitosas / self.intentos_sanacion * 100) if self.intentos_sanacion > 0 else 0
        return {
            "total_errores": total,
            "intentos_sanacion": self.intentos_sanacion,
            "sanaciones_exitosas": self.sanaciones_exitosas,
            "tasa_exito": round(tasa_exito, 1),
            "ultimo_error": self.bitacora_errores[-1] if self.bitacora_errores else None,
        }


class DecoradorReintento:

    def __init__(self, max_reintentos: int = 3, espera_base: float = 1.0, factor_retroceso: float = 2.0):
        self.max_reintentos = max_reintentos
        self.espera_base = espera_base
        self.factor_retroceso = factor_retroceso

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def envoltura(*args, **kwargs) -> Any:
            ultimo_error = None
            for intento in range(self.max_reintentos):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ultimo_error = e
                    if intento < self.max_reintentos - 1:
                        espera = self.espera_base * (self.factor_retroceso ** intento)
                        time.sleep(espera)
            raise ultimo_error
        return envoltura
