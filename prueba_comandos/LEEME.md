# Pruebas de comandos · speedrun del terminal

Tres pruebas de dificultad creciente para **interiorizar los comandos a base de repetirlas**.
Cada prueba es una lista de pasos que haces en tu terminal de verdad. Un script comprueba si lo
has hecho bien, mide el **tiempo** y cuenta los **comandos** que has usado, y si la completas
envía tu marca al ranking de la clase. Puedes repetirla tantas veces como quieras: el objetivo
es que cada vez tardes menos y uses menos comandos.

| Nivel | Qué tienes que saber | Necesita |
|---|---|---|
| 1 · Ficheros y carpetas | navegar, crear, leer, escribir, copiar, mover, borrar, nano, un cambio en /etc | Linux con sudo |
| 2 · Usuarios y servicios | usuarios y grupos, chmod/chown, su/sudo, ejecutar scripts, systemctl, editar configuración de root | Linux con sudo y systemd |
| 3 · Buscar y scripts | find, grep, scripts bash básicos, chattr, sudoers | Linux con sudo, systemd y ext4 |

Cada nivel da por sabido todo lo de los anteriores.

## Antes de empezar (una vez)

1. Descarga el repositorio en tu máquina virtual (Linux Mint o Arch):
   ```bash
   git clone <URL-del-repositorio>
   cd sistemas_operativos_monousuario/prueba_comandos
   ```
2. Comprueba `config.env`: `SERVIDOR_URL` debe ser la dirección que te dé el profesor.
3. La primera vez que inicies una prueba te pedirá tu nombre (queda en `config.local.env`).

## Cómo se juega

```bash
bash prueba.sh iniciar 1      # prepara la carpeta ~/prueba_nivel1 y abre el terminal de la prueba
```

Se abre un terminal con el prompt `[prueba N1]`. Es tu bash de siempre, con cuatro órdenes extra:

| Orden | Qué hace |
|---|---|
| `mision` | Muestra el enunciado (también está en `MISION.md` dentro de la carpeta) |
| `comprobar` | Revisa paso a paso qué has hecho bien (✔) y qué no (✘). Al completar todo, guarda y envía tu marca |
| `reiniciar` | Borra tu trabajo, prepara la prueba de nuevo y pone el reloj a cero |
| `salir` | Sale del terminal de la prueba (el reloj **sigue corriendo**; vuelve con `bash prueba.sh continuar 1`) |

El reloj empieza en el momento en que la prueba se prepara. **Lee bien el enunciado antes de
teclear**: cada comando cuenta.

Otras órdenes desde fuera:

```bash
bash prueba.sh estado        # en qué punto está cada nivel
bash prueba.sh mision 2      # leer el enunciado sin empezar
bash prueba.sh reiniciar 2   # empezar de cero un nivel ya empezado
bash prueba.sh borrar 2      # deshacer TODO lo del nivel (usuarios, servicios, ficheros…)
```

## Puntuación

```
puntos = 100000 / (segundos + 5 × comandos + 60)
```

Ejemplos: 2 min y 15 comandos → 392 puntos · 5 min y 30 comandos → 196 puntos.
Un comando con tuberías (`|`) o encadenado con `&&` cuenta como **uno**: aprender a
combinar comandos se premia.

Los resultados se guardan también en `resultados/nivelN_fecha.json`. Si el servidor no está
disponible, entrega ese fichero en Moodle.

## Consejos

- Ten la **chuleta** del tema al lado (guías 04, 09 y 13).
- Los comodines (`*.jpg`), `mkdir -p` con llaves (`{a,b,c}`) y las tuberías ahorran comandos.
- `Tab` completa nombres y `↑` recupera comandos: no cuentan como comandos.
- `comprobar` te dice exactamente qué paso falla. Úsalo sin miedo: no cuenta como comando.
