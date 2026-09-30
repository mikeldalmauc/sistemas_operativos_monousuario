---
modulo: Sistemas Operativos Monopuesto (SMR 1.º)
nivel: 1 · Básico (nivel 2 del juego: intermedio)
tipo: Práctica · juego de terminal
competencias: CM3, CM4 (nivel 1) · CM6 (nivel 2)
herramientas: H4 (terminal Linux y Bash)
duracion: 2-3 h (nivel 1) + 2 h (nivel 2)
---

# La Mazmorra de los Comandos · guía del alumno

> **Situación.** Te despiertas en la entrada de una mazmorra. No recuerdas cómo has llegado.
> Solo tienes una cosa: tu *grimorio*, que es el terminal de Linux. La única forma de salir es
> llegar a la torre. Por el camino aprenderás a moverte por las carpetas, leer, crear, copiar,
> mover y borrar ficheros. Es decir, lo que hace un técnico de sistemas cien veces al día.

## Índice

- [La Mazmorra de los Comandos · guía del alumno](#la-mazmorra-de-los-comandos--guía-del-alumno)
  - [Índice](#índice)
  - [1. Cómo funciona (léelo, es corto)](#1-cómo-funciona-léelo-es-corto)
  - [2. Instalar el juego](#2-instalar-el-juego)
  - [3. Los comandos del grimorio](#3-los-comandos-del-grimorio)
  - [4. Reglas del juego](#4-reglas-del-juego)
  - [5. Si algo se rompe](#5-si-algo-se-rompe)
  - [6. Nivel 2: las catacumbas de los permisos](#6-nivel-2-las-catacumbas-de-los-permisos)
  - [7. Entrega](#7-entrega)
  - [8. Chuleta](#8-chuleta)

---

## 1. Cómo funciona (léelo, es corto)

La mazmorra **es una carpeta de verdad** en tu carpeta personal: `~/mazmorra`. Cada sala es
una carpeta, cada objeto es un fichero, y tu mochila es la carpeta `~/mazmorra/inventario`.

> **Analogía.** Una ruta es como una dirección postal: `~/mazmorra/entrada/gran_sala`.
> `~` es tu casa; cada `/` es una puerta que atraviesas. Moverte por la mazmorra es moverte por
> las carpetas con `cd`; mirar el suelo es `ls`; leer un pergamino es `cat`.

No hay ninguna consola inventada: **juegas con tu terminal real**. Todo lo que aprendas aquí te
sirve tal cual fuera del juego.

## 2. Instalar el juego

Se juega en tu máquina virtual **Mint-SMR** (o en cualquier Linux).

1. Descarga `mazmorra-juego.zip` de Moodle y descomprímelo (clic derecho → *Extraer aquí*).
2. Abre un terminal **dentro de la carpeta descomprimida** (clic derecho → *Abrir terminal aquí*)
   y ejecuta:

   ```bash
   bash instalar.sh
   ```

3. **Cierra el terminal y abre uno nuevo** (el juego se engancha al terminal al arrancar).
4. Crea tu mazmorra:

   ```bash
   mazmorra iniciar
   ```

   Te preguntará tu nombre: **pon tu nombre y apellido**, que irá en el certificado.

5. Entra:

   ```bash
   cd ~/mazmorra/entrada
   ```

> **Consejo.** No hace falta `sudo` para nada. El juego se instala en `~/.mazmorra` y no toca
> nada fuera de tu carpeta personal.

## 3. Los comandos del grimorio

Son seis comandos nuevos que añade el juego. Funcionan desde cualquier sala.

| Comando | Qué hace |
|---|---|
| `mirar` | Describe la sala: objetivo, lista de cosas por hacer (✓/✗) y qué hay en el suelo. Se ejecuta solo al entrar en una sala. |
| `mapa` | Mapa de la mazmorra y el árbol de carpetas para llegar a cada sala. |
| `inventario` | Qué llevas en la mochila y qué hechizos tienes listos. |
| `lanzar HECHIZO` | Lanza un hechizo. Necesitas su pergamino en la mochila. |
| `pista` | Una ayuda. Cada vez que la pidas será más concreta (3 niveles; la tercera es la solución). |
| `estado` | Tu progreso: salas, hechizos, pistas usadas, tiempo. |

Y los comandos de Linux de siempre: `ls`, `cd`, `cat`, `cp`, `mv`, `rm`, `mkdir`, `touch`...
La chuleta está al final y también en `mazmorra chuleta`.

## 4. Reglas del juego

- **Un hechizo es un fichero** `nombre.txt` en tu mochila (`~/mazmorra/inventario`) que tiene
  dentro su *palabra de poder*. Ejemplo: `luz.txt` con la palabra `LUMEN` → `lanzar luz`.
- Las **puertas selladas** son carpetas en las que no puedes entrar hasta que lances el hechizo
  que piden. `mirar` te dice cuál.
- Los pergaminos se consiguen de muchas formas: copiándolos del suelo, uniendo trozos,
  leyendo tomos, escribiéndolos tú... Cada sala explica la suya en `inscripcion.txt`.
- Un hechizo aprendido **se puede lanzar todas las veces que quieras**.
- Las **pistas se cuentan** y salen en tu certificado. No pasa nada por usarlas, pero intenta
  primero leer la inscripción de la sala con `cat inscripcion.txt`.
- El juego **no te va a borrar nada** fuera de `~/mazmorra`. Pero `rm` sí borra de verdad y no
  pregunta: lee bien lo que escribes.

## 5. Si algo se rompe

| Problema | Solución |
|---|---|
| He borrado o cambiado algo de una sala y no sé volver atrás | Dentro de la sala: `mazmorra reiniciar sala`. La sala vuelve a estar como al principio; tus hechizos se conservan. |
| Quiero empezar de cero | `mazmorra reiniciar todo` |
| `mirar: command not found` | No has abierto un terminal nuevo tras instalar. Ciérralo y abre otro (o ejecuta `source ~/.bashrc`). |
| `Permission denied` al hacer `cd` a una sala | Está sellada: te falta un hechizo. `mirar` te dice cuál. (En el nivel 2 es distinto: ahí las puertas las abres tú con `chmod`.) |
| No sé dónde estoy | `pwd`. Y `mapa` te enseña el árbol entero. |
| Me he perdido del todo | `cd ~/mazmorra/entrada/gran_sala` te lleva al centro de la mazmorra desde donde sea. |

## 6. Nivel 2: las catacumbas de los permisos

Cuando termines el nivel 1, bajo la mazmorra hay unas catacumbas donde los pergaminos no
sirven: allí la magia son los **permisos** (`ls -l`, `chmod`) y los **rituales** (programas que
hay que hacer ejecutables y lanzar con `./ritual.sh`).

```bash
mazmorra iniciar --nivel 2
cd ~/catacumbas/vestibulo
```

Las puertas están cerradas con permisos `000` y **las abres tú** con `chmod`. Es dificultad
extra: hazlo cuando hayamos visto los permisos en clase (o antes, si te atreves; el juego lo
explica todo).

## 7. Entrega

Al llegar a la torre (nivel 1) o romper el último sello (nivel 2) el juego crea un
certificado con un **código de verificación**:

- `~/mazmorra/certificado_nivel1.txt`
- `~/catacumbas/certificado_nivel2.txt`

Súbelos a la tarea de Moodle. El profesor comprueba el código: si cambias el nombre, el nivel o
las pistas del fichero, el código deja de ser válido.

> **Aviso.** El nombre del certificado es el que diste en `mazmorra iniciar`. Si pusiste
> `alumno` o cualquier otra cosa, vuelve a crear la mazmorra con `mazmorra iniciar` (te
> preguntará si quieres empezar de cero) y pon tu nombre real.

## 8. Chuleta

```text
NAVEGAR                             VER
  pwd           dónde estoy           cat f         todo de golpe
  cd ruta       ir                    less f        página a página (q sale)
  cd ..         subir una sala        head -n 5 f   primeras líneas
  cd ~/mazmorra/entrada  ruta absoluta   tail -n 5 f   últimas líneas
  ls            listar                wc -l f       contar líneas
  ls -a         listar también ocultos
  ls -l         listar con permisos

CREAR                               COPIAR / MOVER / BORRAR
  touch f       fichero vacío         cp o d        copiar
  mkdir c       carpeta               mv o d        mover o renombrar
  echo x > f    escribir (borra)      rm f          borrar fichero
  echo x >> f   añadir al final       rmdir c       borrar carpeta vacía
  cat a b > f   unir en f             rm -r c       borrar carpeta y contenido

COMODINES                           PERMISOS (nivel 2)
  *             lo que sea            ls -l         ver permisos
  ?             un carácter           chmod u+x f   dar x al dueño
  runa_*.txt    empieza por runa_     chmod o-r f   quitar r a otros
                                      chmod 750 c   octal: rwx r-x ---
AYUDA                                 chmod -R g+rX c   recursivo
  Tab           completa nombres      ./programa    ejecutar (necesita x)
  ↑             comando anterior
  cmd --help    ayuda rápida
```
