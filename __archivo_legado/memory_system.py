# memory_system.py
import os
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import hashlib

class MemorySystem:
    """
    Sistema de memoria jerárquica para Novaria:
    - Memoria a corto plazo: Últimas interacciones (en brain.chat_history)
    - Memoria a largo plazo: ChromaDB vectorial con resúmenes
    - Memoria episódica: Eventos importantes y lecciones aprendidas
    """
    
    def __init__(self, persist_path: str = "./workspace_novaria/memory_db"):
        """Inicializa el sistema de memoria vectorial"""
        self.persist_path = persist_path
        os.makedirs(persist_path, exist_ok=True)
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Embedding function (modelo pequeño y eficiente para embeddings locales)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # 384 dimensiones, rápido
        )
        
        # Colecciones de memoria
        self.interactions_collection = self._get_or_create_collection(
            "interactions", 
            metadata={"description": "Conversaciones completas"}
        )
        
        self.summaries_collection = self._get_or_create_collection(
            "summaries", 
            metadata={"description": "Resúmenes de sesiones"}
        )
        
        self.learned_patterns = self._get_or_create_collection(
            "patterns", 
            metadata={"description": "Patrones y preferencias aprendidas"}
        )
        
        # Caché en memoria para acceso rápido
        self.interactions: List[Dict] = []
        self.session_start = datetime.now()
        self.max_interactions_in_memory = 100
        
        print(f"🧠 Memoria inicializada en: {persist_path}")
        print(f"   - Interacciones almacenadas: {self.interactions_collection.count()}")
        print(f"   - Resúmenes generados: {self.summaries_collection.count()}")
        print(f"   - Patrones aprendidos: {self.learned_patterns.count()}")
    
    def _get_or_create_collection(self, name: str, metadata: Dict = None):
        """Obtiene o crea una colección en ChromaDB"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata=metadata,
                embedding_function=self.embedding_fn
            )
    
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """
        Almacena una interacción en memoria a largo plazo con embedding
        
        Args:
            user_message: Mensaje del usuario
            assistant_response: Respuesta del asistente
            metadata: Metadatos adicionales (modelo usado, latencia, etc.)
        """
        timestamp = datetime.now().isoformat()
        interaction_id = hashlib.md5(f"{timestamp}{user_message[:50]}".encode()).hexdigest()[:16]
        
        # Preparar documento
        combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
        
        meta = {
            "timestamp": timestamp,
            "user_message_preview": user_message[:200] + ("..." if len(user_message) > 200 else ""),
            "assistant_response_preview": assistant_response[:200] + ("..." if len(assistant_response) > 200 else ""),
            "message_length": len(user_message),
            "response_length": len(assistant_response),
            **(metadata or {})
        }
        
        try:
            # Almacenar en ChromaDB
            self.interactions_collection.add(
                ids=[interaction_id],
                documents=[combined_text],
                metadatas=[meta]
            )
            
            # Almacenar en caché RAM
            self.interactions.append({
                "id": interaction_id,
                "user": user_message,
                "assistant": assistant_response,
                "timestamp": timestamp,
                "metadata": meta
            })
            
            # Limitar caché en RAM
            if len(self.interactions) > self.max_interactions_in_memory:
                self.interactions.pop(0)
            
            # Generar resumen periódico cada 10 interacciones
            if self.interactions_collection.count() % 10 == 0:
                self._generate_session_summary()
                
        except Exception as e:
            print(f"⚠️ Error almacenando en memoria: {e}")
    
    def retrieve_context(self, query: str, n_results: int = 5) -> List[str]:
        """
        Recupera contexto relevante de la memoria a largo plazo
        usando búsqueda semántica
        
        Args:
            query: Consulta para buscar
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de textos relevantes
        """
        if self.interactions_collection.count() == 0:
            return ["No hay memoria previa disponible."]
        
        try:
            # Buscar interacciones similares
            results = self.interactions_collection.query(
                query_texts=[query],
                n_results=min(n_results, self.interactions_collection.count())
            )
            
            if results and results['documents'] and results['documents'][0]:
                contexts = []
                for doc, distance in zip(results['documents'][0], results['distances'][0]):
                    # Solo incluir si es razonablemente relevante (distancia baja)
                    if distance < 1.5:  # Umbral de relevancia
                        # Truncar para no sobrecargar el contexto
                        truncated = doc[:300] + ("..." if len(doc) > 300 else "")
                        contexts.append(truncated)
                
                return contexts if contexts else ["No se encontró contexto relevante."]
            
        except Exception as e:
            print(f"⚠️ Error recuperando contexto: {e}")
        
        return ["No hay memoria relevante para esta consulta."]
    
    def _generate_session_summary(self):
        """Genera un resumen de la sesión actual y lo almacena"""
        if len(self.interactions) < 5:
            return
        
        # Resumen básico: últimas interacciones
        recent = self.interactions[-10:]
        
        summary_text = f"📊 Resumen de sesión ({self.session_start.strftime('%Y-%m-%d %H:%M')}):\n"
        summary_text += f"Total interacciones recientes: {len(recent)}\n\n"
        
        for i, interaction in enumerate(recent[-5:], 1):
            summary_text += f"{i}. User: {interaction['user'][:100]}...\n"
            summary_text += f"   Assistant: {interaction['assistant'][:100]}...\n\n"
        
        summary_id = f"summary_{datetime.now().strftime('%Y%m%d%H%M')}"
        
        try:
            self.summaries_collection.add(
                ids=[summary_id],
                documents=[summary_text],
                metadatas=[{
                    "timestamp": datetime.now().isoformat(),
                    "interactions_count": len(recent),
                    "session_start": self.session_start.isoformat()
                }]
            )
        except Exception as e:
            print(f"⚠️ Error generando resumen: {e}")
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict, confidence: float = 0.5):
        """
        Aprende y almacena patrones de comportamiento del usuario
        
        Args:
            pattern_type: Tipo de patrón (ej: 'tool_preference', 'topic_interest')
            pattern_data: Datos del patrón
            confidence: Nivel de confianza (0-1)
        """
        pattern_id = hashlib.md5(f"{pattern_type}{json.dumps(pattern_data)}".encode()).hexdigest()[:16]
        
        meta = {
            "pattern_type": pattern_type,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "times_observed": 1
        }
        
        # Verificar si el patrón ya existe
        existing = self.learned_patterns.get(ids=[pattern_id])
        if existing and existing['ids']:
            # Actualizar confianza
            current_conf = existing['metadatas'][0].get('confidence', 0.5)
            times_observed = existing['metadatas'][0].get('times_observed', 1) + 1
            
            # Aumentar confianza gradualmente
            new_confidence = min(1.0, (current_conf * 0.8) + (confidence * 0.2))
            
            self.learned_patterns.update(
                ids=[pattern_id],
                metadatas=[{
                    "confidence": new_confidence,
                    "times_observed": times_observed,
                    "last_updated": datetime.now().isoformat()
                }]
            )
        else:
            # Crear nuevo patrón
            self.learned_patterns.add(
                ids=[pattern_id],
                documents=[json.dumps(pattern_data)],
                metadatas=[meta]
            )
    
    def get_learned_patterns(self, pattern_type: str = None, min_confidence: float = 0.6) -> List[Dict]:
        """
        Recupera patrones aprendidos
        
        Args:
            pattern_type: Filtrar por tipo de patrón
            min_confidence: Confianza mínima requerida
            
        Returns:
            Lista de patrones aprendidos
        """
        try:
            if self.learned_patterns.count() == 0:
                return []
            
            results = self.learned_patterns.get()
            
            patterns = []
            for id_, meta, doc in zip(results['ids'], results['metadatas'], results['documents']):
                if meta.get('confidence', 0) >= min_confidence:
                    if pattern_type is None or meta.get('pattern_type') == pattern_type:
                        patterns.append({
                            "id": id_,
                            "type": meta.get('pattern_type'),
                            "confidence": meta.get('confidence'),
                            "data": json.loads(doc) if doc else {},
                            "times_observed": meta.get('times_observed', 0)
                        })
            
            return patterns
        except Exception as e:
            print(f"⚠️ Error recuperando patrones: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del sistema de memoria"""
        return {
            "total_interactions": self.interactions_collection.count(),
            "total_summaries": self.summaries_collection.count(),
            "learned_patterns": self.learned_patterns.count(),
            "memory_size_mb": self._get_memory_size(),
            "session_duration": str(datetime.now() - self.session_start).split('.')[0],
            "ram_cached_interactions": len(self.interactions)
        }
    
    def _get_memory_size(self) -> float:
        """Calcula el tamaño aproximado de la base de datos"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.persist_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)  # Convertir a MB
    
    def clear_old_memories(self, days_to_keep: int = 30):
        """Limpia memorias antiguas para optimizar espacio"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            # Obtener todas las interacciones
            all_interactions = self.interactions_collection.get()
            
            ids_to_delete = []
            for id_, meta in zip(all_interactions['ids'], all_interactions['metadatas']):
                timestamp = datetime.fromisoformat(meta['timestamp'])
                if timestamp < cutoff_date:
                    ids_to_delete.append(id_)
            
            if ids_to_delete:
                self.interactions_collection.delete(ids=ids_to_delete)
                print(f"🧹 Limpiadas {len(ids_to_delete)} interacciones antiguas")
                
        except Exception as e:
            print(f"⚠️ Error limpiando memoria: {e}")