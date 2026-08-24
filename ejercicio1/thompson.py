"""Construccion de AFN a partir de un AST usando Thompson."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .regex import EPSILON, Nodo, es_operando, simbolo_real


@dataclass(frozen=True)
class Transicion:
    origen: int
    destino: int
    simbolo: Optional[str]
    etiqueta: str


@dataclass
class AFN:
    inicio: int
    aceptacion: int
    transiciones: Dict[int, List[Transicion]] = field(default_factory=dict)
    estados: Set[int] = field(default_factory=set)

    def agregar_transicion(
        self, origen: int, destino: int, simbolo: Optional[str], etiqueta: str
    ) -> None:
        self.transiciones.setdefault(origen, []).append(
            Transicion(origen, destino, simbolo, etiqueta)
        )


@dataclass(frozen=True)
class Fragmento:
    inicio: int
    aceptacion: int


class ConstructorThompson:
    def __init__(self) -> None:
        self._siguiente_estado = 0
        self._transiciones: Dict[int, List[Transicion]] = {}
        self._estados: Set[int] = set()

    def nuevo_estado(self) -> int:
        estado = self._siguiente_estado
        self._siguiente_estado += 1
        self._estados.add(estado)
        return estado

    def epsilon(self, origen: int, destino: int) -> None:
        self.agregar_transicion(origen, destino, None, EPSILON)

    def agregar_transicion(
        self, origen: int, destino: int, simbolo: Optional[str], etiqueta: str
    ) -> None:
        self._transiciones.setdefault(origen, []).append(
            Transicion(origen, destino, simbolo, etiqueta)
        )

    def construir(self, nodo: Nodo) -> AFN:
        fragmento = self._construir_nodo(nodo)
        return AFN(
            inicio=fragmento.inicio,
            aceptacion=fragmento.aceptacion,
            transiciones=self._transiciones,
            estados=self._estados,
        )

    def _construir_nodo(self, nodo: Nodo) -> Fragmento:
        if es_operando(nodo.valor):
            inicio = self.nuevo_estado()
            aceptacion = self.nuevo_estado()
            if nodo.valor == EPSILON:
                self.epsilon(inicio, aceptacion)
            else:
                self.agregar_transicion(
                    inicio,
                    aceptacion,
                    simbolo_real(nodo.valor),
                    nodo.valor,
                )
            return Fragmento(inicio, aceptacion)

        if nodo.valor == ".":
            izquierda = self._construir_nodo(nodo.izquierda)  # type: ignore[arg-type]
            derecha = self._construir_nodo(nodo.derecha)  # type: ignore[arg-type]
            self.epsilon(izquierda.aceptacion, derecha.inicio)
            return Fragmento(izquierda.inicio, derecha.aceptacion)

        if nodo.valor == "|":
            izquierda = self._construir_nodo(nodo.izquierda)  # type: ignore[arg-type]
            derecha = self._construir_nodo(nodo.derecha)  # type: ignore[arg-type]
            inicio = self.nuevo_estado()
            aceptacion = self.nuevo_estado()
            self.epsilon(inicio, izquierda.inicio)
            self.epsilon(inicio, derecha.inicio)
            self.epsilon(izquierda.aceptacion, aceptacion)
            self.epsilon(derecha.aceptacion, aceptacion)
            return Fragmento(inicio, aceptacion)

        if nodo.valor == "*":
            hijo = self._construir_nodo(nodo.izquierda)  # type: ignore[arg-type]
            inicio = self.nuevo_estado()
            aceptacion = self.nuevo_estado()
            self.epsilon(inicio, hijo.inicio)
            self.epsilon(inicio, aceptacion)
            self.epsilon(hijo.aceptacion, hijo.inicio)
            self.epsilon(hijo.aceptacion, aceptacion)
            return Fragmento(inicio, aceptacion)

        raise ValueError(f"Operador AST no reconocido: {nodo.valor}")


def construir_afn(raiz: Nodo) -> AFN:
    return ConstructorThompson().construir(raiz)
