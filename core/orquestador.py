import os
import json
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

import requests


RUTA_SECRETOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".streamlit", "secrets.toml")

GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_BASE = "http://localhost:11434/api/generate"
HF_BASE = "https://api-inference.huggingface.co/models/"


class ProveedorModelo(Enum):
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


@dataclass
class InfoModelo:
    nombre: str
    proveedor: ProveedorModelo
    endpoint: str
    api_key: str
    longitud_contexto: int = 4096
    costo_por_token: float = 0.0
    puntuacion_confianza: float = 0.8


def _cargar_secretos() -> dict:
    secretos = {}
    ruta = RUTA_SECRETOS
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            for linea in f:
                if "=" in linea and not linea.strip().startswith("#"):
                    k, v = linea.strip().split("=", 1)
                    secretos[k.strip()] = v.strip().strip('"').strip("'")
    return secretos


SECRETOS = _cargar_secretos()


class OrquestadorModelos:

    def __init__(self):
        self.modelos: dict[str, InfoModelo] = {}
        self.bitacora: list[dict] = []
        self._registrar_modelos_por_defecto()

    def _registrar_modelos_por_defecto(self):
        groq_key = SECRETOS.get("GROQ_KEY", os.environ.get("GROQ_KEY", ""))
        openrouter_key = SECRETOS.get("OPENROUTER_KEY", os.environ.get("OPENROUTER_KEY", ""))
        hf_token = SECRETOS.get("HF_TOKEN", os.environ.get("HF_TOKEN", ""))

        if groq_key:
            self.modelos["llama-3.1-8b-instant"] = InfoModelo(
                nombre="llama-3.1-8b-instant",
                proveedor=ProveedorModelo.GROQ,
                endpoint=GROQ_BASE,
                api_key=groq_key,
                longitud_contexto=8192,
                puntuacion_confianza=0.85,
            )
            self.modelos["mixtral-8x7b-32768"] = InfoModelo(
                nombre="mixtral-8x7b-32768",
                proveedor=ProveedorModelo.GROQ,
                endpoint=GROQ_BASE,
                api_key=groq_key,
                longitud_contexto=32768,
                costo_por_token=0.0001,
                puntuacion_confianza=0.80,
            )
        if openrouter_key:
            self.modelos["google/gemma-2-9b-it"] = InfoModelo(
                nombre="google/gemma-2-9b-it",
                proveedor=ProveedorModelo.OPENROUTER,
                endpoint=OPENROUTER_BASE,
                api_key=openrouter_key,
                longitud_contexto=8192,
                puntuacion_confianza=0.75,
            )
            self.modelos["mistralai/mixtral-8x22b-instruct"] = InfoModelo(
                nombre="mistralai/mixtral-8x22b-instruct",
                proveedor=ProveedorModelo.OPENROUTER,
                endpoint=OPENROUTER_BASE,
                api_key=openrouter_key,
                longitud_contexto=65536,
                costo_por_token=0.0002,
                puntuacion_confianza=0.70,
            )
        if self._verificar_ollama():
            modelos_ollama = self._obtener_modelos_ollama()
            for m in modelos_ollama:
                self.modelos[m] = InfoModelo(
                    nombre=m,
                    proveedor=ProveedorModelo.OLLAMA,
                    endpoint=OLLAMA_BASE,
                    api_key="",
                    longitud_contexto=4096,
                    puntuacion_confianza=0.60,
                )
        if hf_token:
            self.modelos["mistralai/Mistral-7B-Instruct-v0.3"] = InfoModelo(
                nombre="mistralai/Mistral-7B-Instruct-v0.3",
                proveedor=ProveedorModelo.HUGGINGFACE,
                endpoint=HF_BASE + "mistralai/Mistral-7B-Instruct-v0.3",
                api_key=hf_token,
                longitud_contexto=4096,
                puntuacion_confianza=0.50,
            )

    @staticmethod
    def _verificar_ollama() -> bool:
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    @staticmethod
    def _obtener_modelos_ollama() -> list[str]:
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                return [m["name"] for m in resp.json().get("models", [])]
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            pass
        return []

    def registrar_modelo(self, nombre: str, info: InfoModelo):
        self.modelos[nombre] = info

    def seleccionar_mejor_modelo(self, complejidad: str = "media", longitud_contexto: int = 0) -> Optional[str]:
        candidatos = sorted(
            self.modelos.values(),
            key=lambda m: (
                m.puntuacion_confianza,
                m.longitud_contexto if longitud_contexto > 0 else 0,
                -m.costo_por_token,
            ),
            reverse=True,
        )
        if complejidad == "simple":
            for m in candidatos:
                if m.longitud_contexto >= 2048:
                    return m.nombre
        elif complejidad == "alta":
            for m in candidatos:
                if m.longitud_contexto >= max(longitud_contexto, 8192):
                    return m.nombre
        for m in candidatos:
            if m.longitud_contexto >= max(longitud_contexto, 2048):
                return m.nombre
        return candidatos[0].nombre if candidatos else None

    def ejecutar_con_respaldo(self, mensajes: list[dict], complejidad: str = "media") -> dict:
        longitud = sum(len(m.get("content", "")) for m in mensajes)
        modelo_principal = self.seleccionar_mejor_modelo(complejidad, longitud)

        intentos = []
        orden = [modelo_principal] if modelo_principal else []
        orden += [
            m.nombre for m in sorted(
                self.modelos.values(), key=lambda x: x.puntuacion_confianza, reverse=True
            )
            if m.nombre != modelo_principal
        ]
        orden = orden[:3]

        for i, nombre_modelo in enumerate(orden):
            info = self.modelos.get(nombre_modelo)
            if not info:
                continue
            inicio = time.time()
            resultado = self._llamar_modelo(info, mensajes)
            duracion = time.time() - inicio
            exito = resultado.get("exito", False)

            self._actualizar_puntuacion(nombre_modelo, exito, duracion)
            intentos.append({
                "modelo": nombre_modelo,
                "exito": exito,
                "duracion": round(duracion, 2),
            })

            if exito:
                self.bitacora.append({
                    "timestamp": time.time(),
                    "modelo": nombre_modelo,
                    "exito": True,
                    "duracion": round(duracion, 2),
                })
                return {
                    "exito": True,
                    "respuesta": resultado["respuesta"],
                    "modelo": nombre_modelo,
                    "intentos": intentos,
                }
            if i < len(orden) - 1:
                time.sleep(1)

        for intento in intentos:
            self.bitacora.append({
                "timestamp": time.time(),
                "modelo": intento["modelo"],
                "exito": False,
                "duracion": intento["duracion"],
            })
        return {"exito": False, "mensaje": "Todos los modelos fallaron", "intentos": intentos}

    def _llamar_modelo(self, info: InfoModelo, mensajes: list[dict]) -> dict:
        try:
            if info.proveedor in (ProveedorModelo.GROQ, ProveedorModelo.OPENROUTER):
                return self._llamar_api_chat(info, mensajes)
            elif info.proveedor == ProveedorModelo.OLLAMA:
                return self._llamar_ollama(info, mensajes)
            elif info.proveedor == ProveedorModelo.HUGGINGFACE:
                return self._llamar_huggingface(info, mensajes)
            return {"exito": False, "mensaje": f"Proveedor desconocido: {info.proveedor}"}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    def _llamar_api_chat(self, info: InfoModelo, mensajes: list[dict]) -> dict:
        headers = {
            "Authorization": f"Bearer {info.api_key}",
            "Content-Type": "application/json",
        }
        if info.proveedor == ProveedorModelo.OPENROUTER:
            headers["HTTP-Referer"] = "https://novaria.app"
            headers["X-Title"] = "Novaria"

        payload = {
            "model": info.nombre,
            "messages": mensajes,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        resp = requests.post(info.endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        contenido = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"exito": True, "respuesta": contenido}

    def _llamar_ollama(self, info: InfoModelo, mensajes: list[dict]) -> dict:
        prompt = "\n".join(
            f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
            for m in mensajes[-6:]
        )
        payload = {"model": info.nombre, "prompt": prompt, "stream": False}
        resp = requests.post(info.endpoint, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return {"exito": True, "respuesta": data.get("response", "")}

    def _llamar_huggingface(self, info: InfoModelo, mensajes: list[dict]) -> dict:
        ultimo = mensajes[-1]["content"] if mensajes else ""
        prompt = f"<s>[INST] {ultimo} [/INST]"
        headers = {"Authorization": f"Bearer {info.api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1024, "temperature": 0.7}}
        resp = requests.post(info.endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        texto = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
        respuesta = texto.replace(prompt, "").strip()
        return {"exito": True, "respuesta": respuesta}

    def llamar_modelo_especifico(self, nombre_modelo: str, mensajes: list[dict], temperature: float = 0.7, max_tokens: int = 2048, frequency_penalty: float = 0.0, presence_penalty: float = 0.0) -> dict:
        info = self.modelos.get(nombre_modelo)
        if not info:
            return {"exito": False, "mensaje": f"Modelo '{nombre_modelo}' no registrado", "modelo": nombre_modelo}
        try:
            if info.proveedor in (ProveedorModelo.GROQ, ProveedorModelo.OPENROUTER):
                headers = {
                    "Authorization": f"Bearer {info.api_key}",
                    "Content-Type": "application/json",
                }
                if info.proveedor == ProveedorModelo.OPENROUTER:
                    headers["HTTP-Referer"] = "https://novaria.app"
                    headers["X-Title"] = "Novaria"
                payload = {
                    "model": info.nombre,
                    "messages": mensajes,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "frequency_penalty": frequency_penalty,
                    "presence_penalty": presence_penalty,
                }
                resp = requests.post(info.endpoint, headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                contenido = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not contenido or not contenido.strip():
                    return {"exito": False, "mensaje": "Respuesta vacia del modelo", "modelo": nombre_modelo}
                self._actualizar_puntuacion(nombre_modelo, True, 0)
                return {"exito": True, "respuesta": contenido, "modelo": nombre_modelo}
            elif info.proveedor == ProveedorModelo.OLLAMA:
                prompt = "\n".join(
                    f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                    for m in mensajes[-6:]
                )
                payload = {"model": info.nombre, "prompt": prompt, "stream": False}
                resp = requests.post(info.endpoint, json=payload, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                contenido = data.get("response", "")
                if not contenido or not contenido.strip():
                    return {"exito": False, "mensaje": "Respuesta vacia del modelo", "modelo": nombre_modelo}
                self._actualizar_puntuacion(nombre_modelo, True, 0)
                return {"exito": True, "respuesta": contenido, "modelo": nombre_modelo}
            elif info.proveedor == ProveedorModelo.HUGGINGFACE:
                ultimo = mensajes[-1]["content"] if mensajes else ""
                prompt = f"<s>[INST] {ultimo} [/INST]"
                headers = {"Authorization": f"Bearer {info.api_key}"}
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": temperature}}
                resp = requests.post(info.endpoint, headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                texto = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
                contenido = texto.replace(prompt, "").strip()
                if not contenido:
                    return {"exito": False, "mensaje": "Respuesta vacia del modelo", "modelo": nombre_modelo}
                self._actualizar_puntuacion(nombre_modelo, True, 0)
                return {"exito": True, "respuesta": contenido, "modelo": nombre_modelo}
            return {"exito": False, "mensaje": f"Proveedor desconocido: {info.proveedor}", "modelo": nombre_modelo}
        except requests.exceptions.Timeout:
            self._actualizar_puntuacion(nombre_modelo, False, 0)
            return {"exito": False, "mensaje": "Timeout en la llamada al modelo", "modelo": nombre_modelo}
        except requests.exceptions.HTTPError as e:
            self._actualizar_puntuacion(nombre_modelo, False, 0)
            return {"exito": False, "mensaje": f"HTTP {e.response.status_code}: {e.response.text[:200]}", "modelo": nombre_modelo}
        except Exception as e:
            self._actualizar_puntuacion(nombre_modelo, False, 0)
            return {"exito": False, "mensaje": str(e)[:200], "modelo": nombre_modelo}

    def _actualizar_puntuacion(self, nombre_modelo: str, exito: bool, duracion: float):
        info = self.modelos.get(nombre_modelo)
        if not info:
            return
        if exito:
            bonus = 0.05 if duracion < 5 else 0.02
            info.puntuacion_confianza = min(1.0, info.puntuacion_confianza + bonus)
        else:
            info.puntuacion_confianza *= 0.9

    def obtener_modelos_disponibles(self) -> list[dict]:
        return [
            {
                "nombre": m.nombre,
                "proveedor": m.proveedor.value,
                "confianza": round(m.puntuacion_confianza, 3),
                "contexto": m.longitud_contexto,
            }
            for m in sorted(self.modelos.values(), key=lambda x: x.puntuacion_confianza, reverse=True)
        ]

    def obtener_estadisticas(self) -> dict:
        if not self.bitacora:
            return {"total_llamadas": 0, "tasa_exito": 0, "mejor_modelo": "N/A"}
        total = len(self.bitacora)
        exitos = sum(1 for b in self.bitacora if b["exito"])
        mejor = max(self.modelos.items(), key=lambda x: x[1].puntuacion_confianza)[0]
        return {
            "total_llamadas": total,
            "tasa_exito": round(exitos / total * 100, 1) if total > 0 else 0,
            "mejor_modelo": mejor,
            "modelos_disponibles": len(self.modelos),
        }
