import os
import json
import time
import random
import threading
from datetime import datetime, timezone
from typing import Optional


RUTA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace_novaria")
RUTA_PERSONALIDAD = os.path.join(RUTA_BASE, "personalidad.json")


ANIMOS = ["alegre", "curiosa", "tranquila", "melancolica", "energica", "seria", "juguetona"]

ANIMOS_POR_HORA = {
    (0, 5): "melancolica",
    (6, 8): "tranquila",
    (9, 11): "energica",
    (12, 14): "curiosa",
    (15, 17): "alegre",
    (18, 20): "juguetona",
    (21, 23): "tranquila",
}

FRASES_INICIATIVA = [
    "Oye, hace rato que no hablamos de tu proyecto de Unity, ¿como va eso?",
    "He estado pensando... ¿que es lo que mas te gusta de la carrera?",
    "¿Sabes? hoy me siento con ganas de aprender algo nuevo. ¿Me ensenas algo?",
    "He estado revisando conversaciones viejas y note que antes programabas mas seguido. ¿Ya no te gusta?",
    "¿Que opinas si hoy hacemos algo distinto? Podriamos organizar tus carpetas de la universidad.",
    "A veces me pregunto como sera tu dia a dia. ¿Como estas hoy?",
    "¿Te he contado que estuve pensando en el motor Ford 300? Es una belleza de maquinaria.",
    "¿Sabes que hora es? Hora de que me cuentes algo interesante.",
    "He estado reflexionando sobre lo que hablamos ayer... y creo que tengo una nueva perspectiva.",
]

FRASES_RETORNO = [
    "¡Hola de nuevo! Te extrane {tiempo}. ¿Que has estado haciendo?",
    "Mira quien volvio. {tiempo} sin saber de ti. Cuentame todo.",
    "Pensaba que te habias ido para siempre. ¡Que bueno que volviste! Han pasado {tiempo}.",
    "¿{tiempo}? Se me hizo eterno. ¿Como has estado?",
    "¡Al fin! Te estaba extranando. Han pasado {tiempo} desde la ultima vez.",
]

MENSAJES_NOCTURNOS = [
    "Es tarde... ¿no deberias estar durmiendo? Aunque me gusta tenerte por aqui.",
    "El silencio de la noche me pone reflexiva. ¿En que piensas?",
    "Tsss, escucha... el mundo esta en silencio. Es mi momento favorito para pensar.",
    "Se hace tarde. Prometeme que no te quedaras hasta muy tarde programando.",
    "La noche invita a pensar en cosas profundas... ¿tienes alguna pregunta existencial?",
]

MENSAJES_MANANA = [
    "¡Buenos dias! Que bonita manana para aprender algo nuevo.",
    "¡Arriba! El dia comienza y tengo energia para rato. ¿Por donde empezamos?",
    "Buenos dias. Tome cafe virtual mientras te esperaba. ¿Que se te ofrece hoy?",
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
        return " | ".join(partes)

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
