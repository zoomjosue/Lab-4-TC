"""Simulacion de un AFN mediante epsilon-cerradura."""

from typing import Iterable, Set

from .thompson import AFN


def cerradura_epsilon(afn: AFN, estados: Iterable[int]) -> Set[int]:
    """Obtiene todos los estados alcanzables usando solo epsilon."""

    visitados = set(estados)
    pila = list(visitados)

    while pila:
        actual = pila.pop()
        for transicion in afn.transiciones.get(actual, []):
            if transicion.simbolo is None and transicion.destino not in visitados:
                visitados.add(transicion.destino)
                pila.append(transicion.destino)
    return visitados


def mover(afn: AFN, estados: Iterable[int], simbolo: str) -> Set[int]:
    destinos: Set[int] = set()
    for estado in estados:
        for transicion in afn.transiciones.get(estado, []):
            if transicion.simbolo == simbolo:
                destinos.add(transicion.destino)
    return destinos


def normalizar_cadena(cadena: str) -> str:
    """Permite escribir epsilon como ``ε`` o ``epsilon`` en el archivo de entrada."""

    if cadena.strip().lower() in {"ε", "epsilon", "<epsilon>"}:
        return ""
    return cadena


def acepta(afn: AFN, cadena: str) -> bool:
    actuales = cerradura_epsilon(afn, {afn.inicio})
    for simbolo in normalizar_cadena(cadena):
        actuales = cerradura_epsilon(afn, mover(afn, actuales, simbolo))
        if not actuales:
            return False
    return afn.aceptacion in actuales
