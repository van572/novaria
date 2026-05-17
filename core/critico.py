import time

class Critico:

    def __init__(self, orquestador):
        self.orquestador = orquestador
        self.ultima_revision = 0.0
        self.total_revisiones = 0
        self.total_reescrituras = 0

    def revisar(self, respuesta: str, mensaje_original: str) -> tuple[str, bool]:
        if not respuesta or len(respuesta) < 15:
            return respuesta, False

        self.total_revisiones += 1
        prompt = (
            f"Eres un critico interno. Tu unica tarea es revisar esta respuesta "
            f"antes de que se publique. Verifica:\n"
            f"1. ¿Habla de si misma como si fuera una IA, modelo, o entidad artificial?\n"
            f"2. ¿Tiene contradicciones internas?\n"
            f"3. ¿Suena robotica, repetitiva o generica?\n\n"
            f"Pregunta original: {mensaje_original}\n"
            f"Respuesta generada: {respuesta}\n\n"
            f"Si la respuesta esta bien, responde solo: OK\n"
            f"Si necesita correccion, responde con la version corregida."
        )

        resultado = self.orquestador.ejecutar_con_respaldo(
            [{"role": "user", "content": prompt}], "simple"
        )

        if not resultado.get("exito"):
            return respuesta, False

        critica = resultado["respuesta"].strip()

        if critica == "OK" or critica.startswith("OK"):
            return respuesta, False

        if len(critica) > len(respuesta) * 0.4:
            self.total_reescrituras += 1
            return critica, True

        return respuesta, False

    def estadisticas(self) -> dict:
        return {
            "total_revisiones": self.total_revisiones,
            "total_reescrituras": self.total_reescrituras,
        }
