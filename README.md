# Laboratorio 4 - Teoría de la Computación

Este repositorio contiene el Ejercicio 1 del Laboratorio 4. El programa integra
los resultados de los laboratorios anteriores:

1. Expande los operadores `+` y `?`.
2. Inserta la concatenación explícita y aplica Shunting Yard.
3. Construye el árbol abstracto sintáctico.
4. Construye el AFN equivalente mediante el algoritmo de Thompson.
5. Simula el AFN con epsilon-cerradura para decidir si `w` pertenece a `L(r)`.
6. Genera una imagen del AFN con estado inicial, estado de aceptación y transiciones.

## Requisitos

- Python 3.8 o superior.
- Matplotlib instalado en el entorno de Python.

Si todavía no está instalado, puede instalarse con:

```bash
python -m pip install matplotlib
```

## Ejecución

El archivo `ejercicio1/expresiones.txt` contiene las cuatro expresiones del
enunciado y `ejercicio1/cadenas.txt` contiene una cadena de prueba para cada
expresión. Para ejecutar el caso completo:

```bash
python -m ejercicio1.main
```

También se puede ejecutar directamente desde la carpeta:

```bash
cd ejercicio1
python main.py
```

Los grafos se guardan en `ejercicio1/salidas/afn_01.png` hasta
`afn_04.png`. Para mostrar cada grafo en una ventana de Matplotlib:

```bash
python -m ejercicio1.main --mostrar
```

Para probar una misma cadena contra todas las expresiones:

```bash
python -m ejercicio1.main --cadena abb
```

Para usar una cadena diferente por expresión:

```bash
python -m ejercicio1.main --cadenas ejercicio1/cadenas.txt
```

El símbolo `ε` en `cadenas.txt` representa la cadena vacía. También se acepta
`epsilon` o `<epsilon>`.

## Estructura

```text
ejercicio1/
  regex.py          Parser, expansión, Shunting Yard y AST
  thompson.py       Construcción del AFN
  simulador.py      Epsilon-cerradura y reconocimiento de cadenas
  dibujar_afn.py    Visualización del grafo con Matplotlib
  main.py           Interfaz de línea de comandos
  expresiones.txt   Expresiones indicadas en el laboratorio
  cadenas.txt       Cadenas de demostración
```

## Video

