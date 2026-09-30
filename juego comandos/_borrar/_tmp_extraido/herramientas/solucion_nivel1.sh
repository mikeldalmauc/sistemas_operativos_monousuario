#!/bin/bash
# Partida automática del NIVEL 1 con los comandos que escribiría un alumno.
#
# Sirve para dos cosas:
#   - comprobar que el juego funciona de principio a fin (lo usa el profesor),
#   - ver la solución completa paso a paso.
#
# Uso:  bash solucion_nivel1.sh          (juega y muestra todo)
#       bash solucion_nivel1.sh --rapido (solo la solución, sin errores a propósito)
#
# ¡NO repartir a los alumnos!

export MAZMORRA_COLOR="${MAZMORRA_COLOR:-1}"
export PATH="$HOME/.mazmorra/bin:$PATH"
RAPIDO=0; [ "$1" = "--rapido" ] && RAPIDO=1

paso() {                     # muestra el comando como en un terminal y lo ejecuta
    printf '\n\033[1;32malumno@mint-smr\033[0m:\033[1;34m%s\033[0m$ \033[1m%s\033[0m\n' \
        "$(pwd | sed "s|^$HOME|~|")" "$*"
    eval "$@"
}
cd() {                       # el hook de bash describe la sala al entrar; aquí lo imitamos
    builtin cd "$@" && mirar --auto
}
error_esperado() { [ $RAPIDO = 1 ] && return 1; return 0; }

mazmorra iniciar --si --nombre "Ane Ejemplo" >/dev/null
echo "== Mazmorra creada =="

paso cd ~/mazmorra/entrada
paso ls
paso cat inscripcion.txt
paso cat luz.txt
error_esperado && paso lanzar luz                 # error: está en el suelo
paso cp luz.txt ~/mazmorra/inventario/
paso inventario
paso lanzar luz

paso cd gran_sala
paso pwd
paso mapa

# ---- Biblioteca: comodines + cat + > -------------------------------------
paso cd biblioteca
paso ls
paso ls runa_*
paso cat runa_a.txt runa_b.txt runa_c.txt
error_esperado && paso 'cat runa_c.txt runa_b.txt runa_a.txt > ~/mazmorra/inventario/apertura.txt'
error_esperado && paso lanzar apertura            # error: letras en otro orden
paso 'cat runa_*.txt > ~/mazmorra/inventario/apertura.txt'
paso lanzar apertura

# ---- Archivo: ls -a, tail, echo > ------------------------------------------
paso cd archivo
paso ls
paso ls -a
paso wc -l .tomo_infinito.txt
paso tail -n 1 .tomo_infinito.txt
paso pista
paso 'echo SILENTIUM > ~/mazmorra/inventario/silencio.txt'
paso lanzar silencio

# ---- Abismo: mkdir, touch --------------------------------------------------
paso cd abismo
error_esperado && paso 'echo PONS > ~/mazmorra/inventario/puente.txt'
error_esperado && paso lanzar puente              # error: falta el puente
paso mkdir puente
paso touch puente/tablon_1.txt puente/tablon_2.txt puente/tablon_3.txt
paso ls puente
paso 'echo PONS > ~/mazmorra/inventario/puente.txt'
paso lanzar puente                                # puente sí, guarida sigue helada
paso 'ls -l'

# ---- Vuelta a la Gran Sala y a la cripta -----------------------------------
paso cd ~/mazmorra/entrada/gran_sala
paso lanzar apertura                              # abre la cripta
paso cd cripta                                    # ¡trampa!
paso inventario
error_esperado && paso lanzar purificar           # error: maldición
paso rm ~/mazmorra/inventario/maldicion.txt
error_esperado && paso rmdir telarañas            # error real de Linux: no está vacía
paso rmdir escombros
paso 'rm -r telarañas'
error_esperado && paso cp purificar.txt ~/mazmorra/inventario/
error_esperado && paso lanzar purificar           # error: había que moverlo
error_esperado && paso rm purificar.txt
[ $RAPIDO = 1 ] && paso mv purificar.txt ~/mazmorra/inventario/
paso lanzar purificar

# ---- Cámara: mv renombrar, >> ----------------------------------------------
paso cd camara
paso cat borroso.txt
paso mv borroso.txt ~/mazmorra/inventario/fuego.txt
error_esperado && paso 'echo IS > ~/mazmorra/inventario/fuego.txt'
error_esperado && paso lanzar fuego               # error: has borrado el principio
error_esperado && paso 'echo IGN > ~/mazmorra/inventario/fuego.txt'
paso 'echo IS >> ~/mazmorra/inventario/fuego.txt'
paso cat ~/mazmorra/inventario/fuego.txt
paso lanzar fuego

# ---- Guarida: head -----------------------------------------------------------
paso cd ~/mazmorra/entrada/gran_sala/biblioteca/archivo/abismo
paso lanzar fuego                                 # derrite el hielo
paso cd guarida
paso head -n 3 diario.txt
paso 'echo SOMNUS > ~/mazmorra/inventario/dormir.txt'
paso lanzar dormir
paso estado

# ---- Hechizo maestro y torre -------------------------------------------------
paso cd ~/mazmorra/inventario
paso ls
paso 'cat *.txt > maestro.txt'
paso cd ~/mazmorra/entrada/gran_sala
paso lanzar maestro
paso cd torre
paso cat corona.txt
paso cat ~/mazmorra/certificado_nivel1.txt
paso mapa
