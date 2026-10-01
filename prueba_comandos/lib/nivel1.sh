#!/usr/bin/env bash
# NIVEL 1 · Ficheros y carpetas (1.er trimestre · CM3, CM4)
# Navegar, crear, leer, escribir, copiar, mover, borrar, nano y un toque de /etc.

PALABRAS=(cometa brujula faro glaciar bosque nutria tormenta pantera volcan trueno)

nivel1_preparar() {
  local d="$1" e="$1/.prueba" palabra i
  mkdir -p "$d/datos" "$d/pistas" "$d/basura/vieja" "$e"
  palabra="${PALABRAS[$(( RANDOM % ${#PALABRAS[@]} ))]}"
  echo "$palabra" > "$e/palabra"

  printf 'Informe trimestral del taller\n=============================\nEquipos revisados: 14\nEquipos pendientes: 3\nObservaciones: ninguna\n' > "$d/datos/informe.txt"
  printf 'JPEGdata-%s\n' 1 > "$d/datos/foto1.jpg"
  printf 'JPEGdata-%s\n' 2 > "$d/datos/foto2.jpg"
  printf 'PNGdata\n'       > "$d/datos/foto3.png"
  printf 'temporal\n'      > "$d/datos/borrame.tmp"
  printf '[general]\nnombre=taller\nmodo=lento\nidioma=es\n' > "$d/datos/config.ini"

  {
    echo "Este fichero tiene 12 lineas."
    echo "La palabra clave NO esta en esta linea."
    echo "Tampoco en esta."
    echo "Sigue buscando, pero no la copies a mano si puedes evitarlo."
    echo "Pista: head y tail te ayudan a ver lineas concretas."
    echo "Ya casi."
    echo "clave: $palabra"
    echo "La linea de arriba es la buena."
    echo "Aqui hay otra palabra falsa: dinosaurio"
    echo "Y otra: tostadora"
    echo "Fin de las pistas."
    echo "Ultima linea."
  } > "$d/pistas/secreto.txt"

  for i in 1 2 3; do echo "basura $i" > "$d/basura/papel$i.txt"; done
  echo "muy vieja" > "$d/basura/vieja/cosa.txt"
  return 0
}

nivel1_limpiar() {
  # deshacer el cambio en /etc/hosts si se hizo
  if grep -q 'prueba.local' /etc/hosts 2>/dev/null; then
    echo "Retirando la línea prueba.local de /etc/hosts (pide sudo)…"
    sudo sed -i '/prueba\.local/d' /etc/hosts
  fi
  return 0
}

nivel1_mision() {
cat <<'EOF'
# NIVEL 1 · Ficheros y carpetas

Trabaja SIEMPRE dentro de la carpeta de la prueba (~/prueba_nivel1). Al empezar tienes:
  datos/   pistas/   basura/
Cuando creas que has terminado, ejecuta `comprobar`. Puedes ejecutarlo tantas veces como quieras.

 1. Crea la estructura de carpetas  taller/documentos , taller/imagenes  y  taller/copias .
 2. Crea  taller/documentos/notas.txt  con exactamente dos líneas:
        Primera nota
        Segunda nota
    (sin abrir un editor: echo y redirecciones > y >>).
 3. Lee  pistas/secreto.txt . En su línea 7 hay una palabra clave.
    Escribe SOLO esa palabra en  taller/documentos/clave.txt .
 4. Copia  datos/informe.txt  a  taller/copias/  con el nombre  informe_copia.txt .
 5. Mueve TODAS las imágenes .jpg de  datos/  a  taller/imagenes/  (con un comodín).
    foto3.png se queda donde está.
 6. Guarda en  taller/listado.txt  el listado de  taller/imagenes  (la salida de ls).
 7. Con nano, edita  datos/config.ini  y cambia  modo=lento  por  modo=rapido .
 8. Elimina por completo la carpeta  basura/  y el fichero  datos/borrame.tmp .
 9. Añade al final de  /etc/hosts  la línea      127.0.0.1 prueba.local
    (es un fichero del sistema: necesitas sudo. Ojo: `sudo echo ... >> fichero` NO funciona;
    piensa quién hace la redirección. Pista: nano, o tee -a).

Puntuación: 100000 / (segundos + 5·comandos + 60). Menos tiempo y menos comandos = más puntos.
EOF
}

nivel1_comprobar() {
  local d="$1" palabra; palabra="$(cat "$d/.prueba/palabra")"
  paso "1. Carpetas taller/documentos, taller/imagenes y taller/copias" \
       bash -c "[ -d '$d/taller/documentos' ] && [ -d '$d/taller/imagenes' ] && [ -d '$d/taller/copias' ]"
  paso "2. notas.txt con 'Primera nota' y 'Segunda nota'" \
       contenido_es "$d/taller/documentos/notas.txt" $'Primera nota\nSegunda nota'
  paso "3. clave.txt contiene la palabra de la línea 7 de secreto.txt" \
       contenido_limpio_es "$d/taller/documentos/clave.txt" "$palabra"
  paso "4. informe_copia.txt es una copia exacta de datos/informe.txt" \
       bash -c "cmp -s '$d/datos/informe.txt' '$d/taller/copias/informe_copia.txt' && [ -f '$d/datos/informe.txt' ]"
  paso "5. foto1.jpg y foto2.jpg en taller/imagenes (y ya no en datos); foto3.png sigue en datos" \
       bash -c "[ -f '$d/taller/imagenes/foto1.jpg' ] && [ -f '$d/taller/imagenes/foto2.jpg' ] && [ ! -e '$d/datos/foto1.jpg' ] && [ ! -e '$d/datos/foto2.jpg' ] && [ -f '$d/datos/foto3.png' ] && [ ! -e '$d/taller/imagenes/foto3.png' ]"
  paso "6. taller/listado.txt contiene el listado de taller/imagenes" \
       bash -c "grep -q foto1.jpg '$d/taller/listado.txt' && grep -q foto2.jpg '$d/taller/listado.txt'"
  paso "7. config.ini tiene modo=rapido (editado con nano)" \
       bash -c "grep -qx 'modo=rapido' '$d/datos/config.ini' && ! grep -q 'modo=lento' '$d/datos/config.ini' && grep -qE '(^|[ |;&])nano( |$)' '$d/.prueba/historial'"
  paso "8. basura/ y datos/borrame.tmp eliminados" \
       bash -c "[ ! -e '$d/basura' ] && [ ! -e '$d/datos/borrame.tmp' ]"
  paso "9. /etc/hosts contiene '127.0.0.1 prueba.local'" \
       bash -c "grep -qE '^127\.0\.0\.1[[:space:]]+prueba\.local' /etc/hosts"
}
