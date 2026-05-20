import requests
import urllib.parse
import json
import time
from typing import Optional

DUCKDUckGO_API = "https://api.duckduckgo.com/"


def buscar_en_internet(consulta: str, max_resultados: int = 5) -> dict:
    params = {
        "q": consulta,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
        "t": "novaria",
    }
    try:
        resp = requests.get(DUCKDUckGO_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        resultados = []
        if data.get("AbstractText"):
            resultados.append({
                "tipo": "resumen",
                "titulo": data.get("Heading", ""),
                "texto": data["AbstractText"],
                "fuente": data.get("AbstractSource", ""),
            })
        if data.get("Answer"):
            resultados.append({
                "tipo": "respuesta",
                "texto": data["Answer"],
            })

        for topic in data.get("RelatedTopics", [])[:max_resultados]:
            if "Text" in topic:
                resultados.append({
                    "tipo": "relacionado",
                    "titulo": topic.get("FirstURL", ""),
                    "texto": topic["Text"],
                })
            elif "Topics" in topic:
                for sub in topic["Topics"][:3]:
                    if "Text" in sub:
                        resultados.append({
                            "tipo": "relacionado",
                            "texto": sub["Text"],
                        })

        return {
            "exito": True,
            "consulta": consulta,
            "resultados": resultados,
            "total": len(resultados),
        }
    except requests.Timeout:
        return {"exito": False, "consulta": consulta, "error": "La busqueda tardó demasiado"}
    except Exception as e:
        return {"exito": False, "consulta": consulta, "error": str(e)[:200]}
