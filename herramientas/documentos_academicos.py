import os
import hashlib
import threading
from typing import Optional


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_PDFS = os.path.join(RUTA_BASE, "pdfs_unefa")
RUTA_INDEX = os.path.join(RUTA_BASE, "memory_db")


try:
    import fitz
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False


class IndexadorAcademicos:

    def __init__(self, memoria=None):
        self.memoria = memoria
        self.pdfs_indexados: set = set()
        self._lock = threading.Lock()
        os.makedirs(RUTA_PDFS, exist_ok=True)

    def set_memoria(self, memoria):
        self.memoria = memoria

    def escanear_y_indexar(self) -> dict:
        if not HAS_PDF_SUPPORT:
            return {"exito": False, "mensaje": "PyMuPDF no instalado"}
        if not self.memoria:
            return {"exito": False, "mensaje": "Sistema de memoria no disponible"}
        if not os.path.isdir(RUTA_PDFS):
            return {"exito": True, "indexados": 0, "mensaje": "No hay carpeta de PDFs"}

        pdfs = [f for f in os.listdir(RUTA_PDFS) if f.lower().endswith(".pdf")]
        if not pdfs:
            return {"exito": True, "indexados": 0, "mensaje": "No hay PDFs"}

        nuevos = 0
        errores = 0
        for archivo in pdfs:
            ruta = os.path.join(RUTA_PDFS, archivo)
            hash_archivo = self._hash_archivo(ruta)
            if hash_archivo in self.pdfs_indexados:
                continue
            try:
                texto = self._extraer_texto_pdf(ruta)
                if texto.strip():
                    self._indexar_documento(archivo, texto, hash_archivo)
                    self.pdfs_indexados.add(hash_archivo)
                    nuevos += 1
            except Exception:
                errores += 1

        return {"exito": True, "indexados": nuevos, "errores": errores}

    def indexar_pdf_individual(self, ruta: str) -> dict:
        if not HAS_PDF_SUPPORT:
            return {"exito": False, "mensaje": "PyMuPDF no instalado"}
        if not self.memoria:
            return {"exito": False, "mensaje": "Sistema de memoria no disponible"}
        if not os.path.isfile(ruta):
            return {"exito": False, "mensaje": f"No se encuentra: {ruta}"}

        nombre = os.path.basename(ruta)
        hash_archivo = self._hash_archivo(ruta)
        if hash_archivo in self.pdfs_indexados:
            return {"exito": True, "mensaje": f"Ya indexado: {nombre}"}

        try:
            texto = self._extraer_texto_pdf(ruta)
            if not texto.strip():
                return {"exito": False, "mensaje": f"PDF vacío o sin texto: {nombre}"}
            self._indexar_documento(nombre, texto, hash_archivo)
            with self._lock:
                self.pdfs_indexados.add(hash_archivo)
            return {"exito": True, "mensaje": f"Indexado: {nombre}", "paginas": len(texto) // 2000 + 1}
        except Exception as e:
            return {"exito": False, "mensaje": f"Error indexando {nombre}: {str(e)[:200]}"}

    def _extraer_texto_pdf(self, ruta: str) -> str:
        doc = fitz.open(ruta)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        doc.close()
        return texto

    def _indexar_documento(self, nombre: str, texto: str, hash_id: str):
        resumen = texto[:500]
        self.memoria.agregar_documento_academico(
            id_doc=hash_id,
            nombre=nombre,
            texto=texto,
            resumen=resumen,
        )

    def consultar(self, consulta: str, max_resultados: int = 3) -> list[dict]:
        if not self.memoria:
            return []
        return self.memoria.consultar_documentos_academicos(consulta, max_resultados)

    def listar_indexados(self) -> list[str]:
        with self._lock:
            if self.memoria:
                return self.memoria.listar_documentos_academicos()
            return []

    @staticmethod
    def _hash_archivo(ruta: str) -> str:
        try:
            with open(ruta, "rb") as f:
                return hashlib.md5(f.read(8192)).hexdigest()
        except Exception:
            return ""
