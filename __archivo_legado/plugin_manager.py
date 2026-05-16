# plugin_manager.py
import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Callable
from pathlib import Path

class PluginManager:
    """
    Sistema de plugins auto-registrable.
    Los plugins se detectan automáticamente de la carpeta 'plugins/'
    y exponen sus herramientas al sistema principal.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.plugins_folder = os.path.join(workspace_path, "plugins")
        os.makedirs(self.plugins_folder, exist_ok=True)
        
        # Crear __init__.py si no existe
        init_file = os.path.join(self.plugins_folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Plugins de Novaria - Auto-detectados\n")
        
        self.plugins: Dict[str, Any] = {}
        self.tools_registry: Dict[str, Callable] = {}
        
        # Cargar plugins automáticamente
        self._discover_and_load_plugins()
        
    def _discover_and_load_plugins(self):
        """Descubre y carga automáticamente todos los plugins disponibles"""
        
        # Asegurar que la carpeta plugins está en el path
        if self.plugins_folder not in sys.path:
            sys.path.insert(0, self.workspace_path)
        
        # Buscar archivos .py en la carpeta plugins (excepto __init__.py)
        plugin_files = [
            f for f in os.listdir(self.plugins_folder) 
            if f.endswith('.py') and not f.startswith('__')
        ]
        
        if not plugin_files:
            print("📁 No se encontraron plugins. Creando plugins de ejemplo...")
            self._create_default_plugins()
            # Volver a buscar
            plugin_files = [
                f for f in os.listdir(self.plugins_folder) 
                if f.endswith('.py') and not f.startswith('__')
            ]
        
        for plugin_file in plugin_files:
            plugin_name = plugin_file[:-3]  # Quitar .py
            try:
                self._load_plugin(plugin_name)
            except Exception as e:
                print(f"⚠️ Error cargando plugin '{plugin_name}': {e}")
    
    def _load_plugin(self, plugin_name: str):
        """Carga un plugin específico y registra sus herramientas"""
        
        # Importar dinámicamente
        module = importlib.import_module(f"plugins.{plugin_name}")
        
        # Buscar la clase del plugin (por convención, misma que el nombre pero capitalizado)
        plugin_class = None
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                plugin_class = obj
                break
        
        if plugin_class is None:
            print(f"⚠️ No se encontró clase válida en el plugin: {plugin_name}")
            return
        
        # Instanciar el plugin
        plugin_instance = plugin_class(self.workspace_path)
        self.plugins[plugin_name] = plugin_instance
        
        # Registrar sus herramientas
        for name, method in inspect.getmembers(plugin_instance, inspect.ismethod):
            if hasattr(method, '_is_tool') and method._is_tool:
                self.tools_registry[name] = method
        
        print(f"✅ Plugin cargado: {plugin_name} ({len([m for m in inspect.getmembers(plugin_instance, inspect.ismethod) if hasattr(m[1], '_is_tool')])} herramientas)")
    
    def _create_default_plugins(self):
        """Crea plugins por defecto si no existen"""
        
        # Plugin de documentos
        docx_plugin_path = os.path.join(self.plugins_folder, "docx_plugin.py")
        if not os.path.exists(docx_plugin_path):
            with open(docx_plugin_path, 'w', encoding='utf-8') as f:
                f.write('''
import os
from typing import Dict
from docx import Document
from datetime import datetime

def tool(func):
    """Decorador para marcar métodos como herramientas"""
    func._is_tool = True
    return func

class DocxPlugin:
    """Plugin para crear y gestionar documentos DOCX"""
    
    def __init__(self, workspace_path: str):
        self.docs_folder = os.path.join(workspace_path, "documentos")
        os.makedirs(self.docs_folder, exist_ok=True)
    
    @tool
    def crear_documento_docx(self, titulo: str, contenido: str, autor: str = "Novaria") -> Dict:
        """Crea un documento DOCX con formato profesional"""
        try:
            doc = Document()
            
            # Título
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            title = doc.add_heading(titulo, 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Metadata
            doc.add_paragraph(f"Autor: {autor}")
            doc.add_paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph("_" * 50)
            doc.add_paragraph()
            
            # Contenido (soporta markdown básico)
            for linea in contenido.split('\\n'):
                linea = linea.strip()
                if not linea:
                    doc.add_paragraph()
                elif linea.startswith('# '):
                    doc.add_heading(linea[2:], level=1)
                elif linea.startswith('## '):
                    doc.add_heading(linea[3:], level=2)
                elif linea.startswith('- ') or linea.startswith('* '):
                    doc.add_paragraph(linea[2:], style='List Bullet')
                else:
                    p = doc.add_paragraph(linea)
                    p.style.font.size = Pt(11)
            
            # Guardar
            nombre_sanitizado = "".join(c for c in titulo if c.isalnum() or c in (' ', '_', '-')).rstrip()[:50]
            ruta = os.path.join(self.docs_folder, f"{nombre_sanitizado}.docx")
            doc.save(ruta)
            
            return {
                "success": True,
                "message": f"✅ Documento '{titulo}' creado exitosamente\\n📁 {ruta}",
                "ruta": ruta
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    @tool
    def listar_documentos(self) -> Dict:
        """Lista todos los documentos DOCX disponibles"""
        try:
            docs = [f for f in os.listdir(self.docs_folder) if f.endswith('.docx')]
            if not docs:
                return {"success": True, "message": "📁 No hay documentos creados aún"}
            return {"success": True, "message": f"📁 {len(docs)} documentos:\\n" + "\\n".join(f"  - {d}" for d in docs)}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
''')
            print("📝 Plugin DOCX creado automáticamente")
        
        # Plugin de análisis de código
        code_plugin_path = os.path.join(self.plugins_folder, "code_plugin.py")
        if not os.path.exists(code_plugin_path):
            with open(code_plugin_path, 'w', encoding='utf-8') as f:
                f.write('''
import os
import subprocess
from typing import Dict

def tool(func):
    func._is_tool = True
    return func

class CodePlugin:
    """Plugin para análisis y ejecución de código"""
    
    def __init__(self, workspace_path: str):
        self.code_folder = os.path.join(workspace_path, "codigo")
        os.makedirs(self.code_folder, exist_ok=True)
    
    @tool
    def analizar_archivo_codigo(self, ruta: str) -> Dict:
        """Analiza un archivo de código y retorna métricas básicas"""
        try:
            path = os.path.join(self.code_folder, ruta)
            if not os.path.exists(path):
                return {"success": False, "message": f"❌ Archivo no encontrado: {ruta}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            lineas = contenido.split('\\n')
            
            # Métricas básicas
            metricas = {
                "ruta": ruta,
                "lineas_totales": len(lineas),
                "lineas_codigo": len([l for l in lineas if l.strip() and not l.strip().startswith('#')]),
                "lineas_comentarios": len([l for l in lineas if l.strip().startswith('#')]),
                "lineas_vacias": len([l for l in lineas if not l.strip()]),
                "tamaño_bytes": len(contenido),
                "funciones": contenido.count('def ') if ruta.endswith('.py') else 'N/A',
                "clases": contenido.count('class ') if ruta.endswith('.py') else 'N/A'
            }
            
            return {
                "success": True,
                "message": f"📊 Análisis de {ruta}:\\n" + "\\n".join(f"  {k}: {v}" for k, v in metricas.items())
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    @tool
    def listar_archivos_codigo(self) -> Dict:
        """Lista archivos de código en el workspace"""
        try:
            archivos = os.listdir(self.code_folder)
            if not archivos:
                return {"success": True, "message": "📁 No hay archivos de código"}
            return {"success": True, "message": "📁 Archivos:\\n" + "\\n".join(f"  - {a}" for a in archivos)}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
''')
            print("📝 Plugin de Código creado automáticamente")
    
    def get_all_tools(self) -> Dict:
        """Retorna todas las herramientas registradas de todos los plugins"""
        return self.tools_registry
    
    def get_tool_info(self, tool_name: str) -> Dict:
        """Retorna información de una herramienta específica"""
        if tool_name in self.tools_registry:
            func = self.tools_registry[tool_name]
            return {
                "name": tool_name,
                "description": func.__doc__ or "Sin descripción",
                "parameters": inspect.signature(func).parameters
            }
        return {}
    
    def list_plugins(self) -> List[Dict]:
        """Lista todos los plugins cargados con sus herramientas"""
        plugins_info = []
        for name, instance in self.plugins.items():
            tools = []
            for method_name, method in inspect.getmembers(instance, inspect.ismethod):
                if hasattr(method, '_is_tool') and method._is_tool:
                    tools.append({
                        "name": method_name,
                        "description": method.__doc__ or "Sin descripción"
                    })
            
            plugins_info.append({
                "name": name,
                "tools_count": len(tools),
                "tools": tools
            })
        
        return plugins_info