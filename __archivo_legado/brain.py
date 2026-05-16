# brain.py (Versión 6.0 - Multi-modelo Cloud + Memoria + Plugins)
import os
import json
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

# Importar componentes
from auto_evolucion import AutoEvolucion
from model_orchestrator import ModelOrchestrator
from memory_system import MemorySystem
from plugin_manager import PluginManager

class NovariaBrain:
    """
    Novaria v6.0 - Cerebro multi-modelo con memoria persistente
    Usa EXCLUSIVAMENTE modelos en la nube (Groq, OpenRouter, HuggingFace)
    """
    
    def __init__(self):
        print("=" * 60)
        print("🧠 NOVARIA v6.0 - ARQUITECTURA MULTI-MODELO CLOUD")
        print("=" * 60)
        
        # Inicializar componentes core
        self.evolucion = AutoEvolucion(self)
        self.orchestrator = ModelOrchestrator()
        self.memory = MemorySystem()
        self.plugin_manager = PluginManager(self.evolucion.workspace)
        
        # Sistema de herramientas unificado
        self.tools = self._build_unified_tools()
        
        # Estado y métricas
        self.corriendo = True
        self.estado_actual = "🟢 Inicializando..."
        self.historial_chat: List[Dict] = []
        
        self.metricas = {
            "consultas_totales": 0,
            "herramientas_ejecutadas": 0,
            "modelos_utilizados": {},
            "plugins_utilizados": {},
            "memoria_interacciones": 0,
            "tiempo_promedio_respuesta": 0.0,
            "tiempos_respuesta": []
        }
        
        # Sistema de auto-aprendizaje
        self.preferencias_usuario = {
            "modelo_preferido": None,
            "formato_respuesta": "detallado",
            "tareas_frecuentes": []
        }
        
        # Auto-diagnóstico inicial
        self._run_initial_diagnostics()
        
        print(f"\n✅ Modelos disponibles: {len(self.orchestrator.models)}")
        print(f"✅ Herramientas registradas: {len(self.tools)}")
        print(f"✅ Plugins cargados: {len(self.plugin_manager.plugins)}")
        print(f"✅ Memoria: {self.memory.get_stats()['total_interactions']} interacciones previas")
        print("=" * 60 + "\n")
    
    def _build_unified_tools(self) -> Dict:
        """Construye el registro unificado de herramientas"""
        tools = {
            # Herramientas base
            "listar_directorio": self.evolucion.listar_directorio,
            "leer_archivo": self.evolucion.leer_archivo,
            "leer_archivo_completo": self.evolucion.leer_archivo_completo,
            "escribir_archivo": self.evolucion.escribir_archivo,
            "ejecutar_comando": self.evolucion.ejecutar_comando,
            "auto_reparar": self.evolucion.auto_reparar,
            "estado_sistema": self.evolucion.get_estado_sistema,
        }
        
        # Agregar herramientas de plugins
        plugin_tools = self.plugin_manager.get_all_tools()
        tools.update(plugin_tools)
        
        # Agregar herramientas de memoria
        tools["buscar_en_memoria"] = self.memory.retrieve_context
        tools["estadisticas_memoria"] = self.memory.get_stats
        
        return tools
    
    def _run_initial_diagnostics(self):
        """Ejecuta diagnóstico inicial del sistema"""
        try:
            self.estado_actual = "🔍 Ejecutando diagnóstico..."
            
            # Verificar modelos disponibles
            modelos_disponibles = self.orchestrator.get_available_models()
            if not modelos_disponibles:
                print("⚠️ ADVERTENCIA: No se detectaron modelos en la nube")
                print("   Configure al menos una API key (GROQ_KEY, OPENROUTER_KEY o HF_TOKEN)")
            
            # Auto-reparar si es necesario
            diagnostico = self.evolucion.auto_reparar()
            if diagnostico["total_reparaciones"] > 0:
                print(f"🔧 Auto-reparaciones realizadas: {diagnostico['total_reparaciones']}")
            
            self.estado_actual = "✅ Listo"
            
        except Exception as e:
            print(f"⚠️ Error en diagnóstico inicial: {e}")
            self.estado_actual = "⚠️ Operando con capacidades reducidas"
    
    def procesar_mensaje(self, mensaje_usuario: str) -> str:
        """
        Procesa un mensaje del usuario usando la arquitectura completa:
        1. Detección rápida de comandos
        2. Recuperación de contexto de memoria
        3. Selección del mejor modelo cloud
        4. Ejecución de herramientas
        5. Aprendizaje y almacenamiento
        """
        inicio_tiempo = time.time()
        self.metricas["consultas_totales"] += 1
        self.estado_actual = "🔄 Procesando..."
        
        # 1. Añadir a historial
        self.historial_chat.append({"role": "user", "content": mensaje_usuario})
        
        # 2. Intentar detección directa de comandos (ahorra API calls)
        resultado_directo = self._procesar_comando_directo(mensaje_usuario)
        if resultado_directo:
            self._finalizar_procesamiento(resultado_directo, inicio_tiempo)
            return resultado_directo
        
        # 3. Recuperar contexto relevante de la memoria
        contextos = self.memory.retrieve_context(mensaje_usuario, n_results=3)
        
        # 4. Determinar complejidad de la tarea
        complejidad = self._estimar_complejidad(mensaje_usuario)
        
        # 5. Construir prompt del sistema
        prompt_sistema = self._construir_prompt_sistema(contextos)
        
        # 6. Preparar mensajes para el modelo
        mensajes_modelo = [
            {"role": "system", "content": prompt_sistema},
            *self.historial_chat[-8:]  # Últimos 8 mensajes
        ]
        
        # 7. Ejecutar con orquestador multi-modelo
        respuesta_modelo = self.orchestrator.execute_with_fallback(
            messages=mensajes_modelo,
            max_tokens=4000,
            temperature=0.3,
            complexity=complejidad
        )
        
        # 8. Procesar respuesta
        if respuesta_modelo.get("success"):
            contenido = respuesta_modelo["content"]
            
            # Intentar extraer y ejecutar herramientas
            accion = self._extraer_accion_json(contenido)
            
            if accion:
                # Ejecutar herramienta
                resultado_herramienta = self._ejecutar_herramienta(accion)
                
                if resultado_herramienta.get("success"):
                    respuesta_final = resultado_herramienta.get("message", "✅ Acción completada")
                else:
                    respuesta_final = resultado_herramienta.get("message", contenido)
            else:
                respuesta_final = contenido
            
            # Registrar modelo usado
            modelo = respuesta_modelo.get("model_used", "desconocido")
            self.metricas["modelos_utilizados"][modelo] = self.metricas["modelos_utilizados"].get(modelo, 0) + 1
            
        else:
            # Fallback: intentar responder basado en herramientas si el modelo falla
            respuesta_final = self._generar_respuesta_fallback(mensaje_usuario)
        
        # 9. Almacenar en memoria y aprender
        self.memory.add_interaction(
            mensaje_usuario, 
            respuesta_final,
            metadata={
                "modelo": respuesta_modelo.get("model_used", "fallback"),
                "complejidad": complejidad,
                "tiempo": time.time() - inicio_tiempo
            }
        )
        
        # Aprender patrones
        self._aprender_de_interaccion(mensaje_usuario, respuesta_final)
        
        # Finalizar
        self._finalizar_procesamiento(respuesta_final, inicio_tiempo)
        return respuesta_final
    
    def _procesar_comando_directo(self, mensaje: str) -> Optional[str]:
        """Detecta y ejecuta comandos directos sin necesidad de LLM"""
        mensaje_lower = mensaje.lower().strip()
        
        # Comandos de sistema
        if mensaje_lower in ["estado", "status", "diagnóstico"]:
            estado = self.evolucion.get_estado_sistema()
            return f"📊 Estado del sistema:\n" + "\n".join(f"  {k}: {v}" for k, v in estado.items())
        
        if mensaje_lower in ["memoria", "memory"]:
            stats = self.memory.get_stats()
            return f"🧠 Estado de la memoria:\n" + "\n".join(f"  {k}: {v}" for k, v in stats.items())
        
        if mensaje_lower in ["modelos", "models"]:
            modelos = self.orchestrator.get_available_models()
            return "🤖 Modelos disponibles:\n" + "\n".join(
                f"  - {m['name']} ({m['provider']}) [Fiabilidad: {m['reliability']}]"
                for m in modelos
            )
        
        if mensaje_lower in ["plugins", "herramientas"]:
            plugins = self.plugin_manager.list_plugins()
            return "🔌 Plugins cargados:\n" + "\n".join(
                f"  - {p['name']} ({p['tools_count']} herramientas)"
                for p in plugins
            )
        
        if mensaje_lower in ["ayuda", "help", "?"]:
            return self._generar_ayuda()
        
        # Comandos de navegación
        if mensaje_lower.startswith("ls ") or mensaje_lower.startswith("dir "):
            parts = mensaje.split(" ", 1)
            ruta = parts[1] if len(parts) > 1 else "."
            return self.evolucion.listar_directorio(ruta)
        
        if mensaje_lower.startswith("leer "):
            archivo = mensaje_lower[5:].strip()
            return self.evolucion.leer_archivo(archivo)
        
        return None
    
    def _estimar_complejidad(self, mensaje: str) -> str:
        """Estima la complejidad de la tarea para seleccionar el mejor modelo"""
        mensaje_lower = mensaje.lower()
        
        # Alta complejidad
        keywords_alta = [
            "analiza", "optimiza", "refactoriza", "debug", "bug",
            "explica en detalle", "arquitectura", "diseña", "complejo",
            "algoritmo", "eficiencia", "rendimiento"
        ]
        if any(kw in mensaje_lower for kw in keywords_alta) or len(mensaje) > 800:
            return "high"
        
        # Complejidad media
        keywords_media = [
            "crea", "genera", "escribe", "modifica", "actualiza",
            "busca", "encuentra", "lista", "organiza"
        ]
        if any(kw in mensaje_lower for kw in keywords_media) or len(mensaje) > 300:
            return "medium"
        
        return "simple"
    
    def _construir_prompt_sistema(self, contextos: List[str]) -> str:
        """Construye el prompt del sistema con contexto y herramientas"""
        
        # Descripción de herramientas
        herramientas_desc = []
        for nombre, funcion in list(self.tools.items())[:10]:  # Top 10 herramientas
            doc = (funcion.__doc__ or "Sin descripción").split('\n')[0]
            herramientas_desc.append(f"  - {nombre}: {doc}")
        
        prompt = f"""Eres Novaria, un asistente de IA avanzado con capacidades multi-modelo.

📚 CONTEXTO DE MEMORIA:
{chr(10).join(f"  {i+1}. {ctx}" for i, ctx in enumerate(contextos)) if contextos else "  No hay contexto previo relevante."}

🔧 HERRAMIENTAS DISPONIBLES:
{chr(10).join(herramientas_desc)}

📋 REGLAS:
1. Para usar una herramienta, responde SOLO con JSON: {{"accion": "nombre_herramienta", "argumentos": {{"param": "valor"}}}}
2. Para crear documentos Word usa: {{"accion": "crear_documento_docx", "argumentos": {{"titulo": "...", "contenido": "..."}}}}
3. Sé preciso y útil. Incluye ejemplos cuando sea relevante.
4. Si no estás seguro, sé honesto y sugiere alternativas.

🤖 MODELOS: Tengo acceso a múltiples modelos en la nube (Groq, OpenRouter, HuggingFace)
   El sistema selecciona automáticamente el mejor para cada tarea."""
        
        return prompt
    
    def _extraer_accion_json(self, texto: str) -> Optional[Dict]:
        """Extrae una acción JSON de la respuesta del modelo"""
        if not texto:
            return None
        
        # Buscar JSON en la respuesta
        patrones = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^{}]*"accion"[^{}]*\})',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if "accion" in data:
                        return data
                except:
                    continue
        
        # Intentar si todo el texto es JSON
        try:
            data = json.loads(texto.strip())
            if "accion" in data:
                return data
        except:
            pass
        
        return None
    
    def _ejecutar_herramienta(self, accion: Dict) -> Dict:
        """Ejecuta una herramienta del registro"""
        nombre_herramienta = accion.get("accion")
        argumentos = accion.get("argumentos", {})
        
        if nombre_herramienta in self.tools:
            try:
                self.metricas["herramientas_ejecutadas"] += 1
                self.metricas["plugins_utilizados"][nombre_herramienta] = \
                    self.metricas["plugins_utilizados"].get(nombre_herramienta, 0) + 1
                
                resultado = self.tools[nombre_herramienta](**argumentos)
                
                if isinstance(resultado, dict):
                    return resultado
                else:
                    return {"success": True, "message": str(resultado)}
                    
            except Exception as e:
                return {
                    "success": False,
                    "message": f"❌ Error ejecutando {nombre_herramienta}: {str(e)}"
                }
        
        return {
            "success": False,
            "message": f"❌ Herramienta '{nombre_herramienta}' no encontrada"
        }
    
    def _generar_respuesta_fallback(self, mensaje: str) -> str:
        """Genera una respuesta básica cuando todos los modelos fallan"""
        mensaje_lower = mensaje.lower()
        
        if "crea" in mensaje_lower and "documento" in mensaje_lower:
            return self.tools.get("crear_documento_docx", lambda **kw: "❌ Plugin DOCX no disponible")(
                titulo="Documento de Novaria",
                contenido=mensaje
            ).get("message", "✅ Documento creado")
        
        if "lista" in mensaje_lower:
            return self.evolucion.listar_directorio(".")
        
        if "leer" in mensaje_lower:
            partes = mensaje.split()
            for i, parte in enumerate(partes):
                if parte == "leer" and i + 1 < len(partes):
                    return self.evolucion.leer_archivo(partes[i + 1])
        
        return "🤔 Lo siento, estoy experimentando dificultades técnicas. Por favor, intenta:\n" + \
               "  - 'estado' para ver el diagnóstico del sistema\n" + \
               "  - 'ayuda' para ver los comandos disponibles\n" + \
               "  - 'modelos' para ver los modelos activos"
    
    def _aprender_de_interaccion(self, mensaje: str, respuesta: str):
        """Aprende patrones de la interacción actual"""
        
        # Detectar tareas frecuentes
        mensaje_lower = mensaje.lower()
        
        if "documento" in mensaje_lower or "docx" in mensaje_lower:
            self.memory.learn_pattern(
                "tarea_frecuente",
                {"tarea": "crear_documentos", "mensaje_ejemplo": mensaje[:100]},
                confidence=0.3
            )
        
        if "código" in mensaje_lower or "programa" in mensaje_lower:
            self.memory.learn_pattern(
                "tarea_frecuente", 
                {"tarea": "trabajar_con_codigo", "mensaje_ejemplo": mensaje[:100]},
                confidence=0.3
            )
    
    def _finalizar_procesamiento(self, respuesta: str, inicio_tiempo: float):
        """Finaliza el procesamiento actualizando métricas y estado"""
        tiempo_total = time.time() - inicio_tiempo
        
        # Actualizar métricas de tiempo
        self.metricas["tiempos_respuesta"].append(tiempo_total)
        if len(self.metricas["tiempos_respuesta"]) > 50:
            self.metricas["tiempos_respuesta"].pop(0)
        
        self.metricas["tiempo_promedio_respuesta"] = \
            sum(self.metricas["tiempos_respuesta"]) / len(self.metricas["tiempos_respuesta"])
        
        # Añadir respuesta al historial
        self.historial_chat.append({"role": "assistant", "content": respuesta})
        
        # Limitar historial en RAM
        if len(self.historial_chat) > 20:
            self.historial_chat = self.historial_chat[-20:]
        
        self.estado_actual = f"✅ Listo ({tiempo_total:.1f}s)"
    
    def _generar_ayuda(self) -> str:
        """Genera el mensaje de ayuda"""
        return """📚 **NOVARIA v6.0 - AYUDA**

**Comandos directos:**
  - `estado` o `status` - Diagnóstico del sistema
  - `memoria` - Estado de la memoria
  - `modelos` - Modelos cloud disponibles  
  - `plugins` - Plugins cargados
  - `ls [ruta]` - Listar directorio
  - `leer [archivo]` - Leer archivo

**Capacidades avanzadas:**
  - 🧠 Memoria persistente que aprende de tus interacciones
  - 🤖 Múltiples modelos cloud (Groq, OpenRouter, HuggingFace)
  - 📄 Creación de documentos Word (DOCX)
  - 💻 Análisis de código fuente
  - 🔧 Auto-reparación del sistema

**Ejemplos:**
  - "Crea un documento Word sobre Python"
  - "Analiza el archivo script.py"
  - "Busca información sobre [tema] en mi memoria"

**Atajos de teclado:**
  - `Ctrl + Enter` - Enviar mensaje
  - `Esc` - Limpiar input"""
    
    def obtener_estado(self) -> Dict:
        """Retorna el estado actual del cerebro"""
        return {
            "corriendo": self.corriendo,
            "estado_texto": self.estado_actual,
            "proyectos_creados": self.metricas["herramientas_ejecutadas"],
            "consultas_totales": self.metricas["consultas_totales"],
            "modelos_disponibles": len(self.orchestrator.models),
            "plugins_activos": len(self.plugin_manager.plugins),
            "memoria_total": self.memory.get_stats()["total_interactions"]
        }
    
    def get_metricas(self) -> Dict:
        """Retorna métricas detalladas"""
        return {
            **self.metricas,
            "modelos_disponibles": len(self.orchestrator.models),
            "plugins_cargados": len(self.plugin_manager.plugins),
            "memoria_stats": self.memory.get_stats(),
            "modelo_mas_usado": max(
                self.metricas["modelos_utilizados"].items(),
                key=lambda x: x[1]
            )[0] if self.metricas["modelos_utilizados"] else "Ninguno"
        }
    
    def detener(self):
        """Detiene el cerebro de manera ordenada"""
        print("🛑 Deteniendo Novaria...")
        
        # Limpiar memoria antigua
        self.memory.clear_old_memories(days=30)
        
        # Guardar estado
        self.corriendo = False
        self.estado_actual = "⚫ Detenido"
        
        print("✅ Novaria detenida correctamente")