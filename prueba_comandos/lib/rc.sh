# Fichero de arranque del terminal de la prueba (bash --rcfile lib/rc.sh).
# Registra cada comando que escribes en .prueba/historial y define las órdenes especiales.

# Conserva tu configuración habitual (alias, colores…)
[ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc"

# --- registro de comandos (esto es lo que cuenta el marcador) ---
export HISTFILE="$PRUEBA_DIR/.prueba/historial"
HISTSIZE=10000
HISTFILESIZE=10000
HISTCONTROL=            # se registra todo, también los repetidos
unset HISTIGNORE HISTTIMEFORMAT
shopt -s histappend
# Guarda cada comando al instante. Si la carpeta de la prueba desaparece (borrar, rm…), avisa una vez.
_prueba_guardar() {
  if [ -d "$PRUEBA_DIR/.prueba" ]; then
    history -a
  elif [ -z "${_PRUEBA_AVISADO:-}" ]; then
    _PRUEBA_AVISADO=1
    echo "La carpeta de la prueba ($PRUEBA_DIR) ya no existe. Escribe 'salir' y vuelve a empezar con: prueba iniciar $PRUEBA_NIVEL"
  fi
}
PROMPT_COMMAND=_prueba_guardar

# --- prompt ---
PS1="\[\e[1;35m\][prueba N${PRUEBA_NIVEL}]\[\e[0m\] \[\e[1;34m\]\w\[\e[0m\] \$ "

# --- órdenes especiales ---
mision()    { bash "$PRUEBA_SH" mision "$PRUEBA_NIVEL"; }
comprobar() { history -a; bash "$PRUEBA_SH" _comprobar "$PRUEBA_NIVEL"; }
reiniciar() {
  cd "$HOME" || return
  bash "$PRUEBA_SH" _reiniciar "$PRUEBA_NIVEL" && { history -c; cd "$PRUEBA_DIR" || return; echo "Reloj a cero. ¡A por ello!"; }
}
salir()     { exit; }

cd "$PRUEBA_DIR" || return
