#!/bin/bash
# Quita el juego (~/.mazmorra y la línea de ~/.bashrc / ~/.zshrc).
# Las mazmorras creadas (~/mazmorra y ~/catacumbas) se borran solo si lo confirmas.

set -e
rm -rf "$HOME/.mazmorra"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [ -f "$rc" ] && sed -i '/# juego mazmorra$/d' "$rc"
done
echo "Juego desinstalado."
for d in "$HOME/mazmorra" "$HOME/catacumbas"; do
    if [ -d "$d" ]; then
        read -r -p "¿Borrar también $d? (s/N) " r
        if [ "$r" = "s" ] || [ "$r" = "S" ]; then
            chmod -R u+rwx "$d" && rm -rf "$d" && echo "Borrado $d"
        fi
    fi
done
