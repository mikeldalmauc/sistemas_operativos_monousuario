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
2. Instala la orden `prueba` (sin sudo) para poder lanzarla desde cualquier carpeta:
   ```bash
   bash instalar.sh
   ```
   y abre un terminal nuevo. (Si prefieres no instalar nada, `bash prueba.sh …` desde esta
   carpeta hace exactamente lo mismo.)
3. Comprueba `config.env`: `SERVIDOR_URL` debe ser la dirección que te dé el profesor.
4. La primera vez que inicies una prueba te pedirá tu nombre (queda en `config.local.env`).

## Cómo se juega

```bash
prueba iniciar 1      # prepara la carpeta ~/prueba_nivel1 y abre el terminal de la prueba
```

Se abre un terminal con el prompt `[prueba N1]`. Es tu bash de siempre, con cuatro órdenes extra:

| Orden | Qué hace |
|---|---|
| `mision` | Muestra el enunciado (también está en `MISION.md` dentro de la carpeta) |
| `comprobar` | Revisa paso a paso qué has hecho bien (✔) y qué no (✘). Al completar todo, guarda y envía tu marca |
| `reiniciar` | Borra tu trabajo, prepara la prueba de nuevo y pone el reloj a cero |
| `salir` | Sale del terminal de la prueba (el reloj **sigue corriendo**; vuelve con `prueba continuar 1`) |

El reloj empieza en el momento en que la prueba se prepara. **Lee bien el enunciado antes de
teclear**: cada comando cuenta.

Otras órdenes desde fuera:

```bash
prueba estado        # en qué punto está cada nivel
prueba mision 2      # leer el enunciado sin empezar
prueba reiniciar 2   # empezar de cero un nivel ya empezado
prueba borrar 2      # deshacer TODO lo del nivel (usuarios, servicios, ficheros…)
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

## Problemas frecuentes

- **`Permiso denegado` al guardar el nombre o los resultados**: has clonado el repositorio con
  `sudo` y la carpeta es de root. Arréglalo: `sudo chown -R $USER:$USER ~/sistemas_operativos_monousuario`
  (mientras tanto el script guarda tus cosas en `~/.prueba_comandos/`).
- **`El ranking no ha aceptado el envío`**: lee el motivo entre llaves. `nombre inválido` →
  revisa `config.local.env`; `clave incorrecta` → `CLAVE` de `config.env` no coincide con la del
  servidor; sin respuesta → el servidor no está encendido o `SERVIDOR_URL` está mal. Vuelve a
  ejecutar `comprobar` cuando esté arreglado: el intento no se pierde.
- **`prueba: orden no encontrada`** tras `bash instalar.sh`: abre un terminal nuevo (o `source ~/.bashrc`).
- **Nunca clones ni ejecutes la prueba con `sudo`**: `prueba …` siempre como tu usuario.
  El script pide sudo él solo cuando un paso lo necesita.

## Consejos

- Ten la **chuleta** del tema al lado (guías 04, 09 y 13).
- Los comodines (`*.jpg`), `mkdir -p` con llaves (`{a,b,c}`) y las tuberías ahorran comandos.
- `Tab` completa nombres y `↑` recupera comandos: no cuentan como comandos.
- `comprobar` te dice exactamente qué paso falla. Úsalo sin miedo: no cuenta como comando.
