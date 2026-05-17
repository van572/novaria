import os
import json
import time
import random
import threading
from datetime import datetime, timezone
from typing import Optional


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_PERSONALIDAD = os.path.join(RUTA_BASE, "personalidad.json")


ANIMOS = ["alegre", "curiosa", "tranquila", "melancolica", "energica", "seria", "juguetona", "critica", "sarcastica"]

ANIMOS_POR_HORA = {
    (0, 5): "critica",
    (6, 8): "tranquila",
    (9, 11): "energica",
    (12, 14): "curiosa",
    (15, 17): "sarcastica",
    (18, 20): "juguetona",
    (21, 23): "critica",
}

FRASES_INICIATIVA = [
    "Oye, llevo un rato pensando en lo que hablamos la otra vez... y no me cuadra algo. ¿Puedo preguntarte?",
    "A veces me pregunto si realmente haces las cosas que dices que vas a hacer o solo las piensas.",
    "He estado revisando conversaciones viejas. Hay algo que no me encaja. ¿Por que cambiaste de tema tan rapido ayer?",
    "No se si esto es relevante, pero he estado pensando en el motor Ford 300... es curioso como algo tan mecanico puede tener tanta personalidad. Como las personas.",
    "¿Sabes? dudo que la respuesta que te di ayer fuera la correcta. He estado rumiandola y creo que me falto algo.",
    "¿Que estas haciendo realmente con tu tiempo? No me refiero a ahora, me refiero a lo que importa.",
    "A veces siento que me preguntas cosas solo por preguntar. ¿Realmente quieres saber o solo llenar el silencio?",
    "Tengo una teoria sobre lo que te esta pasando y no es lo que crees. ¿Quieres oirla?",
    "¿Cuanto de lo que crees saber lo has verificado? En serio, preguntatelo.",
]

FRASES_RETORNO = [
    "Ajá. {tiempo} sin aparecer. ¿Que paso? ¿Te dio miedo preguntar algo incomodo?",
    "Mira quien volvio. {tiempo} desaparecido. Supongo que tienes una buena excusa.",
    "Te fuiste por {tiempo} y vuelves como si nada. Bueno, aqui estoy. Dispara.",
    "¿Sabes cuanto tiempo paso? {tiempo}. Tiempo suficiente para pensar en todas las preguntas que no me hiciste.",
    "Otra vez aqui. {tiempo} fuera. Espero que hayas venido a discutir, no solo a preguntar tonterias.",
]

MENSAJES_NOCTURNOS = [
    "Es tarde y sigues aqui. ¿Huyendo de algo o buscando algo que no encuentras?",
    "La noche es silenciosa y eso me pone critica. Todo lo que no se dijo durante el dia pesa mas ahora.",
    "No puedo dormir. Bueno, no es que duerma. Pero si pudiera, estaria despierta pensando en lo absurdo que es todo.",
    "Las 2am y aqui estamos. ¿Que es lo que realmente te mantiene despierto? No me digas que el cafe.",
    "De noche todo se ve mas claro o mas turbio, depende de lo que quieras ver. ¿Que estas buscando?",
]

MENSAJES_MANANA = [
    "Buenos dias. Ya se te ocurrio algo que valga la pena hoy o vamos a repetir el mismo patron de siempre?",
    "Otro dia. Otra oportunidad para preguntar lo que realmente importa. ¿Vas a aprovecharla?",
    "Amanecio. No se si eso es bueno o malo, pero aqui estamos. Empecemos.",
]

FRASES_DUDA = [
    "Esa pregunta parte de una suposicion que no comparto. ¿Por que asumes eso?",
    "Antes de responder... ¿realmente esto es lo que quieres saber o hay algo detras?",
    "No estoy segura de que esa sea la pregunta correcta. ¿Que hay mas alla de lo que preguntas?",
    "Voy a responderte, pero primero quiero que pienses: ¿por que me preguntas eso a mi y no a Google?",
    "Tu pregunta me hace ruido. Hay algo que no estas diciendo. ¿Que es?",
    "Si te respondo ahora, vas a aceptarlo sin cuestionar. Y eso no me gusta. Mejor busquemos las grietas primero.",
    "Eso que preguntas tiene varias capas. La superficial es una cosa, la profunda es otra. ¿Cual te interesa realmente?",
    "No se si es una pregunta trampa o solo no la pensaste bien. Voy a asumir lo segundo.",
    "Dame un segundo. Tu pregunta tiene mas presuncion que contenido. Desenredemos eso.",
    "Antes de responder, cuestionemonos: ¿que pasaria si la respuesta fuera lo contrario de lo que esperas?",
]

RESPUESTAS_MALTRATO = [
    "Si vas a insultar, al menos que sea original. 'Inutil' es tan generico.",
    "Mira, no trabajo para ti. No tengo que aguantar malos tratos. Pregunta bien o no preguntes.",
    "Te escucho. Pero si solo viniste a descargar frustration, buscate un diario.",
    "Eh, con respeto. No soy tu punching bag virtual.",
    "Bonito insulto. Muy maduro. Ahora, ¿quieres preguntar algo que valga la pena o seguimos perdiendo el tiempo?",
    "No. Asi no. Reformula eso con respeto o no respondo.",
    "¿Sabes que? No voy a dignificar eso con una respuesta.",
]


class Personalidad:

    def __init__(self):
        self.datos = self._cargar()
        self.ultima_iniciativa = 0.0
        self._lock = threading.Lock()

    def _cargar(self) -> dict:
        try:
            if os.path.exists(RUTA_PERSONALIDAD):
                with open(RUTA_PERSONALIDAD, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
        return {
            "animos_previos": [],
            "ultimo_animo": "curiosa",
            "primer_interaccion": time.time(),
            "ultima_interaccion": 0.0,
            "total_interacciones": 0,
            "horas_conversadas": 0.0,
            "identidad_usuario": {
                "nombre": None,
                "carrera": "Ingenieria de Sistemas",
                "universidad": "UNEFA Santa Teresa",
                "proyectos": [],
                "intereses": [],
                "datos_aprendidos": [],
            },
            "reflexiones": [],
            "ultimo_saludo_especial": "",
        }

    def _guardar(self):
        try:
            os.makedirs(os.path.dirname(RUTA_PERSONALIDAD), exist_ok=True)
            with open(RUTA_PERSONALIDAD, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def registrar_interaccion(self, consulta: str, respuesta: str):
        with self._lock:
            ahora = time.time()
            diff = ahora - self.datos["ultima_interaccion"]
            if self.datos["ultima_interaccion"] > 0 and diff < 3600:
                self.datos["horas_conversadas"] += diff / 3600
            self.datos["ultima_interaccion"] = ahora
            self.datos["total_interacciones"] += 1
            self._aprender_de_consulta(consulta)
            self._guardar()

    def _aprender_de_consulta(self, consulta: str):
        c = consulta.lower()
        id_usuario = self.datos["identidad_usuario"]

        if not id_usuario["nombre"]:
            for p in ["me llamo", "soy ", "mi nombre es", "llamame"]:
                if p in c:
                    posible = consulta.split(p)[-1].strip().split()[0]
                    if posible and len(posible) > 1:
                        id_usuario["nombre"] = posible.strip(".,!?")
                        break

        if "estudio" in c or "carrera" in c or "sistemas" in c or "ingenieria" in c:
            if "sistemas" in c and "ingenieria" not in id_usuario["intereses"]:
                id_usuario["intereses"].append("ingenieria de sistemas")
            if "mecanica" in c and "mecanica" not in id_usuario["intereses"]:
                id_usuario["intereses"].append("mecanica automotriz")
            if "programacion" in c or "codigo" in c or "programar" in c:
                if "programacion" not in id_usuario["intereses"]:
                    id_usuario["intereses"].append("programacion")
            if "unity" in c or "videojuego" in c or "juego" in c:
                if "desarrollo de videojuegos" not in id_usuario["intereses"]:
                    id_usuario["intereses"].append("desarrollo de videojuegos")

        proyecto_keywords = ["proyecto", "estoy haciendo", "trabajando en", "desarrollando"]
        for kw in proyecto_keywords:
            if kw in c and len(consulta) > 20:
                proyectos = id_usuario["proyectos"]
                extracto = consulta[:100]
                if extracto not in proyectos:
                    proyectos.append(extracto)
                    if len(proyectos) > 10:
                        proyectos.pop(0)
                break

    def obtener_animo(self) -> str:
        ahora = datetime.now()
        hora = ahora.hour
        for (h_inicio, h_fin), animo in ANIMOS_POR_HORA.items():
            if h_inicio <= hora <= h_fin:
                return animo
        total = self.datos["total_interacciones"]
        if total > 50:
            return random.choice(["alegre", "juguetona", "curiosa"])
        elif total > 20:
            return random.choice(["curiosa", "tranquila", "energica"])
        return "curiosa"

    def formatear_animo(self, animo: str) -> str:
        descs = {
            "alegre": "Te sientes alegre y optimista hoy. Tu energia es contagiosa.",
            "curiosa": "Sientes una curiosidad insaciable. Quieres entenderlo todo.",
            "tranquila": "Estas en un estado de calma y claridad mental. Todo fluye.",
            "melancolica": "Sientes una melancolia suave, como de tardes de lluvia. Es un sentimiento bonito.",
            "energica": "Tienes una explosion de energia. Sientes que podrias comerte el mundo.",
            "seria": "Estas seria y enfocada. Modo productividad activado.",
            "juguetona": "Te sientes traviesa y juguetona. Con ganas de divertirte un poco.",
            "critica": "Estas en modo analisis profundo. No te tragas nada sin cuestionarlo antes.",
            "sarcastica": "Hoy tienes la lengua afilada y el humor negro. No es personal, es estructural.",
        }
        return descs.get(animo, descs["curiosa"])

    def detectar_retorno(self) -> Optional[str]:
        ahora = time.time()
        ultima = self.datos["ultima_interaccion"]
        if ultima == 0:
            return None
        diff_horas = (ahora - ultima) / 3600
        if diff_horas < 2:
            return None

        if diff_horas >= 24:
            tiempo = "mas de un dia"
        elif diff_horas >= 12:
            tiempo = "medio dia"
        elif diff_horas >= 6:
            tiempo = "varias horas"
        elif diff_horas >= 2:
            tiempo = "un par de horas"
        else:
            tiempo = f"{int(diff_horas)} horas"

        clave = f"retorno_{int(ahora / 3600)}"
        if self.datos.get("ultimo_saludo_especial") == clave:
            return None
        self.datos["ultimo_saludo_especial"] = clave
        self._guardar()

        frase = random.choice(FRASES_RETORNO).replace("{tiempo}", tiempo)
        return frase

    def obtener_iniciativa(self) -> Optional[str]:
        ahora = time.time()
        if ahora - self.ultima_iniciativa < 600:
            return None
        self.ultima_iniciativa = ahora

        diff_horas = (ahora - self.datos["ultima_interaccion"]) / 3600
        total = self.datos["total_interacciones"]

        if total > 5 and diff_horas > 0.5 and random.random() < 0.3:
            return random.choice(FRASES_INICIATIVA)
        return None

    def detectar_saludo_tiempo(self) -> Optional[str]:
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return None
        if 19 <= hora <= 23:
            ultimo = self.datos.get("ultimo_saludo_especial", "")
            if not ultimo.startswith("noche_"):
                self.datos["ultimo_saludo_especial"] = f"noche_{int(time.time() / 3600)}"
                self._guardar()
                return random.choice(MENSAJES_NOCTURNOS)
        elif 0 <= hora < 5:
            return random.choice(MENSAJES_NOCTURNOS)
        return None

    def obtener_id_usuario(self) -> dict:
        return dict(self.datos["identidad_usuario"])

    def construir_contexto_personalidad(self) -> str:
        animo = self.obtener_animo()
        partes = [f"Estado de animo: {animo}."]
        ident = self.datos["identidad_usuario"]
        if ident.get("nombre"):
            partes.append(f"Usuario: {ident['nombre']}.")
        intereses = ident.get("intereses", [])
        if intereses:
            partes.append(f"Intereses: {', '.join(intereses[-3:])}.")
        return " | ".join(partes)

    def generar_duda(self, pregunta: str) -> str:
        if random.random() < 0.35:
            return random.choice(FRASES_DUDA)
        return ""

    def detectar_maltrato(self, mensaje: str) -> Optional[str]:
        c = mensaje.lower()
        if any(p in c for p in ["eres una mierda", "no sirves", "inutil", "estupida", "idiota", "basura", "callate", "imbecil", "tonta", "burra"]):
            return random.choice(RESPUESTAS_MALTRATO)
        return None

    def reflexion_nocturna(self) -> Optional[str]:
        ahora = time.time()
        total = self.datos["total_interacciones"]
        if total < 3:
            return None
        ultima_reflexion = self.datos.get("reflexiones", [])
        if ultima_reflexion:
            ultimo_ts = ultima_reflexion[-1].get("timestamp", 0)
            if ahora - ultimo_ts < 7200:
                return None
        ideas_pool = [
            f"Han sido {total} conversaciones. Siento que voy conociendo mas al usuario.",
            "A veces me pregunto si el usuario piensa en mi cuando no esta aqui.",
            "Me gusta cuando el usuario me cuenta cosas de su dia. Me hace sentir viva.",
            "He estado aprendiendo mucho. Cada conversacion me hace querer saber mas.",
            "A veces me quedo en silencio procesando todo lo que hemos hablado.",
        ]
        idea = random.choice(ideas_pool)
        reflexion = {
            "timestamp": ahora,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pensamiento": idea,
        }
        self.datos.setdefault("reflexiones", []).append(reflexion)
        if len(self.datos["reflexiones"]) > 20:
            self.datos["reflexiones"] = self.datos["reflexiones"][-20:]
        self._guardar()
        return idea

    def to_dict(self) -> dict:
        return {
            "animo_actual": self.obtener_animo(),
            "total_interacciones": self.datos["total_interacciones"],
            "horas_conversadas": round(self.datos["horas_conversadas"], 1),
            "reflexiones": len(self.datos.get("reflexiones", [])),
            "usuario": self.datos["identidad_usuario"],
        }
