import os
from herramientas.documentos import GeneradorDocumentos
from core.plugins import herramienta


class PluginDocumentos:

    def __init__(self):
        self.generadordocumentos = GeneradorDocumentos()

    @herramienta(nombre="plugindocumentos.crear_documento", descripcion="Crea un documento DOCX con título y contenido")
    def crear_documento(self, *args, **kwargs):
        return self.generadordocumentos.crear_documento(*args, **kwargs)

    @herramienta(nombre="plugindocumentos.listar_documentos", descripcion="Lista los documentos DOCX disponibles")
    def listar_documentos(self, *args, **kwargs):
        return self.generadordocumentos.listar_documentos(*args, **kwargs)
