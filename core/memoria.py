import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from typing import Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_MEMORIA = os.path.join(RUTA_BASE, "memory_db")
MAX_CACHE = 100
LIMITE_SUMARIO = 10
DISTANCIA_MAXIMA = 1.5
LOTE_FLUSH = 5


class SistemaMemoria:

    def __init__(self):
        os.makedirs(RUTA_MEMORIA, exist_ok=True)
        self.cliente = chromadb.PersistentClient(
            path=RUTA_MEMORIA,
            settings=Settings(anonymized_telemetry=False),
        )
        self.embeddings = self._inicializar_embeddings()
        self.colecciones = {
            nombre: self._obtener_o_crear_coleccion(nombre)
            for nombre in ("interacciones", "resumenes", "patrones_aprendidos", "documentos_academicos")
        }
        self.cache_ram: list[dict] = []
        self.pendientes: list[dict] = []
        self.inicio_sesion = time.time()
        self.contador_interacciones = 0

    @staticmethod
    def _inicializar_embeddings():
        return embedding_functions.DefaultEmbeddingFunction()

    def _obtener_o_crear_coleccion(self, nombre: str):
        try:
            return self.cliente.get_collection(nombre, embedding_function=self.embeddings)
        except (ValueError, chromadb.errors.NotFoundError):
            return self.cliente.create_collection(nombre, embedding_function=self.embeddings)

    def agregar_interaccion(self, consulta: str, respuesta: str, metadatos: Optional[dict] = None) -> dict:
        id_unico = hashlib.md5(f"{consulta}{respuesta}{time.time()}".encode()).hexdigest()
        texto = f"Usuario: {consulta}\nAsistente: {respuesta}"
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tipo": "interaccion",
            **({"contexto": json.dumps(metadatos)} if metadatos else {}),
        }

        entrada = {"texto": texto, "metadata": metadata, "id": id_unico}
        self.cache_ram.append({"consulta": consulta, "respuesta": respuesta, "id": id_unico})
        self.pendientes.append(entrada)
        if len(self.cache_ram) > MAX_CACHE:
            self.cache_ram.pop(0)

        self.contador_interacciones += 1
        if self.contador_interacciones % LIMITE_SUMARIO == 0:
            self._generar_resumen_sesion()

        if len(self.pendientes) >= LOTE_FLUSH:
            self._flush_pendientes()

        return {"exito": True, "id": id_unico}

    def _flush_pendientes(self):
        if not self.pendientes:
            return
        lote = self.pendientes[:]
        self.pendientes = []
        try:
            self.colecciones["interacciones"].add(
                documents=[e["texto"] for e in lote],
                metadatas=[e["metadata"] for e in lote],
                ids=[e["id"] for e in lote],
            )
        except Exception:
            self.pendientes = lote + self.pendientes

    def flush(self):
        self._flush_pendientes()

    def recuperar_contexto(self, consulta: str, max_resultados: int = 5) -> list[dict]:
        try:
            total = self.colecciones["interacciones"].count()
        except Exception:
            total = 0

        if total == 0 and not self.cache_ram:
            return []

        contextos = []
        if self.cache_ram:
            for item in self.cache_ram[-3:]:
                contextos.append({"texto": item["consulta"][:200], "relevancia": 0.5})

        if total > 0:
            try:
                resultados = self.colecciones["interacciones"].query(
                    query_texts=[consulta],
                    n_results=max_resultados,
                )
                if resultados.get("distances") and resultados.get("documents"):
                    metas = resultados.get("metadatas", [[]])[0]
                    for i, dist in enumerate(resultados["distances"][0]):
                        if dist < DISTANCIA_MAXIMA:
                            meta = metas[i] if i < len(metas) and metas else {}
                            contexto = {"texto": resultados["documents"][0][i][:200], "relevancia": round(1 - dist, 3)}
                            if meta.get("emocion_dominante"):
                                contexto["emocion"] = meta["emocion_dominante"]
                                contexto["intensidad_emocional"] = meta.get("intensidad_emocional", 0)
                            contextos.append(contexto)
            except Exception:
                pass

        return contextos[:max_resultados]

    def _generar_resumen_sesion(self) -> dict:
        if not self.cache_ram:
            return {"exito": False, "mensaje": "No hay interacciones para resumir"}
        resumen = "Resumen de sesión:\n" + "\n".join(
            f"- Consulta: {i['consulta'][:100]}"
            for i in self.cache_ram[-LIMITE_SUMARIO:]
        )
        id_resumen = hashlib.md5(f"resumen{time.time()}".encode()).hexdigest()
        try:
            self.colecciones["resumenes"].add(
                documents=[resumen],
                metadatas=[{"timestamp": datetime.now(timezone.utc).isoformat(), "tipo": "resumen"}],
                ids=[id_resumen],
            )
            return {"exito": True, "id": id_resumen}
        except Exception:
            return {"exito": False, "mensaje": "Error al generar resumen"}

    def aprender_patron(self, tipo: str, descripcion: str) -> dict:
        id_patron = hashlib.md5(tipo.encode()).hexdigest()
        try:
            existentes = self.colecciones["patrones_aprendidos"].get(ids=[id_patron])
            if existentes["ids"]:
                meta = existentes["metadatas"][0] if existentes["metadatas"] else {}
                confianza = min(1.0, (meta.get("confianza", 0.5) or 0.5) + 0.1)
                self.colecciones["patrones_aprendidos"].update(
                    ids=[id_patron],
                    documents=[descripcion],
                    metadatas=[{"confianza": confianza, "tipo": tipo, "ultima_actualizacion": time.time()}],
                )
            else:
                self.colecciones["patrones_aprendidos"].add(
                    documents=[descripcion],
                    metadatas=[{"confianza": 0.5, "tipo": tipo, "ultima_actualizacion": time.time()}],
                    ids=[id_patron],
                )
            return {"exito": True, "id": id_patron}
        except Exception:
            return {"exito": False, "mensaje": "Error al aprender patrón"}

    def obtener_patrones(self, tipo: Optional[str] = None, confianza_minima: float = 0.3) -> list[dict]:
        try:
            todos = self.colecciones["patrones_aprendidos"].get()
        except Exception:
            return []
        resultados = []
        for i, _ in enumerate(todos["ids"]):
            meta = todos["metadatas"][i] if todos["metadatas"] else {}
            if tipo and meta.get("tipo") != tipo:
                continue
            if (meta.get("confianza") or 0) < confianza_minima:
                continue
            resultados.append({
                "tipo": meta.get("tipo", "desconocido"),
                "descripcion": (todos["documents"][i] if todos["documents"] else "")[:200],
                "confianza": meta.get("confianza", 0),
            })
        return resultados

    def agregar_documento_academico(self, id_doc: str, nombre: str, texto: str, resumen: str):
        try:
            self.colecciones["documentos_academicos"].add(
                documents=[texto[:5000]],
                metadatas=[{"nombre": nombre, "resumen": resumen, "tipo": "pdf_academico"}],
                ids=[id_doc],
            )
        except Exception:
            pass

    def consultar_documentos_academicos(self, consulta: str, max_resultados: int = 3) -> list[dict]:
        try:
            if self.colecciones["documentos_academicos"].count() == 0:
                return []
            resultados = self.colecciones["documentos_academicos"].query(
                query_texts=[consulta],
                n_results=max_resultados,
            )
            items = []
            if resultados.get("documents"):
                for i, doc in enumerate(resultados["documents"][0]):
                    meta = resultados["metadatas"][0][i] if resultados.get("metadatas") else {}
                    dist = resultados["distances"][0][i] if resultados.get("distances") else 0
                    items.append({
                        "nombre": meta.get("nombre", ""),
                        "texto": doc[:500],
                        "resumen": meta.get("resumen", ""),
                        "relevancia": round(1 - dist, 3),
                    })
            return items
        except Exception:
            return []

    def listar_documentos_academicos(self) -> list[str]:
        try:
            todos = self.colecciones["documentos_academicos"].get()
            nombres = set()
            for meta in (todos.get("metadatas") or []):
                if meta and meta.get("nombre"):
                    nombres.add(meta["nombre"])
            return sorted(nombres)
        except Exception:
            return []

    def obtener_estadisticas(self) -> dict:
        total_interacciones = 0
        total_resumenes = 0
        total_patrones = 0
        total_academicos = 0
        try:
            total_interacciones = self.colecciones["interacciones"].count()
        except Exception:
            pass
        try:
            total_resumenes = self.colecciones["resumenes"].count()
        except Exception:
            pass
        try:
            total_patrones = self.colecciones["patrones_aprendidos"].count()
        except Exception:
            pass
        try:
            total_academicos = self.colecciones["documentos_academicos"].count()
        except Exception:
            pass
        return {
            "total_interacciones": total_interacciones + len(self.pendientes),
            "total_resumenes": total_resumenes,
            "total_patrones": total_patrones,
            "documentos_academicos": total_academicos,
            "tamano_memoria": self._calcular_tamano_memoria(),
            "duracion_sesion": round(time.time() - self.inicio_sesion, 1),
        }

    def limpiar_memorias_viejas(self, dias: int = 30) -> dict:
        try:
            self.flush()
            corte = time.time() - dias * 86400
            coleccion = self.colecciones["interacciones"]
            todos = coleccion.get()
            eliminar = []
            for i, meta in enumerate(todos["metadatas"] or []):
                ts = meta.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(ts)
                    if dt.timestamp() < corte:
                        eliminar.append(todos["ids"][i])
                except (ValueError, TypeError):
                    continue
            if eliminar:
                coleccion.delete(ids=eliminar)
            return {"exito": True, "eliminados": len(eliminar)}
        except Exception:
            return {"exito": False, "mensaje": "Error al limpiar memorias"}

    def _calcular_tamano_memoria(self) -> str:
        try:
            total = 0
            for dirpath, _, filenames in os.walk(RUTA_MEMORIA):
                for f in filenames:
                    try:
                        total += os.path.getsize(os.path.join(dirpath, f))
                    except OSError:
                        pass
            for unidad in ["B", "KB", "MB", "GB"]:
                if total < 1024:
                    return f"{total:.1f} {unidad}"
                total /= 1024
            return f"{total:.1f} TB"
        except Exception:
            return "0 B"
