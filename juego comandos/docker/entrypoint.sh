#!/bin/bash
# Arranque del contenedor.
#
# La carpeta personal está en un volumen (para no perder la partida), así que
# el juego se (re)instala en cada arranque: si la imagen trae una versión nueva
# del juego, se actualiza ~/.mazmorra sin tocar ~/mazmorra ni ~/catacumbas.

set -e

# Un volumen recién creado con bind mount o tmpfs llega sin los ficheros de /etc/skel.
[ -f "$HOME/.bashrc" ] || cp /etc/skel/.bashrc "$HOME/.bashrc"

bash /opt/mazmorra-juego/instalar.sh >/dev/null

exec "$@"
