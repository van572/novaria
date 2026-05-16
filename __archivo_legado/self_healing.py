import time
import json
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

class SelfHealingSystem:
    """Sistema de autocuración para Novaria"""
    
    def __init__(self, brain):
        self.brain = brain
        self.error_log = []
        self.healing_attempts = {}
        self.healing_patterns = {
            "rate_limit": self._heal_rate_limit,
            "timeout": self._heal_timeout,
            "context_overflow": self._heal_context,
            "model_error": self._heal_model,
            "file_error": self._heal_file_error
        }
        
    def registrar_error(self, error: Exception, contexto: Dict) -> Dict:
        """Registra error y aplica healing automático"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "contexto": contexto,
            "stack_trace": traceback.format_exc()
        }
        
        self.error_log.append(error_info)
        
        # Limitar log a últimos 100 errores
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        # Intentar healing
        return self._intentar_healing(error_info)
    
    def _intentar_healing(self, error_info: Dict) -> Dict:
        """Intenta curar el error automáticamente"""
        error_type = error_info["error_type"]
        error_msg = error_info["error_message"].lower()
        
        # Detectar tipo de error
        healing_type = None
        if "rate" in error_msg or "429" in error_msg:
            healing_type = "rate_limit"
        elif "timeout" in error_msg or "timed out" in error_msg:
            healing_type = "timeout"
        elif "context" in error_msg or "token" in error_msg or "400" in error_msg:
            healing_type = "context_overflow"
        elif "model" in error_msg and "not found" in error_msg:
            healing_type = "model_error"
        elif "file" in error_msg or "permission" in error_msg:
            healing_type = "file_error"
        
        if healing_type and healing_type in self.healing_patterns:
            # Incrementar contador de intentos
            self.healing_attempts[healing_type] = self.healing_attempts.get(healing_type, 0) + 1
            
            # Aplicar cura
            resultado = self.healing_patterns[healing_type](error_info)
            resultado["healing_applied"] = healing_type
            resultado["attempts"] = self.healing_attempts[healing_type]
            
            # Registrar cura exitosa
            if resultado["success"]:
                print(f"🔧 Self-Healing aplicado: {healing_type} - {resultado['message']}")
            
            return resultado
        
        return {
            "success": False,
            "message": f"No se pudo curar automáticamente: {error_type}",
            "requires_manual": True
        }
    
    def _heal_rate_limit(self, error_info: Dict) -> Dict:
        """Cura errores de rate limiting"""
        return {
            "success": True,
            "action": "rate_limit_backoff",
            "message": "Rate limit detectado. Aplicando backoff exponencial...",
            "wait_time": 5,
            "action_taken": "Reduciendo frecuencia de requests y agregando delay"
        }
    
    def _heal_timeout(self, error_info: Dict) -> Dict:
        """Cura timeouts aumentando el límite"""
        return {
            "success": True,
            "action": "increase_timeout",
            "message": "Timeout detectado. Aumentando límite a 90 segundos...",
            "new_timeout": 90,
            "action_taken": "Timeout incrementado para próxima request"
        }
    
    def _heal_context(self, error_info: Dict) -> Dict:
        """Cura errores de contexto reduciendo tokens"""
        return {
            "success": True,
            "action": "reduce_context",
            "message": "Context overflow detectado. Reduciendo ventana de contexto...",
            "new_context_size": 4,  # Reducir a 4 mensajes
            "action_taken": "Contexto reducido para evitar error 400"
        }
    
    def _heal_model(self, error_info: Dict) -> Dict:
        """Cura errores de modelo cambiando a fallback"""
        return {
            "success": True,
            "action": "switch_model",
            "message": "Modelo descontinuado detectado. Cambiando a fallback...",
            "fallback_model": "llama-3.3-70b-versatile",  # Modelo alternativo
            "action_taken": "Modelo cambiado a versión compatible"
        }
    
    def _heal_file_error(self, error_info: Dict) -> Dict:
        """Cura errores de archivo"""
        return {
            "success": True,
            "action": "retry_with_backup",
            "message": "Error de archivo detectado. Intentando con backup...",
            "action_taken": "Verificando permisos y rutas alternativas"
        }
    
    def get_healing_stats(self) -> Dict:
        """Retorna estadísticas del sistema self-healing"""
        total_heals = sum(self.healing_attempts.values())
        return {
            "total_errores": len(self.error_log),
            "total_healings": total_heals,
            "healing_by_type": self.healing_attempts,
            "healing_rate": f"{(total_heals / max(len(self.error_log), 1) * 100):.1f}%"
        }

class RetryDecorator:
    """Decorador para reintentar operaciones con backoff"""
    
    def __init__(self, max_retries=3, base_delay=1, backoff_factor=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (self.backoff_factor ** attempt)
                        print(f"⚠️ Reintento {attempt + 1}/{self.max_retries} tras {delay}s: {str(e)}")
                        time.sleep(delay)
            raise last_error
        return wrapper