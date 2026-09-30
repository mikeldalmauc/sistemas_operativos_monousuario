"""Colores ANSI para el terminal, sin dependencias.

Se desactivan solos si la salida no es un terminal (por ejemplo, si se
redirige a un fichero) o si existe la variable de entorno NO_COLOR.
"""

import os
import re
import sys

_CODIGOS = {
    "reset": 0, "negrita": 1, "tenue": 2, "cursiva": 3, "subrayado": 4,
    "parpadeo": 5, "inverso": 7,
    "negro": 30, "rojo": 31, "verde": 32, "amarillo": 33, "azul": 34,
    "magenta": 35, "cian": 36, "blanco": 37, "gris": 90,
    "rojo+": 91, "verde+": 92, "amarillo+": 93, "azul+": 94,
    "magenta+": 95, "cian+": 96, "blanco+": 97,
}

_RE_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _detectar() -> bool:
    if os.environ.get("MAZMORRA_COLOR") == "1":
        return True
    if os.environ.get("NO_COLOR") or os.environ.get("MAZMORRA_COLOR") == "0":
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


ACTIVO = _detectar()


def c(texto, *estilos):
    """Devuelve `texto` envuelto en los códigos ANSI de los estilos dados."""
    if not ACTIVO or not estilos:
        return str(texto)
    codigos = ";".join(str(_CODIGOS[e]) for e in estilos)
    return f"\x1b[{codigos}m{texto}\x1b[0m"


def sin_ansi(texto: str) -> str:
    return _RE_ANSI.sub("", texto)


def ancho(texto: str) -> int:
    """Ancho visible de un texto (ignora los códigos de color)."""
    return len(sin_ansi(texto))


def rellenar(texto: str, n: int, alinear: str = "<") -> str:
    """Rellena con espacios hasta `n` columnas visibles."""
    falta = n - ancho(texto)
    if falta <= 0:
        return texto
    if alinear == "^":
        izq = falta // 2
        return " " * izq + texto + " " * (falta - izq)
    if alinear == ">":
        return " " * falta + texto
    return texto + " " * falta


# Atajos semánticos: así el resto del código habla de "qué es" y no de "qué color".
def titulo(t):
    return c(t, "negrita", "amarillo+")


def ok(t):
    return c(t, "verde+")


def mal(t):
    return c(t, "rojo+")


def aviso(t):
    return c(t, "amarillo")


def cmd(t):
    """Un comando que el alumno debe teclear."""
    return c(t, "negrita", "cian+")


def magia(t):
    return c(t, "negrita", "magenta+")


def tenue(t):
    return c(t, "gris")


def carpeta(t):
    return c(t, "negrita", "azul+")


def fichero(t):
    return c(t, "amarillo")
