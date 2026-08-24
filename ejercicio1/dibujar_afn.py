"""Dibujo del AFN de Thompson usando Matplotlib."""

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

from .thompson import AFN, Transicion


def _niveles(afn: AFN) -> Dict[int, int]:
    niveles = {afn.inicio: 0}
    cola = deque([afn.inicio])
    while cola:
        actual = cola.popleft()
        for transicion in afn.transiciones.get(actual, []):
            if transicion.destino not in niveles:
                niveles[transicion.destino] = niveles[actual] + 1
                cola.append(transicion.destino)

    nivel_maximo = max(niveles.values(), default=0)
    for estado in sorted(afn.estados):
        niveles.setdefault(estado, nivel_maximo + 1)
    return niveles


def _posiciones(afn: AFN) -> Dict[int, Tuple[float, float]]:
    niveles = _niveles(afn)
    por_nivel: Dict[int, List[int]] = defaultdict(list)
    for estado, nivel in niveles.items():
        por_nivel[nivel].append(estado)

    posiciones: Dict[int, Tuple[float, float]] = {}
    for nivel, estados in por_nivel.items():
        estados.sort()
        centro = (len(estados) - 1) / 2
        for indice, estado in enumerate(estados):
            posiciones[estado] = (nivel * 2.7, (centro - indice) * 1.5)
    return posiciones


def _agrupar_transiciones(afn: AFN) -> Iterable[Tuple[int, int, List[Transicion]]]:
    agrupadas: Dict[Tuple[int, int], List[Transicion]] = defaultdict(list)
    for transiciones in afn.transiciones.values():
        for transicion in transiciones:
            agrupadas[(transicion.origen, transicion.destino)].append(transicion)
    return ((origen, destino, transiciones) for (origen, destino), transiciones in agrupadas.items())


def dibujar_afn(afn: AFN, ruta_salida: str, titulo: str, mostrar: bool = False) -> None:
    posiciones = _posiciones(afn)
    niveles = _niveles(afn)
    ancho = max(11.0, (max(niveles.values(), default=1) + 1) * 2.7)
    alto = max(6.0, (max(sum(1 for nivel in niveles.values() if nivel == n) for n in set(niveles.values())) + 1) * 1.35)

    figura, eje = plt.subplots(figsize=(ancho, alto))
    eje.set_title(titulo, fontsize=13, pad=18)
    eje.axis("off")

    for origen, destino, transiciones in _agrupar_transiciones(afn):
        x1, y1 = posiciones[origen]
        x2, y2 = posiciones[destino]
        if origen == destino:
            flecha = FancyArrowPatch(
                (x1, y1 + 0.28),
                (x1 + 0.01, y1 + 0.28),
                connectionstyle="arc3,rad=1.6",
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=1.2,
                color="#536878",
            )
            etiqueta_x, etiqueta_y = x1 + 0.3, y1 + 0.75
        else:
            diferencia = y2 - y1
            radio = 0.12 if abs(diferencia) < 0.2 else 0.0
            flecha = FancyArrowPatch(
                (x1 + 0.25, y1),
                (x2 - 0.25, y2),
                connectionstyle=f"arc3,rad={radio}",
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=1.2,
                color="#536878",
            )
            etiqueta_x = (x1 + x2) / 2
            etiqueta_y = (y1 + y2) / 2 + (0.16 if diferencia >= 0 else -0.16)
        eje.add_patch(flecha)
        etiqueta = ", ".join(transicion.etiqueta for transicion in transiciones)
        eje.text(
            etiqueta_x,
            etiqueta_y,
            etiqueta,
            fontsize=9,
            color="#203040",
            ha="center",
            va="center",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5},
        )

    for estado, (x, y) in posiciones.items():
        color = "#e8f1f8" if estado not in {afn.inicio, afn.aceptacion} else "#d7ead8"
        eje.add_patch(Circle((x, y), 0.28, facecolor=color, edgecolor="#1d4e6d", linewidth=1.5, zorder=3))
        if estado == afn.aceptacion:
            eje.add_patch(Circle((x, y), 0.21, facecolor="none", edgecolor="#1d4e6d", linewidth=1.2, zorder=4))
        eje.text(x, y, str(estado), ha="center", va="center", fontsize=9, zorder=5)

    inicio_x, inicio_y = posiciones[afn.inicio]
    eje.add_patch(
        FancyArrowPatch(
            (inicio_x - 1.25, inicio_y),
            (inicio_x - 0.3, inicio_y),
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=1.4,
            color="#193b52",
        )
    )
    eje.text(inicio_x - 1.25, inicio_y + 0.28, "inicio", fontsize=9, ha="center")

    eje.relim()
    eje.autoscale_view()
    eje.margins(x=0.08, y=0.12)
    figura.tight_layout()
    figura.savefig(ruta_salida, dpi=160, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(figura)
