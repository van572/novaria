# model_orchestrator.py
import os
import time
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"

@dataclass
class ModelInfo:
    name: str
    provider: ModelProvider
    endpoint: str
    api_key: Optional[str] = None
    context_length: int = 4096
    cost_per_token: float = 0.0
    reliability_score: float = 1.0  # RLHF: se ajusta con feedback

class ModelOrchestrator:
    """Orquestador multi-modelo con failover inteligente y aprendizaje"""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._register_default_models()
        self.performance_log: List[Dict] = []
        
    def _register_default_models(self):
        """Registra modelos open-source y propietarios disponibles"""
        
        # 1. Groq (Principal)
        groq_key = os.getenv("GROQ_KEY")
        if groq_key:
            self.register_model(ModelInfo(
                name="llama-3.1-8b-instant",
                provider=ModelProvider.GROQ,
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                context_length=8192,
                cost_per_token=0.05
            ))
            self.register_model(ModelInfo(
                name="mixtral-8x7b-32768",
                provider=ModelProvider.GROQ,
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                context_length=32768,
                cost_per_token=0.27
            ))
        
        # 2. OpenRouter (Acceso a 100+ modelos)
        openrouter_key = os.getenv("OPENROUTER_KEY")
        if openrouter_key:
            self.register_model(ModelInfo(
                name="google/gemma-7b-it:free",
                provider=ModelProvider.OPENROUTER,
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                api_key=openrouter_key,
                context_length=8192,
                cost_per_token=0.0  # Modelo gratuito
            ))
            self.register_model(ModelInfo(
                name="mistralai/mixtral-8x22b-instruct",
                provider=ModelProvider.OPENROUTER,
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                api_key=openrouter_key,
                context_length=65536,
                cost_per_token=0.65
            ))
        
        # 3. Ollama (Local - Máxima autonomía)
        if self._check_ollama():
            local_models = self._get_ollama_models()
            for model in local_models:
                self.register_model(ModelInfo(
                    name=f"local/{model}",
                    provider=ModelProvider.OLLAMA,
                    endpoint=f"http://localhost:11434/api/generate",
                    context_length=4096,  # Ollama puede manejar más
                    cost_per_token=0.0
                ))
        
        # 4. Hugging Face Inference API
        hf_key = os.getenv("HF_TOKEN")
        if hf_key:
            self.register_model(ModelInfo(
                name="mistralai/Mistral-7B-Instruct-v0.2",
                provider=ModelProvider.HUGGINGFACE,
                endpoint="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                api_key=hf_key,
                context_length=32000
            ))
    
    def _check_ollama(self) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_ollama_models(self) -> List[str]:
        try:
            response = requests.get("http://localhost:11434/api/tags")
            return [m['name'] for m in response.json()['models']]
        except:
            return []
    
    def register_model(self, model: ModelInfo):
        self.models[model.name] = model
    
    def select_best_model(self, task_complexity: str = "medium", max_tokens: int = 4000) -> ModelInfo:
        """Selecciona el mejor modelo basado en la tarea y aprendizaje (RLHF)"""
        
        # Filtrar modelos que soporten el contexto necesario
        suitable = [m for m in self.models.values() if m.context_length >= max_tokens]
        if not suitable:
            suitable = list(self.models.values())
        
        # Priorizar por:
        # 1. Puntuación de fiabilidad (aprendida)
        # 2. Costo (preferir locales/gratuitos para tareas simples)
        # 3. Contexto disponible
        
        if task_complexity == "simple":
            # Preferir modelos locales/gratuitos
            suitable.sort(key=lambda m: (m.reliability_score * -1, m.cost_per_token))
        else:
            # Preferir modelos potentes y confiables
            suitable.sort(key=lambda m: (m.reliability_score * -1, m.context_length * -1))
        
        return suitable[0] if suitable else list(self.models.values())[0]
    
    def execute_with_fallback(self, 
                              messages: List[Dict], 
                              max_tokens: int = 4000,
                              temperature: float = 0.7,
                              complexity: str = "medium") -> Dict[str, Any]:
        """Ejecuta con fallback automático entre modelos"""
        
        primary_model = self.select_best_model(complexity, max_tokens)
        fallback_models = [m for m in self.models.values() if m.name != primary_model.name]
        fallback_models.sort(key=lambda m: m.reliability_score, reverse=True)
        
        attempt_models = [primary_model] + fallback_models[:2]  # Intentar hasta 3 modelos
        
        last_error = None
        for model in attempt_models:
            try:
                start_time = time.time()
                response = self._call_model(model, messages, max_tokens, temperature)
                latency = time.time() - start_time
                
                # Registrar éxito para RLHF
                self._update_model_score(model.name, success=True, latency=latency)
                
                return {
                    "success": True,
                    "content": response,
                    "model_used": model.name,
                    "provider": model.provider.value,
                    "latency": latency
                }
                
            except Exception as e:
                last_error = str(e)
                self._update_model_score(model.name, success=False)
                continue
        
        return {
            "success": False,
            "error": f"Todos los modelos fallaron: {last_error}",
            "models_tried": [m.name for m in attempt_models]
        }
    
    def _call_model(self, model: ModelInfo, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Llama a un modelo específico según su proveedor"""
        
        if model.provider == ModelProvider.GROQ:
            return self._call_groq(model, messages, max_tokens, temperature)
        elif model.provider == ModelProvider.OPENROUTER:
            return self._call_openrouter(model, messages, max_tokens, temperature)
        elif model.provider == ModelProvider.OLLAMA:
            return self._call_ollama(model, messages, max_tokens, temperature)
        elif model.provider == ModelProvider.HUGGINGFACE:
            return self._call_huggingface(model, messages, max_tokens, temperature)
        else:
            raise ValueError(f"Proveedor no soportado: {model.provider}")
    
    def _call_groq(self, model: ModelInfo, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        headers = {"Authorization": f"Bearer {model.api_key}", "Content-Type": "application/json"}
        data = {
            "model": model.name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = requests.post(model.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_openrouter(self, model: ModelInfo, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "HTTP-Referer": "https://novaria.ai",
            "X-Title": "Novaria Assistant"
        }
        data = {
            "model": model.name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = requests.post(model.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_ollama(self, model: ModelInfo, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        # Formatear mensajes para Ollama
        prompt = ""
        for msg in messages:
            if msg['role'] == 'system':
                prompt += f"System: {msg['content']}\n\n"
            elif msg['role'] == 'user':
                prompt += f"User: {msg['content']}\n\n"
            elif msg['role'] == 'assistant':
                prompt += f"Assistant: {msg['content']}\n\n"
        
        data = {
            "model": model.name.replace("local/", ""),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        response = requests.post(model.endpoint, json=data, timeout=120)
        response.raise_for_status()
        return response.json()['response']
    
    def _call_huggingface(self, model: ModelInfo, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        headers = {"Authorization": f"Bearer {model.api_key}"}
        # Formatear como prompt simple
        prompt = messages[-1]['content'] if messages else ""
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        response = requests.post(model.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()[0]['generated_text']
    
    def _update_model_score(self, model_name: str, success: bool, latency: float = 0):
        """Actualiza puntuación de fiabilidad del modelo (RLHF)"""
        if model_name in self.models:
            model = self.models[model_name]
            if success:
                # Recompensa por éxito: aumentar fiabilidad, bonificar baja latencia
                latency_bonus = max(0, (5.0 - min(latency, 5.0)) / 5.0) * 0.05  # Hasta 0.05 extra
                model.reliability_score = min(1.0, model.reliability_score * 0.95 + 0.05 + latency_bonus)
            else:
                # Penalización por fallo
                model.reliability_score *= 0.9
        
        self.performance_log.append({
            "timestamp": time.time(),
            "model": model_name,
            "success": success,
            "latency": latency,
            "new_score": self.models[model_name].reliability_score if model_name in self.models else 0
        })
    
    def get_available_models(self) -> List[Dict]:
        return [
            {
                "name": m.name,
                "provider": m.provider.value,
                "context": m.context_length,
                "cost": m.cost_per_token,
                "reliability": f"{m.reliability_score:.2f}"
            }
            for m in self.models.values()
        ]