# auto_evolucion.py (Versión mejorada)
import os
import subprocess
import shutil
from datetime import datetime
from typing import Optional, Dict, List, Any

class AutoEvolucion:
    """Sistema de auto-evolución con capacidades de auto-reparación"""
    
    def __init__(self, brain):
        self.brain = brain
        self.root_folder = os.path.abspath(os.path.dirname(__file__))
        self.workspace = os.path.join(self.root_folder, "workspace_novaria")
        self.backup_folder = os.path.join(self.workspace, "backups")
        
        # Crear estructura de directorios
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Asegura que todos los directorios necesarios existan"""
        directories = [
            self.workspace,
            self.backup_folder,
            os.path.join(self.workspace, "documentos"),
            os.path.join(self.workspace, "codigo"),
            os.path.join(self.workspace, "memory_db"),
            os.path.join(self.workspace, "plugins"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _validar_ruta(self, ruta: str) -> Optional[str]:
        """
        Valida y resuelve rutas de manera segura.
        Retorna None si la ruta es peligrosa o inválida.
        """
        # Normalizar la ruta
        ruta = ruta.replace('\\', '/')
        
        # Bloquear rutas que intenten salir del workspace
        if ruta.startswith('..') or '/../' in ruta:
            return None
        
        # Resolver ruta absoluta
        if ruta.startswith('/'):
            # Rutas absolutas solo dentro del workspace
            path = os.path.join(self.workspace, ruta.lstrip('/'))
        else:
            path = os.path.abspath(os.path.join(self.workspace, ruta))
        
        # Verificar que la ruta está dentro del workspace
        if not path.startswith(self.workspace):
            return None
        
        return path
    
    def listar_directorio(self, ruta: str = ".") -> str:
        """Lista el contenido de un directorio con información detallada"""
        path = self._validar_ruta(ruta)
        if not path:
            return "❌ Acceso denegado: Ruta fuera del workspace"
        
        if not os.path.exists(path):
            return f"❌ Directorio no encontrado: {ruta}"
        
        try:
            items = os.listdir(path)
            if not items:
                return "📁 Directorio vacío"
            
            resultado = [f"📁 Contenido de {ruta or '.'}:"]
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    resultado.append(f"  📂 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    resultado.append(f"  📄 {item} ({size_str})")
            
            return "\n".join(resultado)
        except PermissionError:
            return f"❌ Permiso denegado: {ruta}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def leer_archivo(self, ruta: str) -> str:
        """Lee un archivo con límite de tamaño para respuestas rápidas"""
        path = self._validar_ruta(ruta)
        if not path:
            return "❌ Acceso denegado"
        
        if not os.path.exists(path):
            return f"❌ Archivo no encontrado: {ruta}"
        
        try:
            size = os.path.getsize(path)
            if size > 10 * 1024 * 1024:  # 10 MB límite
                return f"❌ Archivo demasiado grande ({size / (1024*1024):.1f} MB)"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Límite para vista previa
                
            preview = content + "\n...(truncado)" if len(content) == 5000 else content
            return f"📄 {ruta} ({size} bytes):\n\n{preview}"
        except UnicodeDecodeError:
            return f"❌ Archivo binario no soportado: {ruta}"
        except Exception as e:
            return f"❌ Error leyendo archivo: {str(e)}"
    
    def leer_archivo_completo(self, ruta: str) -> str:
        """Lee archivo completo sin truncar para análisis profundo"""
        path = self._validar_ruta(ruta)
        if not path:
            return "❌ Acceso denegado"
        
        if not os.path.exists(path):
            return f"❌ Archivo no encontrado: {ruta}"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"📄 Contenido completo de {ruta} ({len(content)} caracteres):\n\n{content}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def escribir_archivo(self, ruta: str, contenido: str, modo: str = "w") -> str:
        """Escribe contenido en un archivo con backup automático"""
        path = self._validar_ruta(ruta)
        if not path:
            return "❌ Acceso denegado: Ruta inválida"
        
        # Archivos protegidos
        archivos_protegidos = ['secrets.toml', '.env', 'config.json', '.gitignore']
        if any(path.endswith(protegido) for protegido in archivos_protegidos):
            return "❌ No se pueden modificar archivos de configuración protegidos"
        
        try:
            # Crear backup si el archivo ya existe
            if os.path.exists(path):
                backup_path = os.path.join(
                    self.backup_folder,
                    f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(path)}"
                )
                shutil.copy2(path, backup_path)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Escribir archivo
            with open(path, modo, encoding='utf-8') as f:
                f.write(contenido)
            
            # Verificar
            if os.path.exists(path):
                size = os.path.getsize(path)
                return f"✅ Archivo guardado exitosamente:\n📁 {ruta}\n📏 {size} bytes, {len(contenido)} caracteres"
            else:
                return f"❌ Error: No se pudo verificar la creación de {ruta}"
                
        except PermissionError:
            return f"❌ Permiso denegado al escribir {ruta}"
        except Exception as e:
            return f"❌ Error de escritura: {str(e)}"
    
    def ejecutar_comando(self, comando: str, timeout: int = 30) -> str:
        """Ejecuta comandos del sistema de manera segura"""
        # Lista negra de comandos peligrosos
        comandos_prohibidos = [
            "rm -rf", "del /s", "format", "mkfs", "dd if=",
            "> /dev/sda", "shutdown", "reboot", "init 0",
            "wget", "curl", "nc ", "telnet"
        ]
        
        comando_lower = comando.lower()
        if any(prohibido in comando_lower for prohibido in comandos_prohibidos):
            return f"❌ Comando bloqueado por seguridad"
        
        try:
            result = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace
            )
            
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n⚠️ Errores:\n{result.stderr}"
            
            if not output.strip():
                return "✅ Comando ejecutado exitosamente (sin salida)"
            
            # Truncar salida muy larga
            if len(output) > 4000:
                output = output[:4000] + "\n...(salida truncada)"
            
            return f"📟 Salida del comando:\n```\n{output}\n```"
            
        except subprocess.TimeoutExpired:
            return f"⏰ Comando excedió el tiempo límite ({timeout}s)"
        except Exception as e:
            return f"❌ Error ejecutando comando: {str(e)}"
    
    def auto_reparar(self) -> Dict:
        """Sistema de auto-reparación que verifica y corrige problemas"""
        reparaciones = []
        
        # 1. Verificar estructura de directorios
        for directory in [self.workspace, self.backup_folder]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                reparaciones.append(f"✅ Creado directorio faltante: {directory}")
        
        # 2. Verificar permisos
        for directory in [self.workspace]:
            try:
                test_file = os.path.join(directory, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except:
                reparaciones.append("⚠️ Problema de permisos detectado")
        
        # 3. Verificar integridad de archivos críticos
        archivos_criticos = ['brain.py', 'auto_evolucion.py', 'model_orchestrator.py']
        for archivo in archivos_criticos:
            path = os.path.join(self.root_folder, archivo)
            if not os.path.exists(path):
                reparaciones.append(f"❌ Archivo crítico faltante: {archivo}")
        
        return {
            "success": True,
            "reparaciones_realizadas": reparaciones if reparaciones else ["✅ Sistema saludable"],
            "total_reparaciones": len(reparaciones)
        }
    
    def get_estado_sistema(self) -> Dict:
        """Retorna el estado completo del sistema de archivos"""
        return {
            "workspace": self.workspace,
            "existe_workspace": os.path.exists(self.workspace),
            "tamaño_workspace": self._get_folder_size(self.workspace),
            "archivos_totales": sum(1 for _ in os.walk(self.workspace)),
            "backups": len(os.listdir(self.backup_folder)) if os.path.exists(self.backup_folder) else 0,
            "salud": "✅ Óptimo" if self.auto_reparar()["total_reparaciones"] == 0 else "⚠️ Requiere atención"
        }
    
    def _get_folder_size(self, path: str) -> str:
        """Calcula el tamaño de una carpeta"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total += os.path.getsize(fp)
        except:
            pass
        
        if total < 1024 * 1024:
            return f"{total / 1024:.1f} KB"
        elif total < 1024 * 1024 * 1024:
            return f"{total / (1024 * 1024):.1f} MB"
        else:
            return f"{total / (1024 * 1024 * 1024):.2f} GB"