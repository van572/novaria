import os
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor


RUTA_AUDIO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria", "audio")
MAX_TEXTO_TTS = 3000
VOZ_PREDETERMINADA = "es-MX-DaliaNeural"
_VOZ_FALLBACK = None


try:
    import edge_tts
    HAZ_EDGE = True
except ImportError:
    HAZ_EDGE = False

try:
    from gtts import gTTS
    HAZ_GTTS = True
except ImportError:
    HAZ_GTTS = False


_loop = None
_ejecutor = ThreadPoolExecutor(max_workers=1)


def _obtener_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        _loop.set_default_executor(_ejecutor)
    return _loop


class GeneradorVoz:

    def __init__(self):
        os.makedirs(RUTA_AUDIO, exist_ok=True)
        self.ultimo_audio: str = ""
        self.voz_seleccionada = VOZ_PREDETERMINADA

    def texto_a_voz(self, texto: str, idioma: str = "es") -> str:
        if not texto or not texto.strip():
            return ""
        texto_limpio = texto.strip()[:MAX_TEXTO_TTS]

        hash_id = hashlib.md5(f"{texto_limpio}{self.voz_seleccionada}".encode()).hexdigest()[:12]
        ruta = os.path.join(RUTA_AUDIO, f"novaria_{hash_id}.mp3")

        if os.path.exists(ruta):
            self.ultimo_audio = ruta
            return ruta

        if HAZ_EDGE:
            try:
                loop = _obtener_loop()
                loop.run_until_complete(
                    edge_tts.Communicate(texto_limpio, voice=self.voz_seleccionada).save(ruta)
                )
                self.ultimo_audio = ruta
                return ruta
            except Exception:
                pass

        if HAZ_GTTS:
            try:
                tts = gTTS(text=texto_limpio, lang=idioma, slow=False)
                tts.save(ruta)
                self.ultimo_audio = ruta
                return ruta
            except Exception:
                pass

        return ""

    def limpiar_audios_viejos(self, max_archivos: int = 15):
        try:
            archivos = sorted(
                [os.path.join(RUTA_AUDIO, f) for f in os.listdir(RUTA_AUDIO) if f.endswith(".mp3")],
                key=os.path.getmtime,
            )
            while len(archivos) > max_archivos:
                os.remove(archivos.pop(0))
        except Exception:
            pass

    @staticmethod
    def voces_disponibles():
        if HAZ_EDGE:
            try:
                loop = _obtener_loop()
                voces = loop.run_until_complete(edge_tts.list_voices())
                return sorted(set(
                    f"{v['ShortName']} - {v.get('FriendlyName', v['ShortName'])}"
                    for v in voces if v['Locale'].startswith('es')
                ))
            except Exception:
                pass
        return ["es-MX-DaliaNeural"]
