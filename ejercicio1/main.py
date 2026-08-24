"""CLI del Ejercicio 1"""

import argparse
import sys
from pathlib import Path
from typing import List

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from ejercicio1.dibujar_afn import dibujar_afn
    from ejercicio1.regex import analizar
    from ejercicio1.simulador import acepta
    from ejercicio1.thompson import construir_afn
else:
    from .dibujar_afn import dibujar_afn
    from .regex import analizar
    from .simulador import acepta
    from .thompson import construir_afn


BASE_DIR = Path(__file__).resolve().parent


def leer_lineas(ruta: Path) -> List[str]:
    with ruta.open("r", encoding="utf-8") as archivo:
        return [linea.strip() for linea in archivo if linea.strip()]


def procesar_expresion(
    expresion: str,
    indice: int,
    cadena: str,
    carpeta_salida: Path,
    mostrar: bool,
) -> bool:
    tokens, con_concatenacion, postfix, ast = analizar(expresion)
    afn = construir_afn(ast)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_imagen = carpeta_salida / f"afn_{indice:02d}.png"
    dibujar_afn(afn, str(ruta_imagen), f"AFN de Thompson - expresion {indice}", mostrar)

    aceptada = acepta(afn, cadena)
    respuesta = "si" if aceptada else "no"
    print(f"Expresion {indice}: {expresion}")
    print(f"  Tokens:             {tokens}")
    print(f"  Con concatenacion:  {' '.join(con_concatenacion)}")
    print(f"  Postfix:             {' '.join(postfix)}")
    print(f"  Estados del AFN:     {len(afn.estados)}")
    print(f"  Cadena w:            {cadena if cadena else 'ε (vacia)'}")
    print(f"  w pertenece a L(r):  {respuesta}")
    print(f"  Grafo:               {ruta_imagen}")
    print()
    return aceptada


def obtener_cadenas(args: argparse.Namespace, cantidad: int) -> List[str]:
    if args.cadena is not None:
        return [args.cadena] * cantidad
    if args.cadenas is not None:
        cadenas = leer_lineas(Path(args.cadenas))
        if len(cadenas) != cantidad:
            raise ValueError(
                f"El archivo de cadenas debe tener {cantidad} lineas; tiene {len(cadenas)}."
            )
        return cadenas

    cadenas_ejemplo = BASE_DIR / "cadenas.txt"
    if not args.interactivo and cadenas_ejemplo.exists():
        cadenas = leer_lineas(cadenas_ejemplo)
        if len(cadenas) == cantidad:
            return cadenas

    return [input(f"Cadena w para la expresion {indice}: ") for indice in range(1, cantidad + 1)]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Construye y simula los AFN de Thompson de un archivo de regex."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        type=Path,
        default=BASE_DIR / "expresiones.txt",
        help="Archivo con una expresion regular por linea.",
    )
    grupo_cadena = parser.add_mutually_exclusive_group()
    grupo_cadena.add_argument("--cadena", help="Usa la misma cadena w para todas las expresiones.")
    grupo_cadena.add_argument("--cadenas", type=Path, help="Archivo con una cadena w por expresion.")
    parser.add_argument(
        "--salida",
        type=Path,
        default=BASE_DIR / "salidas",
        help="Carpeta para los dibujos del AFN.",
    )
    parser.add_argument(
        "--mostrar",
        action="store_true",
        help="Abre cada dibujo en una ventana de Matplotlib.",
    )
    parser.add_argument(
        "--interactivo",
        action="store_true",
        help="Solicita w en consola en lugar de usar cadenas.txt.",
    )
    args = parser.parse_args()

    expresiones = leer_lineas(args.archivo)
    if not expresiones:
        raise ValueError("El archivo de expresiones no contiene expresiones.")
    cadenas = obtener_cadenas(args, len(expresiones))

    for indice, (expresion, cadena) in enumerate(zip(expresiones, cadenas), start=1):
        procesar_expresion(expresion, indice, cadena, args.salida, args.mostrar)


if __name__ == "__main__":
    main()
