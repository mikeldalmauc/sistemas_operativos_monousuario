#!/usr/bin/env bash
# Administración del ranking (solo profesor). Se ejecuta en el servidor, desde la carpeta ranking/.
# Lee CLAVE_ADMIN de ranking/.env. Por defecto habla con http://localhost:8080 (variable URL para cambiarlo).
#
#   bash admin.sh listar [nivel]            lista los envíos (con su ID) de un nivel o de todos
#   bash admin.sh borrar ID [ID…]           borra uno o varios envíos por ID
#   bash admin.sh borrar-alumno "Nombre"    borra todos los envíos de ese alumno (todos los niveles)
#   bash admin.sh vaciar [nivel]            borra TODO (o todo un nivel). Pide confirmación.
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="${URL:-http://localhost:8080}"
[ -f "$AQUI/.env" ] && source "$AQUI/.env"
: "${CLAVE_ADMIN:?Falta CLAVE_ADMIN: crea ranking/.env a partir de .env.ejemplo}"

api() { curl -sS -m 10 -H "X-Clave-Admin: $CLAVE_ADMIN" "$@"; echo; }

case "${1:-}" in
  listar)
    for n in ${2:-1 2 3}; do
      echo "=== Nivel $n ==="
      curl -sS -m 10 "$URL/api/ranking/$n?texto=1" || echo "(no responde el servidor en $URL)"
    done ;;
  borrar)
    shift; [ $# -gt 0 ] || { echo "Falta el ID (lo ves con: bash admin.sh listar)"; exit 1; }
    for id in "$@"; do printf '%s → ' "$id"; api -X DELETE "$URL/api/resultados/$id"; done ;;
  borrar-alumno)
    [ -n "${2:-}" ] || { echo "Falta el nombre entre comillas"; exit 1; }
    api -X DELETE -G --data-urlencode "nombre=$2" "$URL/api/resultados" ;;
  vaciar)
    if [ -n "${2:-}" ]; then que="el nivel $2"; filtro="?nivel=$2"; else que="TODOS los niveles"; filtro=""; fi
    read -r -p "Vas a borrar todos los envíos de $que. Escribe SI para confirmar: " conf
    [ "$conf" = "SI" ] || { echo "Cancelado."; exit 0; }
    api -X DELETE "$URL/api/resultados$filtro" ;;
  *) sed -n '2,9p' "$0" | sed 's/^# \{0,2\}//' ;;
esac
