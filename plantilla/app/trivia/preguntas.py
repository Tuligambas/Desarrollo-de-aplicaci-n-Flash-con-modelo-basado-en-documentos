"""
Modulo que contiene diferentes modelos de consulta para la seccion de "trivia".
"""
import random
from typing import List
from abc import ABC, abstractmethod
from .operaciones_coleccion import OperacionesEurovision


# Clases para encapsular las preguntas y respuestas generadas aleatoriamente
class Trivia(ABC):
    """
    Clase abstracta con los metodos que deben implementar todas las preguntas de trivia.
    """
    @abstractmethod
    def __init__(self, parametros: OperacionesEurovision):
        # Obligamos a que todos los constructores les pasen un objeto con los parametros aleatorios
        pass

    @property
    @abstractmethod
    def pregunta(self) -> str:
        """
        Pregunta que se debe mostrar
        """
        pass

    @property
    @abstractmethod
    def opciones_invalidas(self) -> List[str]:
        """
        Lista de opciones invalidas. Deben ser exactamente 3
        """
        pass

    @property
    @abstractmethod
    def respuesta(self) -> str:
        """
        Respuesta correcta
        """
        pass

    @property
    @abstractmethod
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        pass

    def to_dict(self):
        # Sorteamos aleatoriamente las respuestas
        respuestas = [self.respuesta, *self.opciones_invalidas]
        random.shuffle(respuestas)

        # Funcion que genera la informacion que pasamos al script de trivia en el formato adecuado
        return {"pregunta": self.pregunta,
                "correcta": respuestas.index(self.respuesta),
                "respuestas": respuestas,
                "puntuacion": self.puntuacion,
                "tipo": "pregunta"}


class PrimerAnyoParticipacion(Trivia):
    """
    Pregunta que anyo fue el primero en el que participo un pais seleccionado aleatoriamente
    """

    def __init__(self, parametros: OperacionesEurovision):
        #busco utilizando las funciones auxiliares un pais aleatorio sobre el que hacer la pregunta
        self.pais = parametros.paises_participantes_aleatorios(1)[0]

        #cojo el año de participacion del pais
        #parecido a numero_peliculas_por_categorias!!!!
        agregacion = list(parametros.agregacion([
            {"$unwind": "$concursantes"},
            {"$match": {"concursantes.pais": self.pais}},
            {"$group": {
                "_id": "$concursantes.pais",
                "primer_anyo": {
                    "$min": "$anyo"}}}
        ]))
        self._respuesta = agregacion[0]["primer_anyo"]

        opciones = parametros.anyo_aleatorio(50)
        opciones_invalidas = []
        for anyo in opciones:
            if anyo != self._respuesta and anyo not in opciones_invalidas:
                opciones_invalidas.append(anyo)
            if len(opciones_invalidas) == 3:
                break

        self._opciones_invalidas = opciones_invalidas

    @property
    def pregunta(self) -> str:
        return f"¿En qué año participó por primera vez {self.pais}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 2


class CancionPais(Trivia):
    """
    Pregunta de que pais es el interprete de una cancion, dada el titulo de la cancion
    """

    def __init__(self, parametros: OperacionesEurovision):
        # Obtenemos una participacion para la respuesta
        participacion_aleatoria = parametros.paises_participantes_aleatorios(1)[0]
        self._respuesta = participacion_aleatoria["pais"]
        self._cancion = participacion_aleatoria["cancion"]

        #saco posibles paises y aplico la misma logica que antes
        opciones = parametros.paises_participantes_aleatorios(50)
        opciones_invalidas = []
        for pais in opciones:
            if pais != self._respuesta and pais not in opciones_invalidas:
                opciones_invalidas.append(pais)
            if len(opciones_invalidas) == 3:
                break

        self._opciones_invalidas = opciones_invalidas

    @property
    def pregunta(self) -> str:
        return f"¿De que país es el intérprete de la canción '{self._cancion}'?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 1


class MejorClasificacion(Trivia):
    """
    Pregunta: ¿Que cancion/pais obtuvo la mejor posicion en un anyo dado?

    Respuesta: las respuestas deben ser de la forma cancion/pais.

    IMPORTANTE: la solucion debe ser unica. Ademas, todos las opciones
    deben haber participado el mismo anyo.
    """
    def __init__(self, parametros: OperacionesEurovision):
        self._anyo = parametros.anyo_aleatorio(1)[0]
        agregacion_ordenada = list(parametros.agregacion([
                {"$match": {"anyo": self._anyo}},
                {"$unwind": "$concursantes"},
                {"$project": {
                    "_id": 0,
                    "resultado": "$concursantes.resultado",
                    "respuesta": {"$concat": ["$concursantes.cancion", " / ", "$concursantes.pais"]}
                }},
                {"$sort": {"resultado": 1}}
            ]))
        self._respuesta = agregacion_ordenada[0]["respuesta"]

        #igual pero sin ordenar para que las 3 opciones invalidas no sean las otras 3 mejores
        agregacion_desordenada = list(parametros.agregacion([
                {"$match": {"anyo": self._anyo}},
                {"$unwind": "$concursantes"},
                {"$project": {
                    "_id": 0,
                    "resultado": "$concursantes.resultado",
                    "respuesta": {"$concat": ["$concursantes.cancion", " / ", "$concursantes.pais"]}
                }}
        ]))

        self._opciones_invalidas = []
        for i in agregacion_desordenada:
            opcion = i["respuesta"]
            if opcion != self.respuesta and opcion not in self._opciones_invalidas:
                self._opciones_invalidas.append(opcion)
            if len(self._opciones_invalidas) == 3:
                break

    @property
    def pregunta(self) -> str:
        return f"¿Que canción/país obtuvo la mejor posición en {self._anyo}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 3


class MejorMediaPuntos(Trivia):
    """
    Pregunta que pais ha tenido mejor media de resultados en un periodo determinado.

    IMPORTANTE: la solucion debe ser unica.
    """
    def __init__(self, parametros: OperacionesEurovision):
        aux = parametros.anyo_aleatorio(2)
        if aux[0]<aux[1]:
            self._anyo_inicial = aux[0]
            self._anyo_final = aux[1]
        else:
            self._anyo_inicial = aux[1]
            self._anyo_final = aux[0]

        agregacion_ordenada = list(parametros.agregacion([
            {"$match": {"anyo": {"$gte": self._anyo_inicial, "$lte": self._anyo_final}}},
            {"$unwind": "$concursantes"},
            {"$group": {
                "_id": "$concursantes.pais",
                "media_resultado": {"$avg": "$concursantes.resultado"}
            }},
            {"$project": {
                "_id": 0,
                "pais": "$_id",
                "media_resultado": 1
            }},
            {"$sort": {"media_resultado": 1}}  # menor media = mejor
            ]))
        self._respuesta = agregacion_ordenada[0]["pais"]

        agregacion_desordenada = list(parametros.agregacion([
            {"$match": {"anyo": {"$gte": self._anyo_inicial, "$lte": self._anyo_final}}},
            {"$unwind": "$concursantes"},
            {"$group": {
                "_id": "$concursantes.pais",
                "media_resultado": {"$avg": "$concursantes.resultado"}
            }},
            {"$project": {
                "_id": 0,
                "pais": "$_id",
                "media_resultado": 1
            }}
        ]))
        self._opciones_invalidas = []
        for fila in agregacion_desordenada:
            opcion = fila["pais"]
            if opcion != self._respuesta and opcion not in self._opciones_invalidas:
                self._opciones_invalidas.append(opcion)
            if len(self._opciones_invalidas) == 3:
                break


    @property
    def pregunta(self) -> str:
        return f"¿Qué país quedó mejor posicionado de media entre los años {self._anyo_inicial} y {self._anyo_final}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 4
