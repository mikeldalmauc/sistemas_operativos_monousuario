#!/usr/bin/env bash
# NIVEL 3 · find, grep, scripts, atributos y configuración (3.er trimestre · CM4, CM6)
# Requiere: sudo, chattr/lsattr (e2fsprogs) sobre un sistema de ficheros ext4.

nivel3_preparar() {
  local d="$1" e="$1/.prueba" codigo i n sub
  command -v lsattr >/dev/null || { error "Este nivel necesita lsattr/chattr (paquete e2fsprogs)."; return 1; }
  echo "La preparación necesita sudo (sólo para comprobar que funciona)."
  sudo -v || return 1
  mkdir -p "$d/respuestas" "$d/scripts" "$e"
  mkdir -p "$d/bosque"/{norte/cueva,norte/rio,sur/aldea,sur/aldea/taberna,este,oeste/mina}

  codigo="TESORO-$(( 1000 + RANDOM % 9000 ))"
  echo "$codigo" > "$e/codigo"

  # ficheros de relleno: .txt, .cfg, .dat
  i=0
  for sub in norte norte/cueva norte/rio sur sur/aldea sur/aldea/taberna este oeste oeste/mina; do
    i=$((i+1))
    printf 'Notas de %s\nlinea 2\nlinea 3\n' "$sub" > "$d/bosque/$sub/notas$i.txt"
    printf 'opcion=%d\n' "$i"                      > "$d/bosque/$sub/ajustes$i.cfg"
  done
  # 7 ficheros .log repartidos
  n=0
  for sub in norte/cueva norte/rio sur/aldea sur/aldea/taberna este oeste/mina norte; do
    n=$((n+1)); printf 'registro %d\n' "$n" > "$d/bosque/$sub/evento$n.log"
  done
  echo "$n" > "$e/num_logs"
  # el tesoro, escondido en un fichero con nombre poco llamativo
  printf 'inventario de la taberna\nsillas: 12\nmesas: 4\ncodigo secreto: %s\nbarriles: 3\n' "$codigo" > "$d/bosque/sur/aldea/taberna/inventario.dat"
  # señuelos con formato parecido
  printf 'TESORO-falso no vale\nTESORO-12 tampoco\n' > "$d/bosque/este/rumores.txt"
  # el fichero más grande, con nombre nada evidente
  head -c 20000 /dev/urandom | base64 > "$d/bosque/oeste/mina/mapa_antiguo.dat"
  head -c 6000  /dev/urandom | base64 > "$d/bosque/norte/cueva/eco.dat"
  # ficheros con x que no deberían tenerlo
  chmod +x "$d/bosque/norte/notas1.txt" "$d/bosque/este/rumores.txt" "$d/bosque/sur/aldea/ajustes5.cfg" "$d/bosque/oeste/mina/mapa_antiguo.dat"
  # registro para chattr +a
  printf 'inicio del registro\n' > "$d/registro.log"
  return 0
}

nivel3_limpiar() {
  local d="$1"
  echo "La limpieza necesita sudo (quita atributos inmutables, el fichero de sudoers y el usuario ana)."
  sudo -v || return 1
  [ -e "$d/respuestas/tesoro.txt" ] && sudo chattr -i "$d/respuestas/tesoro.txt" 2>/dev/null
  [ -e "$d/registro.log" ]          && sudo chattr -a "$d/registro.log" 2>/dev/null
  sudo rm -f /etc/sudoers.d/ana /etc/sudoers.d/prueba* 2>/dev/null
  id ana >/dev/null 2>&1 && sudo userdel -r ana 2>/dev/null
  return 0
}

nivel3_mision() {
cat <<'EOF'
# NIVEL 3 · Buscar, scripts, atributos y configuración

Todo lo de los niveles 1 y 2 se da por sabido. Carpeta de trabajo: ~/prueba_nivel3
(tienes bosque/ con muchas subcarpetas, respuestas/, scripts/ y registro.log).

 1. En bosque/ hay ficheros .log repartidos por sus subcarpetas. Muévelos TODOS a la carpeta
    logs/ (créala en la raíz de la prueba). No debe quedar ningún .log dentro de bosque/.
 2. Algún fichero de bosque/ contiene un código con el formato  TESORO-  seguido de 4 cifras.
    Escribe SOLO el código en  respuestas/tesoro.txt  (cuidado: hay señuelos).
 3. Varios ficheros de bosque/ tienen permiso de ejecución sin necesitarlo. Quítaselo a todos
    los FICHEROS (las carpetas deben conservar el suyo o no podrás entrar).
 4. Averigua cuál es el fichero más grande de bosque/ y escribe su nombre (sin ruta) en
    respuestas/grande.txt .
 5. Escribe  scripts/contar.sh : recibe una carpeta como argumento e imprime SOLO un número:
    cuántos ficheros (no carpetas) hay dentro, incluyendo subcarpetas. Con shebang y ejecutable.
 6. Escribe  scripts/copia.sh : copia todos los .txt de bosque/ (de cualquier subcarpeta) a
    copia_seguridad/ , creando esa carpeta si no existe. Con shebang y ejecutable. Ejecútalo.
 7. Haz que  respuestas/tesoro.txt  sea INMUTABLE y que a  registro.log  solo se le pueda
    AÑADIR contenido (atributos especiales; necesitas sudo).
 8. Crea el usuario  ana  (si no existe) y, con un fichero en  /etc/sudoers.d/ , permite que
    ejecute  /usr/bin/systemctl  con sudo SIN contraseña. La sintaxis debe ser válida.

Puntuación: 100000 / (segundos + 5·comandos + 60).
EOF
}

_n3_probar_contar() { # crea un árbol temporal con 5 ficheros y comprueba que el script devuelve 5
  local s="$1" tmp; tmp="$(mktemp -d)"
  mkdir -p "$tmp/a/b" "$tmp/c"
  touch "$tmp/1" "$tmp/a/2" "$tmp/a/b/3" "$tmp/a/b/4" "$tmp/c/5"
  local out; out="$("$s" "$tmp" 2>/dev/null | tr -d ' \n')"
  rm -rf "$tmp"
  [ "$out" = "5" ]
}
_n3_probar_copia() { # ejecuta copia.sh y compara con los .txt reales de bosque/
  local d="$1" esperado real
  rm -rf "$d/copia_seguridad"
  ( cd "$d" && ./scripts/copia.sh >/dev/null 2>&1 ) || return 1
  esperado="$(find "$d/bosque" -type f -name '*.txt' -printf '%f\n' | sort)"
  real="$(find "$d/copia_seguridad" -type f -name '*.txt' -printf '%f\n' 2>/dev/null | sort)"
  [ -n "$real" ] && [ "$esperado" = "$real" ]
}

nivel3_comprobar() {
  local d="$1" codigo nlogs
  codigo="$(cat "$d/.prueba/codigo")"; nlogs="$(cat "$d/.prueba/num_logs")"
  echo "(la comprobación usa sudo para leer /etc/sudoers.d)"; sudo -v
  paso "1. Los $nlogs .log están en logs/ y ninguno queda en bosque/" \
       bash -c "[ \"\$(find '$d/logs' -maxdepth 1 -type f -name '*.log' 2>/dev/null | wc -l)\" -eq $nlogs ] && [ \"\$(find '$d/bosque' -type f -name '*.log' | wc -l)\" -eq 0 ]"
  paso "2. respuestas/tesoro.txt contiene el código correcto" \
       contenido_limpio_es "$d/respuestas/tesoro.txt" "$codigo"
  paso "3. Ningún fichero de bosque/ tiene permiso de ejecución (las carpetas sí)" \
       bash -c "[ \"\$(find '$d/bosque' -type f -perm /111 | wc -l)\" -eq 0 ] && [ \"\$(find '$d/bosque' -type d ! -perm -u+x | wc -l)\" -eq 0 ]"
  paso "4. respuestas/grande.txt dice mapa_antiguo.dat" \
       contenido_limpio_es "$d/respuestas/grande.txt" "mapa_antiguo.dat"
  paso "5. scripts/contar.sh ejecutable, con shebang, y cuenta bien" \
       bash -c "[ -x '$d/scripts/contar.sh' ] && head -c 2 '$d/scripts/contar.sh' | grep -q '#!' && $(declare -f _n3_probar_contar); _n3_probar_contar '$d/scripts/contar.sh'"
  paso "6. scripts/copia.sh ejecutable, con shebang, y copia todos los .txt a copia_seguridad/" \
       bash -c "[ -x '$d/scripts/copia.sh' ] && head -c 2 '$d/scripts/copia.sh' | grep -q '#!' && $(declare -f _n3_probar_copia); _n3_probar_copia '$d'"
  paso "7. tesoro.txt inmutable (i) y registro.log solo-añadir (a)" \
       bash -c "lsattr -d '$d/respuestas/tesoro.txt' | awk '{print \$1}' | grep -q i && lsattr -d '$d/registro.log' | awk '{print \$1}' | grep -q a"
  paso "8. Usuario ana con sudo sin contraseña para /usr/bin/systemctl en /etc/sudoers.d (sintaxis válida)" \
       bash -c "id ana >/dev/null 2>&1 && sudo visudo -c -q && sudo grep -rhE '^[[:space:]]*ana[[:space:]].*NOPASSWD:.*(/usr/bin/|/bin/)systemctl' /etc/sudoers.d/ | grep -q ."
}
