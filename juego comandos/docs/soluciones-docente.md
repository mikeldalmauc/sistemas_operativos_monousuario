# La Mazmorra de los Comandos · notas del docente

**No repartir a los alumnos.** Aquí está la solución completa de los dos niveles, qué enseña
cada sala, los errores que el juego detecta a propósito, cómo evaluar y cómo ampliar.

## Índice

- [1. Qué enseña cada sala](#1-qué-enseña-cada-sala)
- [2. Solución del nivel 1](#2-solución-del-nivel-1)
- [3. Solución del nivel 2](#3-solución-del-nivel-2)
- [4. Errores que el juego detecta y explica](#4-errores-que-el-juego-detecta-y-explica)
- [5. Evaluación y entrega en Moodle](#5-evaluación-y-entrega-en-moodle)
- [6. En clase: cómo llevarlo](#6-en-clase-cómo-llevarlo)
- [7. Ampliar o modificar el juego](#7-ampliar-o-modificar-el-juego)

---

## 1. Qué enseña cada sala

### Nivel 1 · La Mazmorra de los Comandos Perdidos (CM3, CM4)

```
                  TORRE
                    │
ARCHIVO ─ BIBLIOTECA ─ GRAN SALA ─ CRIPTA ─ CÁMARA
   │                    │
ABISMO               ENTRADA
   │
GUARIDA
```

| Sala | Puzle | Comandos y conceptos | Hechizo (palabra) |
|---|---|---|---|
| Entrada | Tutorial: leer el pergamino y copiarlo a la mochila | `ls`, `cat`, `cp`, ruta absoluta con `~` | LUZ (LUMEN) |
| Gran Sala | Hub con cuatro puertas; inscripción sobre rutas | `pwd`, `cd`, `cd ..`, relativa vs absoluta, `mapa` | MAESTRO (todas) |
| Biblioteca | 24 libros y 3 runas; unir las runas en orden | comodines `runa_*`, `cat a b c`, redirección `>` | APERTURA (APERIRE) |
| Archivo | Parece vacío; tomo oculto de 300 líneas | `ls -a`, `wc -l`, `tail -n 1`, `head`, `less`, `echo >` | SILENCIO (SILENTIUM) |
| Abismo | Construir un puente con tres tablones | `mkdir`, `touch` con varios argumentos y rutas relativas | PUENTE (PONS) |
| Guarida | Nombre secreto en la línea 3 del diario | `head -n 3` | DORMIR (SOMNUS) |
| Cripta | Trampa: maldición en la mochila; escombros y telarañas | `rm`, `rmdir` (solo vacías), `rm -r`, `mv` frente a `cp` | PURIFICAR (PURGO) |
| Cámara | Pergamino borroso «IGN» que hay que renombrar y completar | `mv` para renombrar, `>>` frente a `>` | FUEGO (IGNIS) |
| Torre | Final | `cat *.txt > maestro.txt` (comodín + unión) | — |

Dependencias: cripta ← APERTURA (biblioteca); abismo ← SILENCIO (archivo); guarida ← PUENTE
**y** FUEGO (abismo + cámara: obliga a recorrer las dos ramas); torre ← MAESTRO (los siete).

### Nivel 2 · Las Catacumbas de los Permisos (CM6)

Lineal: vestíbulo → galería → escriba → números → bóveda → altar. Cada sala termina con
`chmod u+x ritual.sh && ./ritual.sh` (el ritual comprueba la sala y da un sello) y la puerta
siguiente está en `000`: el alumno la abre con `chmod 700 sala`.

| Sala | Situación | Enseña |
|---|---|---|
| Vestíbulo | `inscripcion.txt` en `----------`; `ritual.sh` sin x | leer `ls -l`, `chmod u+r`, `chmod u+x`, `./` y por qué |
| Galería | `espejo/` en `r--r--r--`: se lista pero no se entra | `x` en carpetas, `ls -ld` |
| Escriba | `archivo/` en `r-xr-xr-x`: no se puede crear ni borrar dentro | `w` en carpetas manda sobre borrar; `rm -f` |
| Números | Dejar `tesoro/` 750, `secreto.txt` 600, `publico.txt` 644 | octal exacto (fija, no añade) |
| Bóveda | `chmod o-r ofrenda_*.txt` y `chmod -R g+rX templo` | comodines + recursivo + `X` mayúscula |
| Altar | `guardian.sh` en `000`: leerlo antes de ejecutarlo | regla de oro: nunca ejecutar sin leer |

Queda fuera a propósito (necesita `sudo`): `chown`, `chgrp`, SUID/SGID/sticky, ACL. Es un
nivel 3 natural si algún día se quiere.

## 2. Solución del nivel 1

`herramientas/solucion_nivel1.sh` juega la partida entera (con `--rapido`, sin los errores a
propósito). Resumen humano:

```bash
mazmorra iniciar                      # nombre y apellido
cd ~/mazmorra/entrada
cp luz.txt ~/mazmorra/inventario/ ; lanzar luz
cd gran_sala
cd biblioteca
cat runa_*.txt > ~/mazmorra/inventario/apertura.txt ; lanzar apertura
cd archivo
ls -a ; tail -n 1 .tomo_infinito.txt
echo SILENTIUM > ~/mazmorra/inventario/silencio.txt ; lanzar silencio
cd abismo
mkdir puente ; touch puente/tablon_1.txt puente/tablon_2.txt puente/tablon_3.txt
echo PONS > ~/mazmorra/inventario/puente.txt ; lanzar puente     # guarida sigue helada
cd ~/mazmorra/entrada/gran_sala
lanzar apertura                                                  # abre la cripta
cd cripta                                                        # trampa: maldicion.txt
rm ~/mazmorra/inventario/maldicion.txt ; rmdir escombros ; rm -r telarañas
mv purificar.txt ~/mazmorra/inventario/ ; lanzar purificar
cd camara
mv borroso.txt ~/mazmorra/inventario/fuego.txt
echo IS >> ~/mazmorra/inventario/fuego.txt ; lanzar fuego
cd ~/mazmorra/entrada/gran_sala/biblioteca/archivo/abismo
lanzar fuego                                                     # derrite el hielo
cd guarida
head -n 3 diario.txt ; echo SOMNUS > ~/mazmorra/inventario/dormir.txt ; lanzar dormir
cd ~/mazmorra/inventario ; cat *.txt > maestro.txt
cd ~/mazmorra/entrada/gran_sala ; lanzar maestro
cd torre                                                         # victoria + certificado
```

## 3. Solución del nivel 2

`herramientas/solucion_nivel2.sh`. Resumen:

```bash
mazmorra iniciar --nivel 2
cd ~/catacumbas/vestibulo
chmod u+r inscripcion.txt ; cat inscripcion.txt
chmod u+x ritual.sh ; ./ritual.sh ; chmod 700 galeria ; cd galeria
chmod u+x espejo ; cat espejo/reflejo.txt
chmod u+x ritual.sh ; ./ritual.sh ; chmod 700 escriba ; cd escriba
chmod u+w archivo ; rm -f archivo/polvo.txt ; echo Nombre > archivo/firma.txt
chmod u+x ritual.sh ; ./ritual.sh ; chmod 700 numeros ; cd numeros
chmod 750 tesoro ; chmod 600 secreto.txt ; chmod 644 publico.txt
chmod u+x ritual.sh ; ./ritual.sh ; chmod 700 boveda ; cd boveda
chmod o-r ofrenda_*.txt ; chmod -R g+rX templo
chmod u+x ritual.sh ; ./ritual.sh ; chmod 700 altar ; cd altar
chmod u+r guardian.sh ; cat guardian.sh ; chmod u+x guardian.sh ; ./guardian.sh
```

## 4. Errores que el juego detecta y explica

Cada uno lleva un mensaje propio que explica el concepto en vez de un «incorrecto»:

| Lo que hace el alumno | Mensaje del juego |
|---|---|
| `lanzar luz` con el pergamino aún en el suelo | «está en el suelo de esta sala, no en la mochila: `cp luz.txt ~/mazmorra/inventario/`» |
| `cat runa_c.txt runa_b.txt runa_a.txt > apertura.txt` | «son las letras correctas pero en otro orden: en `cat a b c` el orden importa» |
| `echo IS > fuego.txt` (un solo `>`) | «solo pone IS: has borrado el principio; para añadir se usan dos `>>`» |
| Pergamino en blanco (`> fichero` sin echo) | «está EN BLANCO: `echo PALABRA > ...`» |
| Nombre parecido (`Luz.txt`, `luz.txt.txt`) | «tiene que llamarse exactamente luz.txt: `mv ...`» |
| `lanzar` con la maldición en la mochila | «la maldición te ahoga la voz: `rm ~/mazmorra/inventario/maldicion.txt`» |
| `cp purificar.txt` en vez de `mv` | condición «el pergamino ya no está en el suelo» sin cumplir |
| `lanzar lux` (hechizo inexistente) | «nunca has oído hablar... ¿querías decir luz?» |
| Ficheros nuevos que no estaban (p. ej. `mv luz.txt ~/mazmorra/inventari` mal escrito) | `mirar` avisa: «cosas que no estaban aquí al principio: inventari» |
| `bash ritual.sh` sin `+x` (nivel 2) | «no tiene permiso de EJECUCIÓN: `chmod u+x ritual.sh` y `./ritual.sh`» |
| `chmod 755 tesoro` cuando se pedía 750 | «tesoro tiene rwxr-xr-x = 755» (el octal exacto que ha puesto) |
| Ejecutar un ritual de otra sala | «ese ritual pertenece a otra sala» |

Y los errores **reales de Linux** que el alumno ve tal cual (el juego no los tapa):
`rmdir: Directory not empty`, `cd: Permission denied`, `cat: Permission denied`,
`bash: ./ritual.sh: Permission denied`, `rm: remove write-protected regular file?`.

## 5. Evaluación y entrega en Moodle

**Entregable**: el alumno sube `~/mazmorra/certificado_nivel1.txt` (y opcionalmente el del
nivel 2). El certificado lleva nombre, fecha, tiempo, pistas usadas y un código.

**Verificar el código**:

```bash
python3 herramientas/verificar_codigo.py certificado_nivel1.txt
python3 herramientas/verificar_codigo.py "Ane Ejemplo" 1 3 3B958843
```

El código es SHA-256 de `SECRETO|nivel|nombre|pistas` (8 caracteres). Si cambian el nombre
o el número de pistas en el fichero, no cuadra. `SECRETO` está en `mazmorra/motor.py`; si lo
cambias, cámbialo **antes** de repartir el zip (y el verificador lo lee del mismo sitio).

**Propuesta de calificación** (coherente con Apto / No apto del resto de temas):

| Criterio | Apto |
|---|---|
| Certificado del nivel 1 con código válido y nombre real | obligatorio |
| Pistas usadas | orientativo, no penaliza: ≤ 6 es normal; > 15 conviene revisar en clase |
| Nivel 2 | ampliación voluntaria; con código válido, anotar como mérito |

Si se quiere nota numérica: 5 por el certificado válido, +3 por un mini-manual en Markdown
(qué comando usó en cada sala y para qué sirve), +2 por el nivel 2.

**Las pistas**: la pista 3 de cada sala es la solución literal. Es deliberado: el objetivo es
que nadie se quede atascado más de unos minutos; un alumno que usa 27 pistas (todas) y termina
ha tecleado todos los comandos igualmente, y ese dato queda en el certificado.

**Anti-trampas**: mínimo, a propósito. Un alumno que descubra `chmod` en el nivel 1 y abra
una puerta sellada se encuentra con que la torre exige los ocho hechizos igual. El estado del
juego está en `~/mazmorra/.juego/estado.json` en texto plano: editarlo es posible; el código
del certificado se calcula al terminar a partir del nombre y las pistas, así que un estado
editado da un certificado «válido». No merece la pena blindarlo más: quien sepa hacer eso ya
sabe lo que el juego enseña.

## 6. En clase: cómo llevarlo

- **Sesión 1 (1 h)**: instalar (10 min), entrada + gran sala + biblioteca juntos en el
  proyector, resto individual. Al final de la sesión el `estado` de cada uno.
- **Sesión 2 (1-2 h)**: terminar el nivel 1. Los que acaban ayudan o empiezan el nivel 2.
- **Nivel 2**: cuando se haya explicado permisos (tema 09). Cabe en 1-2 h.
- El comando `estado` en cada puesto te dice en 5 segundos por dónde va cada alumno.
- Si un alumno rompe su sala: `mazmorra reiniciar sala`. Si rompe todo: `mazmorra reiniciar todo`
  (pierde el progreso, no el nombre).
- Si en la MV no se ve la descripción al entrar en una sala: no ha abierto un terminal nuevo
  tras instalar (`source ~/.bashrc` lo arregla en el acto).

Requisitos: Python 3 (viene en Mint), bash o zsh, un terminal con UTF-8 (el de Mint lo es).
Sin `sudo`, sin dependencias, sin red.

## 7. Ampliar o modificar el juego

Todo el contenido está en dos ficheros de datos: `mazmorra/mundo_nivel1.py` y
`mazmorra/mundo_nivel2.py`. El motor (`motor.py`) no sabe nada de la historia.

**Cambiar un texto o una pista**: edita la sala en el fichero del nivel. Nada más.

**Añadir una sala** (nivel 1): añade un diccionario a `SALAS` con:

```python
{
    "id": "pozo", "padre": "cripta", "carpeta": "pozo",
    "titulo": "El Pozo", "mapa": "POZO", "pos": (3, 2), "arte": "abismo",
    "descripcion": "...", "objetivo": "...",
    "ficheros": {"inscripcion.txt": "...", "eco.txt": "Palabra de poder: VOX\n"},
    "puertas": {},                       # o {"hija": ["hechizo"]}
    "hechizo": "eco", "palabra": "VOX",
    "condiciones": [ {"tipo": "existe", "ruta": "cubo", "dir": True, "texto": "..."} ],
    "pistas": ["...", "...", "..."],
    "exito": "...",
}
```

y en la sala padre añade la puerta: `"puertas": {..., "pozo": ["purificar"]}`. `pos` es la
casilla del mapa (columna, fila); padre e hijo tienen que ser casillas contiguas.

Tipos de condición: `existe` (con `dir`, `no_vacio`), `no_existe`, `cuenta` (`patron`,
`minimo`), `modo` (`igual`, `bits`, `sin_bits`; con `patron` o `recursivo` + `que`), `sello`,
`hechizo`. Las rutas son relativas a la sala; con `@` delante, relativas a la raíz
(`@inventario/x.txt`). Con `al_entrar` se programan trampas (acción `crear`).

**Arte**: `mazmorra/arte.py`. Cada dibujo es una lista de líneas de ≤ 60 columnas; la fuente
de bloques (`rotulo("TEXTO")`) sirve para rótulos nuevos.

**Probar**: `bash herramientas/solucion_nivel1.sh` juega la partida entera con un usuario
normal (no como root: root se salta los permisos y las puertas no se cierran).

**Repartir**: `bash herramientas/empaquetar.sh` → `dist/mazmorra-juego.zip` (solo el juego,
el instalador y la guía del alumno; sin soluciones ni verificador).
