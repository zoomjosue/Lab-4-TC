"""Analisis de expresiones regulares para el Ejercicio 1.

La expresion se transforma en cuatro representaciones:

    infix -> tokens -> expansion de + y ? -> postfix -> AST

Los simbolos escapados, por ejemplo ``\\(``, se conservan como un solo token.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


EPSILON = "ε"
BINARY_OPERATORS = {"|", "."}
POSTFIX_OPERATORS = {"*"}
ALL_OPERATORS = BINARY_OPERATORS | POSTFIX_OPERATORS
PRECEDENCE = {"|": 1, ".": 2, "*": 3}


@dataclass
class Nodo:
    """Nodo del arbol abstracto sintactico de una expresion regular."""

    valor: str
    izquierda: Optional["Nodo"] = None
    derecha: Optional["Nodo"] = None


def tokenizar(regex: str) -> List[str]:
    """Convierte la expresion en tokens de un caracter o escapados."""

    tokens: List[str] = []
    indice = 0
    while indice < len(regex):
        caracter = regex[indice]
        if caracter.isspace():
            indice += 1
            continue
        if caracter == "\\":
            if indice + 1 >= len(regex):
                raise ValueError("La expresion termina con una barra invertida.")
            tokens.append(regex[indice : indice + 2])
            indice += 2
            continue
        tokens.append(caracter)
        indice += 1
    return tokens


def expandir_extensiones(tokens: List[str]) -> List[str]:
    """Expande ``A+`` como ``AA*`` y ``A?`` como ``(A|ε)``."""

    expandidos, indice, cerro_grupo = _expandir_secuencia(tokens, 0, dentro_grupo=False)
    if cerro_grupo:
        raise ValueError("La expresion tiene un parentesis de cierre sin apertura.")
    if indice != len(tokens):
        raise ValueError("No se pudo consumir toda la expresion.")
    return expandidos


def _expandir_secuencia(
    tokens: List[str], indice: int, dentro_grupo: bool
) -> Tuple[List[str], int, bool]:
    resultado: List[str] = []

    while indice < len(tokens):
        token = tokens[indice]

        if token == ")":
            if dentro_grupo:
                return resultado, indice + 1, True
            return resultado, indice, True

        if token == "|":
            resultado.append(token)
            indice += 1
            continue

        if token in {"*", "+", "?"}:
            raise ValueError(f"Operador postfix '{token}' sin operando.")

        if token == "(":
            contenido, indice, cerro = _expandir_secuencia(tokens, indice + 1, True)
            if not cerro:
                raise ValueError("La expresion tiene un parentesis de apertura sin cierre.")
            if not contenido:
                raise ValueError("Los parentesis no pueden estar vacios.")
            atomos = ["("] + contenido + [")"]
        else:
            atomos = [token]
            indice += 1

        while indice < len(tokens) and tokens[indice] in {"*", "+", "?"}:
            operador = tokens[indice]
            indice += 1

            if operador == "*":
                atomos = atomos + ["*"]
            elif operador == "+":
                atomos = atomos + atomos.copy() + ["*"]
            else:
                atomos = ["("] + atomos + ["|", EPSILON, ")"]

        resultado.extend(atomos)

    return resultado, indice, False


def insertar_concatenacion(tokens: List[str]) -> List[str]:
    """Inserta ``.`` donde la concatenacion esta implicita."""

    if not tokens:
        return []

    resultado: List[str] = []
    for indice in range(len(tokens) - 1):
        actual = tokens[indice]
        siguiente = tokens[indice + 1]
        resultado.append(actual)
        if debe_concatenar(actual, siguiente):
            resultado.append(".")
    resultado.append(tokens[-1])
    return resultado


def debe_concatenar(actual: str, siguiente: str) -> bool:
    termina_expresion = actual not in {"(", "|", "."}
    inicia_expresion = siguiente not in {")",
        "|",
        "*",
        ".",
    }
    return termina_expresion and inicia_expresion


def es_operando(token: str) -> bool:
    return token not in ALL_OPERATORS and token not in {"(", ")"}


def infix_a_postfix(tokens: List[str]) -> List[str]:
    """Aplica Shunting Yard y devuelve una lista de tokens postfix."""

    pila: List[str] = []
    salida: List[str] = []

    for token in tokens:
        if es_operando(token):
            salida.append(token)
        elif token == "(":
            pila.append(token)
        elif token == ")":
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if not pila:
                raise ValueError("La expresion tiene parentesis desbalanceados.")
            pila.pop()
        elif token in ALL_OPERATORS:
            while (
                pila
                and pila[-1] != "("
                and PRECEDENCE[pila[-1]] >= PRECEDENCE[token]
            ):
                salida.append(pila.pop())
            pila.append(token)
        else:
            raise ValueError(f"Token no reconocido: {token}")

    while pila:
        if pila[-1] == "(":
            raise ValueError("La expresion tiene parentesis desbalanceados.")
        salida.append(pila.pop())
    return salida


def construir_ast(postfix: List[str]) -> Nodo:
    """Construye el AST a partir de la salida postfix."""

    pila: List[Nodo] = []
    for token in postfix:
        if es_operando(token):
            pila.append(Nodo(token))
        elif token == "*":
            if not pila:
                raise ValueError("No hay operando para el operador '*'.")
            pila.append(Nodo(token, izquierda=pila.pop()))
        elif token in BINARY_OPERATORS:
            if len(pila) < 2:
                raise ValueError(f"No hay operandos suficientes para '{token}'.")
            derecha = pila.pop()
            izquierda = pila.pop()
            pila.append(Nodo(token, izquierda=izquierda, derecha=derecha))
        else:
            raise ValueError(f"Token postfix no reconocido: {token}")

    if len(pila) != 1:
        raise ValueError("La expresion postfix no produjo un unico AST.")
    return pila[0]


def analizar(regex: str) -> Tuple[List[str], List[str], List[str], Nodo]:
    """Ejecuta todas las etapas heredadas de Lab-3."""

    tokens = tokenizar(regex)
    expandidos = expandir_extensiones(tokens)
    con_concatenacion = insertar_concatenacion(expandidos)
    postfix = infix_a_postfix(con_concatenacion)
    return tokens, con_concatenacion, postfix, construir_ast(postfix)


def simbolo_real(token: str) -> str:
    """Devuelve el caracter que debe consumir una transicion escapada."""

    if not token.startswith("\\"):
        return token
    escapes = {"n": "\n", "r": "\r", "t": "\t"}
    return escapes.get(token[1:], token[1:])
