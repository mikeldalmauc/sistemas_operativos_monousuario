#!/bin/bash
# Instalador de «La Mazmorra de los Comandos».
#
#   bash instalar.sh
#
# Copia el juego a ~/.mazmorra, crea los comandos del grimorio (mirar, mapa,
# inventario, lanzar, pista, estado, mazmorra) y engancha el juego al terminal.
# No necesita sudo ni instala nada fuera de tu carpeta personal.

set -e

ORIGEN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$HOME/.mazmorra"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Hace falta python3 y no lo encuentro. En Linux Mint:  sudo apt install python3"
    exit 1
fi

if [ ! -d "$ORIGEN/mazmorra" ]; then
    echo "No encuentro la carpeta mazmorra/ junto a este instalador. ¿Has descomprimido el zip entero?"
    exit 1
fi

mkdir -p "$DESTINO/bin" "$DESTINO/juego"
rm -rf "$DESTINO/juego/mazmorra"
cp -r "$ORIGEN/mazmorra" "$DESTINO/juego/"
cp "$ORIGEN/mazmorra/mazmorra.sh" "$DESTINO/mazmorra.sh"

# Un comando por cada orden del grimorio. Son programas de verdad: por eso
# funcionan desde cualquier carpeta, igual que ls o cat.
for orden in mirar mapa inventario lanzar pista estado; do
    cat > "$DESTINO/bin/$orden" <<EOF
#!/bin/bash
PYTHONPATH="\$HOME/.mazmorra/juego" exec python3 -m mazmorra $orden "\$@"
EOF
    chmod +x "$DESTINO/bin/$orden"
done
cat > "$DESTINO/bin/mazmorra" <<'EOF'
#!/bin/bash
PYTHONPATH="$HOME/.mazmorra/juego" exec python3 -m mazmorra "$@"
EOF
chmod +x "$DESTINO/bin/mazmorra"

LINEA='[ -f "$HOME/.mazmorra/mazmorra.sh" ] && source "$HOME/.mazmorra/mazmorra.sh"  # juego mazmorra'
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] || [ "$rc" = "$HOME/.bashrc" ]; then
        if ! grep -q "juego mazmorra" "$rc" 2>/dev/null; then
            printf '\n%s\n' "$LINEA" >> "$rc"
        fi
    fi
done

echo
echo "  Juego instalado en $DESTINO"
echo
echo "  Cierra este terminal y abre uno nuevo (o ejecuta:  source ~/.bashrc)."
echo "  Después escribe:      mazmorra iniciar"
echo
