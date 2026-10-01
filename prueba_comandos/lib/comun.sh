#!/usr/bin/env bash
# Funciones comunes a todos los niveles. No se ejecuta directamente.

# ---------- colores ----------
if [ -t 1 ]; then
  C_ROJO=$'\e[1;31m'; C_VERDE=$'\e[1;32m'; C_AMAR=$'\e[1;33m'; C_AZUL=$'\e[1;34m'
  C_MAG=$'\e[1;35m'; C_CIAN=$'\e[1;36m'; C_GRIS=$'\e[0;90m'; C_FIN=$'\e[0m'
else
  C_ROJO=; C_VERDE=; C_AMAR=; C_AZUL=; C_MAG=; C_CIAN=; C_GRIS=; C_FIN=
fi
ok()    { echo "${C_VERDE}✔${C_FIN} $*"; }
fallo() { echo "${C_ROJO}✘${C_FIN} $*"; }
aviso() { echo "${C_AMAR}!${C_FIN} $*"; }
error() { echo "${C_ROJO}ERROR:${C_FIN} $*" >&2; }
titulo(){ echo; echo "${C_MAG}══════════════════════════════════════════════════════════${C_FIN}"; echo "${C_MAG}  $*${C_FIN}"; echo "${C_MAG}══════════════════════════════════════════════════════════${C_FIN}"; }

# ---------- rutas ----------
dir_nivel()   { echo "$HOME/prueba_nivel$1"; }
dir_estado()  { echo "$(dir_nivel "$1")/.prueba"; }
# Cómo se invoca la prueba en los mensajes: `prueba` si está instalada (instalar.sh), si no `bash prueba.sh`
if [ "$(command -v prueba 2>/dev/null)" ] && grep -qs "$PRUEBA_RAIZ/prueba.sh" "$(command -v prueba)"; then PRUEBA_CMD="prueba"; else PRUEBA_CMD="bash prueba.sh"; fi
CONFIG="$PRUEBA_RAIZ/config.env"
# Lo que escribe el alumno (su nombre y sus resultados) va en la carpeta del repo si es
# escribible; si no (p. ej. clonado con sudo), en ~/.prueba_comandos para no bloquear la prueba.
if [ -w "$PRUEBA_RAIZ" ]; then DATOS_ALUMNO="$PRUEBA_RAIZ"; else DATOS_ALUMNO="$HOME/.prueba_comandos"; fi
CONFIG_LOCAL="$DATOS_ALUMNO/config.local.env"
RESULTADOS="$DATOS_ALUMNO/resultados"

requiere_nivel() {
  case "${1:-}" in 1|2|3) return 0 ;; esac
  error "Indica el nivel: 1, 2 o 3.   Ejemplo:  $PRUEBA_CMD iniciar 1"; exit 1
}
cargar_nivel() { # shellcheck disable=SC1090
  source "$PRUEBA_RAIZ/lib/nivel$1.sh"; }

# ---------- configuración ----------
cargar_config() {
  NOMBRE_ALUMNO=""; SERVIDOR_URL=""; CLAVE=""; ENVIAR="si"
  [ -f "$CONFIG" ]       && source "$CONFIG"
  [ -f "$CONFIG_LOCAL" ] && source "$CONFIG_LOCAL"
}
pedir_nombre() {
  cargar_config
  if [ -z "$NOMBRE_ALUMNO" ]; then
    echo "${C_CIAN}¿Cómo te llamas? (nombre y apellido, aparecerá en el ranking):${C_FIN}"
    read -r -p "> " NOMBRE_ALUMNO
    NOMBRE_ALUMNO="$(echo "$NOMBRE_ALUMNO" | sed 's/^ *//;s/ *$//')"
    [ -n "$NOMBRE_ALUMNO" ] || { error "Necesito un nombre."; exit 1; }
    mkdir -p "$DATOS_ALUMNO" 2>/dev/null
    if printf 'NOMBRE_ALUMNO="%s"\n' "$NOMBRE_ALUMNO" > "$CONFIG_LOCAL"; then
      ok "Guardado en $CONFIG_LOCAL (edítalo si te equivocas)."
    else
      error "No puedo escribir $CONFIG_LOCAL. ¿Has clonado el repositorio con sudo? Arréglalo con:"
      echo "    sudo chown -R \$USER:\$USER \"$PRUEBA_RAIZ\""; exit 1
    fi
  fi
}

# ---------- preparar / limpiar / entrar ----------
preparar_nivel() {
  local n="$1" d; d="$(dir_nivel "$n")"
  titulo "Preparando el nivel $n"
  mkdir -p "$(dir_estado "$n")"
  "nivel${n}_preparar" "$d" || { error "No se ha podido preparar el nivel $n."; return 1; }
  "nivel${n}_mision" > "$d/MISION.md"
  date +%s > "$(dir_estado "$n")/inicio"
  : > "$(dir_estado "$n")/historial"
  rm -f "$(dir_estado "$n")/completado"
  ok "Listo. Carpeta de trabajo: $d"
}
limpiar_nivel() {
  local n="$1" d; d="$(dir_nivel "$n")"
  titulo "Limpiando el nivel $n"
  "nivel${n}_limpiar" "$d"
  rm -rf "$d"
}
entrar_shell() {
  local n="$1"
  titulo "Nivel $n · ¡El reloj está en marcha!"
  echo "Órdenes especiales:  ${C_CIAN}mision${C_FIN} (ver enunciado) · ${C_CIAN}comprobar${C_FIN} · ${C_CIAN}reiniciar${C_FIN} · ${C_CIAN}salir${C_FIN}"
  echo "Todo lo demás es tu terminal de siempre. El enunciado también está en MISION.md"
  echo
  PRUEBA_NIVEL="$n" PRUEBA_DIR="$(dir_nivel "$n")" PRUEBA_SH="$PRUEBA_RAIZ/prueba.sh" \
    bash --rcfile "$PRUEBA_RAIZ/lib/rc.sh" -i
  echo; echo "Has salido de la prueba del nivel $n. Vuelve con:  $PRUEBA_CMD continuar $n"
}

# ---------- comprobación ----------
PASOS_OK=0; PASOS_TOTAL=0
paso() { # paso "descripción" comando [args…]   → el comando decide si el paso está hecho
  local desc="$1"; shift
  PASOS_TOTAL=$((PASOS_TOTAL+1))
  if "$@" >/dev/null 2>&1; then PASOS_OK=$((PASOS_OK+1)); ok "$desc"; else fallo "$desc"; fi
}
# predicados reutilizables
es_dir()          { [ -d "$1" ]; }
es_fichero()      { [ -f "$1" ]; }
no_existe()       { [ ! -e "$1" ]; }
contiene()        { grep -q -- "$2" "$1"; }            # contiene FICHERO PATRON
contiene_linea()  { grep -qx -- "$2" "$1"; }           # línea exacta
no_contiene()     { [ -f "$1" ] && ! grep -q -- "$2" "$1"; }
contenido_es()    { [ "$(cat "$1" 2>/dev/null)" = "$2" ]; }
contenido_limpio_es() { [ "$(tr -d ' \t\r' < "$1" 2>/dev/null | sed '/^$/d')" = "$2" ]; }
iguales()         { cmp -s "$1" "$2"; }
permisos_son()    { [ "$(stat -c %a "$1" 2>/dev/null)" = "$2" ]; }
propietario_es()  { [ "$(stat -c %U "$1" 2>/dev/null)" = "$2" ]; }
grupo_es()        { [ "$(stat -c %G "$1" 2>/dev/null)" = "$2" ]; }
ejecutable()      { [ -x "$1" ] && head -c 2 "$1" | grep -q '#!'; }
historial_usa()   { grep -qE "(^|[ |;&])$1( |$)" "$(dir_estado "$PRUEBA_NIVEL_ACTUAL")/historial"; }
existe_usuario()  { id "$1" >/dev/null 2>&1; }
existe_grupo()    { getent group "$1" >/dev/null 2>&1; }
usuario_en_grupo(){ id -nG "$1" 2>/dev/null | tr ' ' '\n' | grep -qx "$2"; }
usuario_no_en_grupo(){ existe_usuario "$1" && ! usuario_en_grupo "$1" "$2"; }
servicio_activo()   { systemctl is-active  --quiet "$1"; }
servicio_parado()   { ! systemctl is-active --quiet "$1"; }
servicio_habilitado(){ systemctl is-enabled --quiet "$1"; }
servicio_deshabilitado(){ [ "$(systemctl is-enabled "$1" 2>/dev/null)" = "disabled" ]; }
atributo()        { lsattr -d "$1" 2>/dev/null | awk '{print $1}' | grep -q "$2"; }

contar_comandos() { # cuenta las líneas del historial que son comandos reales
  grep -vE '^\s*$|^\s*(mision|comprobar|reiniciar|salir|exit|clear|history|estado)\s*$' "$1" | wc -l | tr -d ' '
}
calcular_puntos() { # tiempo_s num_comandos → puntos (misma fórmula que el servidor)
  echo $(( 100000 / ( $1 + 5 * $2 + 60 ) ))
}
formato_tiempo() { printf '%dm %02ds' $(( $1 / 60 )) $(( $1 % 60 )); }

comprobar_nivel() {
  local n="$1" d e inicio ahora t ncmd puntos
  d="$(dir_nivel "$n")"; e="$(dir_estado "$n")"
  export PRUEBA_NIVEL_ACTUAL="$n"
  [ -d "$d" ] || { error "No hay una prueba del nivel $n preparada."; return 1; }
  PASOS_OK=0; PASOS_TOTAL=0
  titulo "Comprobando el nivel $n"
  "nivel${n}_comprobar" "$d"
  echo
  inicio="$(cat "$e/inicio" 2>/dev/null || date +%s)"; ahora="$(date +%s)"; t=$(( ahora - inicio ))
  ncmd="$(contar_comandos "$e/historial")"
  if [ "$PASOS_OK" -lt "$PASOS_TOTAL" ]; then
    echo "  Pasos completados: ${C_AMAR}$PASOS_OK / $PASOS_TOTAL${C_FIN}   ·   tiempo: $(formato_tiempo "$t")   ·   comandos: $ncmd"
    echo "  Sigue con los pasos marcados con ✘ y vuelve a ejecutar ${C_CIAN}comprobar${C_FIN}."
    return 1
  fi
  puntos="$(calcular_puntos "$t" "$ncmd")"
  echo "${C_VERDE}  ★ ¡NIVEL $n COMPLETADO! ★${C_FIN}"
  echo "  Tiempo:   ${C_CIAN}$(formato_tiempo "$t")${C_FIN} ($t s)"
  echo "  Comandos: ${C_CIAN}$ncmd${C_FIN}"
  echo "  Puntos:   ${C_CIAN}$puntos${C_FIN}   (100000 / (segundos + 5·comandos + 60))"
  echo
  if [ -f "$e/completado" ]; then
    aviso "Este intento ya se envió. Para otro intento: ${C_CIAN}reiniciar${C_FIN}"
    return 0
  fi
  if guardar_resultado "$n" "$t" "$ncmd" "$puntos"; then
    echo "$t $ncmd $puntos" > "$e/completado"
    echo "  ¿Puedes hacerlo más rápido y con menos comandos? ${C_CIAN}reiniciar${C_FIN} y otra vez."
  else
    echo "  Arregla lo de arriba y vuelve a ejecutar ${C_CIAN}comprobar${C_FIN}: el intento no se ha perdido."
    return 1
  fi
}

# ---------- resultados: fichero local + envío al servidor ----------
json_escapar() { # escapa una cadena para JSON (sin comillas exteriores)
  sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/\\t/g' -e 's/\r//g' | awk 'BEGIN{ORS=""} NR>1{print "\\n"} {print}'
}
guardar_resultado() {
  local n="$1" t="$2" ncmd="$3" puntos="$4" e json fecha fich comandos
  e="$(dir_estado "$n")"; cargar_config
  [ -n "$NOMBRE_ALUMNO" ] || pedir_nombre
  fecha="$(date -Iseconds)"
  comandos="$(grep -vE '^\s*$|^\s*(mision|comprobar|reiniciar|salir|exit|clear|history|estado)\s*$' "$e/historial" \
              | while IFS= read -r l; do printf '"%s",' "$(printf '%s' "$l" | json_escapar)"; done)"
  comandos="[${comandos%,}]"
  json=$(printf '{"nombre":"%s","nivel":%s,"tiempo_s":%s,"num_comandos":%s,"puntos":%s,"fecha":"%s","usuario":"%s","equipo":"%s","comandos":%s}' \
         "$(printf '%s' "$NOMBRE_ALUMNO" | json_escapar)" "$n" "$t" "$ncmd" "$puntos" "$fecha" \
         "$(id -un)" "$(hostname 2>/dev/null | json_escapar)" "$comandos")
  mkdir -p "$RESULTADOS" 2>/dev/null || { error "No puedo crear $RESULTADOS."; return 1; }
  fich="$RESULTADOS/nivel${n}_$(date +%Y%m%d_%H%M%S).json"
  printf '%s\n' "$json" > "$fich" || { error "No puedo escribir en $RESULTADOS."; return 1; }
  ok "Resultado guardado en $fich"
  if [ "$ENVIAR" != "si" ]; then aviso "Envío desactivado en config.env (ENVIAR=$ENVIAR)."; return 0; fi
  [ -n "$SERVIDOR_URL" ] || { aviso "No hay SERVIDOR_URL en config.env; no se envía."; return 0; }
  command -v curl >/dev/null || { aviso "No tienes curl instalado; entrega el fichero JSON en Moodle."; return 0; }
  local resp
  if resp="$(curl -sS -m 10 -X POST "$SERVIDOR_URL/api/resultados" -H 'Content-Type: application/json' -H "X-Clave: $CLAVE" --data-binary "@$fich" 2>&1)" \
     && printf '%s' "$resp" | grep -q '"ok":true'; then
    local pos clave_ver
    pos="$(printf '%s' "$resp" | sed -n 's/.*"posicion":\([0-9]*\).*/\1/p')"
    clave_ver="$(printf '%s' "$resp" | sed -n 's/.*"clave_ver":"\([^"]*\)".*/\1/p')"
    ok "Enviado al ranking: posición ${pos:-?} del nivel $n"
    if [ -n "$clave_ver" ]; then
      echo "nivel$n $clave_ver $(date +%Y-%m-%d)" >> "$DATOS_ALUMNO/claves.txt"   # sobrevive a reiniciar
      echo
      echo "  ${C_AMAR}🔑 Clave del nivel $n: ${C_CIAN}$clave_ver${C_FIN}"
      echo "  Con ella puedes ver en la web los comandos de los envíos de este nivel (los tuyos y los de"
      echo "  los demás). Guárdala; también la verás con: ${C_CIAN}$PRUEBA_CMD estado${C_FIN}"
    fi
  else
    aviso "El ranking no ha aceptado el envío ($SERVIDOR_URL): ${resp:-sin respuesta}"
    echo "  Si no puedes arreglarlo, entrega el JSON en Moodle."
    return 1   # el intento no se marca como enviado: un próximo `comprobar` lo reintenta
  fi
}

mostrar_estado() {
  local n d e
  cargar_config
  titulo "Estado de las pruebas · ${NOMBRE_ALUMNO:-(sin nombre)}"
  for n in 1 2 3; do
    d="$(dir_nivel "$n")"; e="$(dir_estado "$n")"
    if [ ! -d "$d" ]; then echo "  Nivel $n: ${C_GRIS}sin empezar${C_FIN}"
    elif [ -f "$e/completado" ]; then read -r t c p < "$e/completado"; echo "  Nivel $n: ${C_VERDE}completado${C_FIN} en $(formato_tiempo "$t"), $c comandos, $p puntos"
    else echo "  Nivel $n: ${C_AMAR}en curso${C_FIN} ($(formato_tiempo $(( $(date +%s) - $(cat "$e/inicio" 2>/dev/null || date +%s) ))) desde el inicio)"
    fi
  done
  echo; echo "  Resultados guardados: $(ls "$RESULTADOS" 2>/dev/null | wc -l | tr -d ' ')  (en $RESULTADOS)"
  if [ -s "$DATOS_ALUMNO/claves.txt" ]; then
    echo "  🔑 Claves para ver comandos en la web (una por nivel completado):"
    for n in 1 2 3; do c="$(grep "^nivel$n " "$DATOS_ALUMNO/claves.txt" | tail -1 | cut -d' ' -f2)"; [ -n "$c" ] && echo "     nivel $n: ${C_CIAN}$c${C_FIN}"; done
  fi
}
