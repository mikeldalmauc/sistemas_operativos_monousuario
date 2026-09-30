#!/usr/bin/env python3
"""Comprueba el código de un certificado entregado por un alumno.

Uso:
    python3 verificar_codigo.py certificado_nivel1.txt      (lee el fichero entregado)
    python3 verificar_codigo.py "Ane Ejemplo" 1 3 3B958843  (nombre, nivel, pistas, código)

El código es un resumen (hash) de nombre + nivel + pistas usadas + la frase
SECRETO de mazmorra/motor.py. Si el alumno cambia cualquiera de esos datos
en el certificado, el código deja de cuadrar.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mazmorra.motor import codigo_certificado  # noqa: E402


def desde_fichero(ruta: str):
    texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
    campos = {}
    for clave, patron in [("nombre", r"Aprendiz:\s*(.+)"), ("nivel", r"Nivel (\d+) superado"),
                          ("pistas", r"Pistas usadas:\s*(\d+)"), ("codigo", r"Código:\s*([0-9A-F]{8})")]:
        m = re.search(patron, texto)
        if not m:
            print(f"No encuentro el campo «{clave}» en {ruta}. ¿Es un certificado del juego?")
            sys.exit(2)
        campos[clave] = m.group(1).strip()
    return campos["nombre"], int(campos["nivel"]), int(campos["pistas"]), campos["codigo"]


def main(argv):
    if len(argv) == 2 and Path(argv[1]).is_file():
        nombre, nivel, pistas, codigo = desde_fichero(argv[1])
    elif len(argv) == 5:
        nombre, nivel, pistas, codigo = argv[1], int(argv[2]), int(argv[3]), argv[4].upper()
    else:
        print(__doc__)
        return 2
    esperado = codigo_certificado(nivel, nombre, pistas)
    print(f"Aprendiz: {nombre} · nivel {nivel} · pistas {pistas}")
    if esperado == codigo.upper():
        print(f"VÁLIDO   ({codigo})")
        return 0
    print(f"NO VÁLIDO: el código {codigo} no cuadra (esperaba {esperado}). "
          f"Nombre, nivel o pistas no coinciden con lo que generó el juego.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
