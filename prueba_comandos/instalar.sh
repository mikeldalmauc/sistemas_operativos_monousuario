#!/usr/bin/env bash
# Instala la orden `prueba` para poder usarla desde cualquier carpeta. Ejecutar UNA vez, sin sudo:
#     bash instalar.sh            → instala
#     bash instalar.sh --quitar   → desinstala
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HOME/.local/bin"
ORDEN="$BIN/prueba"

if [ "${1:-}" = "--quitar" ]; then
  rm -f "$ORDEN" && echo "Orden 'prueba' eliminada."; exit 0
fi

mkdir -p "$BIN"
cat > "$ORDEN" <<EOF
#!/usr/bin/env bash
# Lanzador de las pruebas de comandos (creado por instalar.sh)
exec bash "$AQUI/prueba.sh" "\$@"
EOF
chmod +x "$ORDEN"

if ! echo ":$PATH:" | grep -q ":$BIN:"; then
  if ! grep -q 'prueba_comandos' "$HOME/.bashrc" 2>/dev/null; then
    printf '\n# prueba_comandos: la orden `prueba` disponible en cualquier carpeta\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
  fi
  echo "Añadido ~/.local/bin al PATH en ~/.bashrc."
  echo "Abre un terminal NUEVO (o ejecuta: source ~/.bashrc) y luego:   prueba iniciar 1"
else
  echo "Listo. Ya puedes usar:   prueba iniciar 1"
fi
