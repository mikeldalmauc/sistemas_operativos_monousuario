#!/usr/bin/env bash
# =============================================================================
#  Pruebas de comandos · Sistemas Operativos Monopuesto (SMR 1.º)
#  Punto de entrada único. Uso:  bash prueba.sh ORDEN [NIVEL]
#
#    iniciar   N   prepara el nivel N desde cero y abre el terminal de la prueba
#    continuar N   vuelve a entrar en una prueba ya empezada (el reloj sigue)
#    reiniciar N   borra tu trabajo del nivel N, lo prepara de nuevo y entra
#    borrar    N   elimina todo lo del nivel N (ficheros, usuarios, servicios…)
#    estado        muestra en qué punto está cada nivel
#    mision    N   imprime el enunciado del nivel N sin entrar
#    ayuda         esta ayuda
#
#  Dentro del terminal de la prueba tienes:  mision · comprobar · reiniciar · salir
# =============================================================================
set -u

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PRUEBA_RAIZ="$AQUI"
# shellcheck source=lib/comun.sh
source "$AQUI/lib/comun.sh"

orden="${1:-ayuda}"
nivel="${2:-}"

case "$orden" in
  iniciar)    requiere_nivel "$nivel"; cargar_nivel "$nivel"
              if [ -d "$(dir_nivel "$nivel")" ]; then
                aviso "Ya existe una prueba del nivel $nivel en $(dir_nivel "$nivel")."
                echo   "  · Para seguir con ella:      bash prueba.sh continuar $nivel"
                echo   "  · Para empezar desde cero:   bash prueba.sh reiniciar $nivel"
                exit 1
              fi
              pedir_nombre
              preparar_nivel "$nivel" && entrar_shell "$nivel" ;;
  continuar)  requiere_nivel "$nivel"; cargar_nivel "$nivel"
              [ -d "$(dir_nivel "$nivel")" ] || { error "No hay ninguna prueba del nivel $nivel empezada. Usa: bash prueba.sh iniciar $nivel"; exit 1; }
              entrar_shell "$nivel" ;;
  reiniciar)  requiere_nivel "$nivel"; cargar_nivel "$nivel"
              pedir_nombre
              limpiar_nivel "$nivel" && preparar_nivel "$nivel" && entrar_shell "$nivel" ;;
  borrar)     requiere_nivel "$nivel"; cargar_nivel "$nivel"
              limpiar_nivel "$nivel" && ok "Nivel $nivel eliminado por completo." ;;
  estado)     mostrar_estado ;;
  mision)     requiere_nivel "$nivel"; cargar_nivel "$nivel"; "nivel${nivel}_mision" ;;
  # --- órdenes internas (las llama el terminal de la prueba) ---
  _comprobar) requiere_nivel "$nivel"; cargar_nivel "$nivel"; comprobar_nivel "$nivel" ;;
  _reiniciar) requiere_nivel "$nivel"; cargar_nivel "$nivel"; limpiar_nivel "$nivel" && preparar_nivel "$nivel" ;;
  ayuda|-h|--help|*) sed -n '2,15p' "$0" | sed 's/^# \{0,2\}//' ;;
esac
