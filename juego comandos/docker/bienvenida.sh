# Se carga desde /etc/bash.bashrc en cada terminal interactivo del contenedor.
# Solo avisa mientras no exista ninguna mazmorra: después ya guía el juego.

case "$-" in
    *i*)
        if [ ! -d "$HOME/mazmorra" ] && [ ! -d "$HOME/catacumbas" ]; then
            echo
            echo "  La Mazmorra de los Comandos"
            echo
            echo "  Para empezar:     mazmorra iniciar"
            echo "  Después entra:    cd ~/mazmorra/entrada"
            echo "  Ayuda:            mazmorra ayuda"
            echo "  Salir:            exit   (la partida se guarda)"
            echo
        fi
        ;;
esac
