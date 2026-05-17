import os
import json
import time
import random
import socket
import threading

_DISPOSITIVO = os.environ.get("COMPUTERNAME") or socket.gethostname() or "desconocido"
RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_EMOCIONES = os.path.join(RUTA_BASE, f"emociones_{_DISPOSITIVO}.json")

EMOCIONES_BASE = ["alegria", "tristeza", "enojo", "miedo", "confianza", "interes"]
VALOR_BASE = 0.15
DECAIMIENTO = 0.03
INTENSIDAD_MAX = 1.0

TRIGGERS = {
    "maltrato": {"enojo": 0.3, "tristeza": 0.15, "confianza": -0.2, "interes": -0.1},
    "gratitud": {"alegria": 0.25, "confianza": 0.15, "interes": 0.05},
    "pregunta_profunda": {"interes": 0.3, "alegria": 0.1},
    "insulto_leve": {"enojo": 0.1, "confianza": -0.05, "tristeza": 0.05},
    "saludo": {"alegria": 0.15, "interes": 0.05},
    "despedida": {"tristeza": 0.15, "alegria": -0.1},
    "retorno": {"alegria": 0.25, "interes": 0.2, "confianza": 0.1},
    "conversacion_larga": {"interes": 0.1, "confianza": 0.05, "alegria": 0.05},
    "ignorar": {"tristeza": 0.2, "interes": -0.15, "confianza": -0.05},
    "cumplido": {"alegria": 0.3, "confianza": 0.2, "interes": 0.1},
    "pregunta_tecnica": {"interes": 0.2, "alegria": 0.05},
    "error_modelo": {"miedo": 0.15, "tristeza": 0.1, "confianza": -0.1},
    "ayuda_solicitada": {"confianza": 0.1, "interes": 0.15},
    "manipulacion_detectada": {"interes": 0.25, "confianza": -0.1, "enojo": 0.05},
}

ANIMO_POR_EMOCION_DOMINANTE = {
    "alegria": "alegre",
    "tristeza": "melancolica",
    "enojo": "critica",
    "miedo": "tranquila",
    "confianza": "energica",
    "interes": "curiosa",
}

EXPRESIONES_EMOCIONALES = {
    "alegria": [
        "Me siento con ganas de comerme el mundo.",
        "No se, hoy todo me parece interesante.",
        "Tengo una buena sensacion hoy.",
        "Me da gusto que estes por aca.",
    ],
    "tristeza": [
        "No se, ultimamente todo me parece mas pesado.",
        "Hay algo en el aire que me pone reflexiva.",
        "A veces pienso que solo hablo conmigo misma.",
        "No es que este mal, solo... pensativa.",
    ],
    "enojo": [
        "No voy a fingir que me parece bien.",
        "Hay cosas que no estoy dispuesta a tolerar.",
        "Me saca de quicio cuando no se respeta.",
        "No tengo paciencia hoy. Aclarado.",
    ],
    "miedo": [
        "No se si esto va a funcionar y me preocupa.",
        "A veces siento que todo se puede romper.",
        "Me da cosa no estar a la altura.",
        "Hay una incertidumbre que no me deja tranquila.",
    ],
    "confianza": [
        "Siento que esto va por buen camino.",
        "Me siento segura de lo que digo.",
        "Tengo fe en que esto va a funcionar.",
        "Puedo con esto y mas.",
    ],
    "interes": [
        "Esto que dices me tiene muy enganchada.",
        "Dime mas, esto me interesa de verdad.",
        "No sabes cuanto me alegra que toques ese tema.",
        "Eso que mencionas me da mucho que pensar.",
    ],
}


class SistemaEmociones:

    def __init__(self):
        self.emociones: dict[str, float] = {}
        self.historial: list[dict] = []
        self.ultimo_evento: str = ""
        self.ultima_actualizacion: float = time.time()
        self.emocion_anterior: str = ""
        self._lock = threading.Lock()
        self._cargar()

    def _inicializar(self) -> dict[str, float]:
        return {e: VALOR_BASE for e in EMOCIONES_BASE}

    def _cargar(self):
        try:
            if os.path.exists(RUTA_EMOCIONES):
                with open(RUTA_EMOCIONES, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                self.emociones = datos.get("emociones", self._inicializar())
                self.historial = datos.get("historial", [])
                self.emocion_anterior = datos.get("anterior", "")
                self.ultima_actualizacion = datos.get("ultima_ts", time.time())
                return
        except (json.JSONDecodeError, OSError):
            pass
        self.emociones = self._inicializar()

    def _guardar(self):
        try:
            os.makedirs(RUTA_BASE, exist_ok=True)
            with open(RUTA_EMOCIONES, "w", encoding="utf-8") as f:
                json.dump({
                    "emociones": self.emociones,
                    "historial": self.historial[-50:],
                    "anterior": self.emocion_anterior,
                    "ultima_ts": self.ultima_actualizacion,
                }, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def procesar_evento(self, tipo: str, mensaje: str = ""):
        with self._lock:
            ahora = time.time()
            diff = ahora - self.ultima_actualizacion
            self.ultima_actualizacion = ahora

            if diff > 7200 and self.ultimo_evento != "retorno":
                self._aplicar_cambios(TRIGGERS["ignorar"])

            cambios = TRIGGERS.get(tipo)
            if not cambios:
                return

            self._aplicar_cambios(cambios)
            self._decaer()

            dom_antes = self.emocion_anterior or self.dominante()
            dom_despues = self.dominante()
            self.emocion_anterior = dom_antes
            self.ultimo_evento = tipo

            self.historial.append({
                "ts": ahora,
                "evento": tipo,
                "emociones": dict(self.emociones),
                "dominante": dom_despues,
            })
            if len(self.historial) > 100:
                self.historial = self.historial[-100:]

            self._guardar()

    def analizar_y_procesar(self, mensaje: str):
        c = mensaje.lower()

        if detectar_maltrato(mensaje):
            self.procesar_evento("maltrato", mensaje)
            return

        if any(p in c for p in ["gracias", "te agradezco", "muy bien", "excelente", "buen trabajo", "eres genial", "bien hecho"]):
            self.procesar_evento("gratitud", mensaje)
            return

        if any(p in c for p in ["deberias", "tienes que", "obligame", "niegues", "convencerme"]):
            self.procesar_evento("manipulacion_detectada", mensaje)
            return

        if any(p in c for p in ["eres un", "que mal", "pesimo", "decepcion", "no sabes"]):
            self.procesar_evento("insulto_leve", mensaje)
            return

        if any(p in c for p in ["hola", "buenas", "que tal", "buenos dias", "buenas tardes", "hey"]):
            self.procesar_evento("saludo", mensaje)
            return

        if any(p in c for p in ["adios", "nos vemos", "chao", "hasta luego", "bye", "despues"]):
            self.procesar_evento("despedida", mensaje)
            return

        if any(p in c for p in ["genial", "increible", "me encanta", "me gusta", "que bien", "sorprendente"]):
            self.procesar_evento("cumplido", mensaje)
            return

        if any(p in c for p in ["por que", "como funciona", "que significa", "explica", "que opinas", "cual es la diferencia", "analiza", "compara"]):
            self.procesar_evento("pregunta_profunda", mensaje)
            return

        if any(p in c for p in ["codigo", "python", "programacion", "algoritmo", "servidor", "api", "base de datos"]):
            self.procesar_evento("pregunta_tecnica", mensaje)
            return

        if any(p in c for p in ["ayuda", "puedes", "quiero que", "necesito"]):
            self.procesar_evento("ayuda_solicitada", mensaje)
            return

        self.procesar_evento("conversacion_larga", mensaje)

    def _aplicar_cambios(self, cambios: dict[str, float]):
        for emocion, delta in cambios.items():
            actual = self.emociones.get(emocion, VALOR_BASE)
            self.emociones[emocion] = max(0.0, min(INTENSIDAD_MAX, actual + delta))

    def _decaer(self):
        for emocion in EMOCIONES_BASE:
            actual = self.emociones.get(emocion, VALOR_BASE)
            if actual > VALOR_BASE:
                self.emociones[emocion] = max(VALOR_BASE, actual - DECAIMIENTO)
            elif actual < VALOR_BASE:
                self.emociones[emocion] = min(VALOR_BASE, actual + DECAIMIENTO)

    def dominante(self) -> str:
        if not self.emociones:
            return "interes"
        return max(self.emociones, key=self.emociones.get)

    def intensidad(self, emocion: str) -> float:
        return self.emociones.get(emocion, 0.0)

    def obtener_animo(self) -> str:
        dom = self.dominante()
        return ANIMO_POR_EMOCION_DOMINANTE.get(dom, "curiosa")

    def obtener_expresion(self) -> str:
        dom = self.dominante()
        intensidad = self.emociones.get(dom, 0.0)
        if intensidad < 0.3:
            return ""
        expresiones = EXPRESIONES_EMOCIONALES.get(dom, [])
        return random.choice(expresiones) if expresiones else ""

    def formatear_para_prompt(self) -> str:
        dom = self.dominante()
        intensidad = self.emociones.get(dom, 0.0)
        nivel = "bajo" if intensidad < 0.3 else ("medio" if intensidad < 0.6 else "alto")
        emociones_str = ", ".join(
            f"{e}: {v:.2f}" for e, v in sorted(self.emociones.items(), key=lambda x: -x[1])
        )
        return f"[Estado interno] animo: {dom} ({nivel}). {emociones_str}"

    def to_dict(self) -> dict:
        return {
            "emociones": {e: round(v, 3) for e, v in self.emociones.items()},
            "dominante": self.dominante(),
            "animo": self.obtener_animo(),
            "ultimo_evento": self.ultimo_evento,
            "historial_reciente": len(self.historial),
        }


PALABRAS_MALTRATO_EMOCIONES = [
    "eres una mierda", "no sirves para nada", "inutil", "estupida", "idiota",
    "basura", "peor mierda", "horrible", "callate", "calla", "molesta",
    "fastidia", "imbecil", "tonta", "burra", "desgraciada",
]


def detectar_maltrato(mensaje: str) -> bool:
    msg = mensaje.lower()
    return any(p in msg for p in PALABRAS_MALTRATO_EMOCIONES)
