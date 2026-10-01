#!/bin/bash
# Partida automática del NIVEL 2 (catacumbas) con los comandos de un alumno.
# Uso:  bash solucion_nivel2.sh [--rapido]
# ¡NO repartir a los alumnos!

export MAZMORRA_COLOR="${MAZMORRA_COLOR:-1}"
export PATH="$HOME/.mazmorra/bin:$PATH"
RAPIDO=0; [ "$1" = "--rapido" ] && RAPIDO=1

paso() {
    printf '\n\033[1;32malumno@mint-smr\033[0m:\033[1;34m%s\033[0m$ \033[1m%s\033[0m\n' \
        "$(pwd | sed "s|^$HOME|~|")" "$*"
    eval "$@"
}
cd() { builtin cd "$@" && mirar --auto; }
error_esperado() { [ $RAPIDO = 1 ] && return 1; return 0; }

mazmorra iniciar --nivel 2 --si --nombre "Ane Ejemplo" >/dev/null
echo "== Catacumbas creadas =="

# ---- Vestíbulo: ls -l, u+r, +x, ./ ---------------------------------------
paso cd ~/catacumbas/vestibulo
paso 'ls -l'
error_esperado && paso cat inscripcion.txt          # Permission denied
paso chmod u+r inscripcion.txt
paso cat inscripcion.txt
error_esperado && paso ./ritual.sh                  # Permission denied (sin x)
error_esperado && paso bash ritual.sh               # el ritual detecta que no tiene x
paso chmod u+x ritual.sh
paso ./ritual.sh
error_esperado && paso cd galeria                   # Permission denied
paso chmod u+rwx galeria
paso cd galeria

# ---- Galería: x en carpetas ------------------------------------------------
paso 'ls -ld espejo'
paso ls espejo
error_esperado && paso cat espejo/reflejo.txt       # Permission denied
paso chmod u+x espejo
paso cat espejo/reflejo.txt
paso chmod u+x ritual.sh
paso ./ritual.sh
paso chmod 700 escriba
paso cd escriba

# ---- Escriba: w en carpetas --------------------------------------------------
paso 'ls -l archivo'
error_esperado && paso 'echo Ane > archivo/firma.txt'   # Permission denied
paso chmod u+w archivo
paso 'rm -f archivo/polvo.txt'
paso 'echo Ane Ejemplo > archivo/firma.txt'
paso pista
paso chmod u+x ritual.sh
error_esperado && paso ./ritual.sh                  # ya ok en realidad; muestra sello
[ $RAPIDO = 1 ] && paso ./ritual.sh
paso chmod 700 numeros
paso cd numeros

# ---- Números: octal ------------------------------------------------------------
paso 'ls -l'
error_esperado && paso chmod 755 tesoro
error_esperado && paso chmod u+x ritual.sh
error_esperado && paso ./ritual.sh                  # falla: 755 no es 750
paso chmod 750 tesoro
paso chmod 600 secreto.txt
paso chmod 644 publico.txt
paso 'ls -l'
[ $RAPIDO = 1 ] && paso chmod u+x ritual.sh
paso ./ritual.sh
paso chmod 700 boveda
paso cd boveda

# ---- Bóveda: comodines y -R ------------------------------------------------------
paso 'chmod o-r ofrenda_*.txt'
paso 'ls -l ofrenda_*'
error_esperado && paso chmod u+x ritual.sh
error_esperado && paso ./ritual.sh                  # falta el templo
paso 'chmod -R g+rX templo'
paso 'ls -lR templo'
[ $RAPIDO = 1 ] && paso chmod u+x ritual.sh
paso ./ritual.sh
paso chmod 700 altar
paso cd altar

# ---- Altar: leer antes de ejecutar -------------------------------------------------
paso 'ls -l'
paso chmod u+r guardian.sh
paso cat guardian.sh
paso chmod u+x guardian.sh
paso ./guardian.sh
paso cat ~/catacumbas/certificado_nivel2.txt
paso mapa
paso estado
