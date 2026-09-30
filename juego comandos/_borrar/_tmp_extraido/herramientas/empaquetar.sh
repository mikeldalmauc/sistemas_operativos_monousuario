#!/bin/bash
# Genera el zip que se sube a Moodle para los alumnos.
# Solo incluye lo que el alumno necesita (el juego y el instalador):
# NI las soluciones NI el verificador de códigos.
#
# Uso:  bash herramientas/empaquetar.sh   →   dist/mazmorra-juego.zip

set -e
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"
mkdir -p dist
rm -f dist/mazmorra-juego.zip
rm -rf dist/mazmorra-juego
mkdir -p dist/mazmorra-juego
cp -r mazmorra instalar.sh desinstalar.sh docs/guia-alumno.md dist/mazmorra-juego/
find dist/mazmorra-juego -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
(cd dist && zip -qr mazmorra-juego.zip mazmorra-juego)
rm -rf dist/mazmorra-juego
echo "Creado: dist/mazmorra-juego.zip"
unzip -l dist/mazmorra-juego.zip
