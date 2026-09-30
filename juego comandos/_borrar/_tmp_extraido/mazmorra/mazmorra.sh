# Se carga desde ~/.bashrc y ~/.zshrc (lo hace instalar.sh).
#
# 1. Pone los comandos del grimorio en el PATH.
# 2. Al cambiar de carpeta dentro de una mazmorra, describe la sala automáticamente.
# 3. Completa con Tab los nombres de los hechizos.

export PATH="$HOME/.mazmorra/bin:$PATH"

__mazmorra_ultimo_pwd="$PWD"

__mazmorra_al_cambiar_de_sala() {
    [ "$PWD" = "$__mazmorra_ultimo_pwd" ] && return
    __mazmorra_ultimo_pwd="$PWD"
    case "$PWD" in
        "$HOME/mazmorra"|"$HOME/mazmorra/"*|"$HOME/catacumbas"|"$HOME/catacumbas/"*)
            mirar --auto ;;
    esac
}

if [ -n "$ZSH_VERSION" ]; then
    autoload -Uz add-zsh-hook 2>/dev/null
    add-zsh-hook chpwd __mazmorra_al_cambiar_de_sala 2>/dev/null
elif [ -n "$BASH_VERSION" ]; then
    case ";$PROMPT_COMMAND;" in
        *";__mazmorra_al_cambiar_de_sala;"*) ;;
        *) PROMPT_COMMAND="__mazmorra_al_cambiar_de_sala${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
    esac
    __mazmorra_completar_lanzar() {
        local actual="${COMP_WORDS[COMP_CWORD]}"
        local nombres
        nombres=$(ls "$HOME/mazmorra/inventario" 2>/dev/null | sed -n 's/\.txt$//p')
        COMPREPLY=($(compgen -W "$nombres" -- "$actual"))
    }
    complete -F __mazmorra_completar_lanzar lanzar
fi
