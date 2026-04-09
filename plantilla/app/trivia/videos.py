"""
Modulo para hacer cuestiones de trivia relacionadas con videos de Youtube. Creamos una clase TriviaVideo que extiende
a Trivia y almacena el id de reproduccion de video
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from.operaciones_coleccion import OperacionesEurovision
from .preguntas import Trivia


def extraer_id_url(url) -> str:
    """
    Para renderizar el juego, necesitamos extraer el id desde la url del video.
    Utilizamos expresiones regulares
    """
    try:
        return Path(url).name
    except:
        # Return id for Rick Roll
        return "dQw4w9WgXcQ"


class TriviaVideo(Trivia, ABC):
    """
    Clase abstracta que contiene los metodos que deben incorporar las preguntas asociadas a videos.
    """
    @property
    @abstractmethod
    def url(self) -> str:
        pass

    def to_dict(self):
        # Modifica el diccionario de Trivia con la url del video
        # y el tipo "video"
        super_dict = super().to_dict()
        super_dict["url"] = self.url
        # Extraemos el id de la URL
        super_dict["url_id"] = extraer_id_url(self.url)
        super_dict["tipo"] = "video"
        return super_dict


class PaisActuacion(TriviaVideo):
    """
    ¿Que pais represento la cancion?
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion_aleatoria = parametros.participacion_aleatoria(1)[0]
        self._url = participacion_aleatoria["url_youtube"]
        self._respuesta = participacion_aleatoria["pais"]

        opciones = parametros.paises_participantes_aleatorios(50)
        opciones_invalidas = []
        for pais in opciones:
            if pais != self._respuesta and pais not in opciones_invalidas:
                opciones_invalidas.append(pais)
            if len(opciones_invalidas) == 3:
                break

        self._opciones_invalidas = opciones_invalidas

    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return "¿A qué país representó esta canción?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 3


class NombreCancion(TriviaVideo):
    """
    ¿Cual es el titulo de esta cancion?

    NOTA: para dificultar la respuesta, se deben seleccionar canciones del mismo pais.
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion_aleatoria = parametros.participacion_aleatoria(1)[0]
        self._url = participacion_aleatoria["url_youtube"]
        self._respuesta = participacion_aleatoria["cancion"]
        pais_participando = participacion_aleatoria["pais"]
        canciones_pais = list(parametros.agregacion([
            {"$unwind": "$concursantes"},
            {"$match": {
                "concursantes.pais": pais_participando}}, #me quedo solo con las participaciones del pais
            {"$project":{
                "_id":0,
                "cancion": "$concursantes.cancion" #me quedo solo con sus canciones
            }},
            {"$group": {
                "_id": "$concursantes.cancion" #para evitar repetidos
            }}
        ]))
        opciones_invalidas = []
        for cancion in canciones_pais:
            if cancion != self._respuesta and cancion not in opciones_invalidas:
                opciones_invalidas.append(cancion)
            if len(opciones_invalidas) == 3:
                break
        self._opciones_invalidas = opciones_invalidas

    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return "¿Cual es el titulo de esta cancion?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 2


class InterpreteCancion(TriviaVideo):
    """
    ¿Quien interpreto esta cancion?

    NOTA: para dificultar la respuesta, se deben seleccionar interpretes del mismo pais.
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion_aleatoria = parametros.participacion_aleatoria(1)[0]
        self._url = participacion_aleatoria["url_youtube"]
        self._respuesta = participacion_aleatoria["artista"]

        pais_participando = participacion_aleatoria["pais"]
        artistas_pais = list(parametros.agregacion([
            {"$unwind": "$concursantes"},
            {"$match": {
                "concursantes.pais": pais_participando}},  # me quedo solo con las participaciones del pais
            {"$project": {
                "_id": 0,
                "artista": "$concursantes.artista"  # me quedo solo con sus artistas
            }},
            {"$group": {
                "_id": "$concursantes.artista"  #para evitar repetidos
            }}
        ]))

        opciones_invalidas = []
        for artista in artistas_pais:
            if artista != self._respuesta and artista not in opciones_invalidas:
                opciones_invalidas.append(artista)
            if len(opciones_invalidas) == 3:
                break
        self._opciones_invalidas = opciones_invalidas

    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return f"¿Qué artista interpretó esta canción?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 4
