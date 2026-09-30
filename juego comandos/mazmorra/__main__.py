"""Punto de entrada:  python3 -m mazmorra ORDEN [args]

Los comandos cortos del alumno (mirar, mapa, lanzar...) son pequeños
envoltorios que llaman aquí con la orden correspondiente.
"""

import os
import sys

from . import motor


ORDENES = {
    "iniciar": motor.cmd_iniciar,
    "mirar": motor.cmd_mirar,
    "mapa": motor.cmd_mapa,
    "inventario": motor.cmd_inventario,
    "lanzar": motor.cmd_lanzar,
    "pista": motor.cmd_pista,
    "estado": motor.cmd_estado,
    "reiniciar": motor.cmd_reiniciar,
    "ritual": motor.cmd_ritual,
    "ayuda": motor.cmd_ayuda,
    "chuleta": motor.cmd_chuleta,
}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        return motor.cmd_ayuda([])
    orden, args = argv[0], argv[1:]
    if orden in ("-v", "--version", "version"):
        print(f"mazmorra {motor.VERSION}")
        return 0
    fn = ORDENES.get(orden)
    if fn is None:
        print(f"Orden desconocida: {orden}. Escribe  mazmorra ayuda")
        return 2
    try:
        return fn(args) or 0
    except KeyboardInterrupt:
        print()
        return 130
    except BrokenPipeError:
        # Salida cortada con | head o similar: no es un error del juego.
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        return 0
    except PermissionError as e:
        print(f"Permiso denegado: {e}. Si has tocado permisos a mano, prueba  mazmorra reiniciar sala")
        return 1


if __name__ == "__main__":
    sys.exit(main())
