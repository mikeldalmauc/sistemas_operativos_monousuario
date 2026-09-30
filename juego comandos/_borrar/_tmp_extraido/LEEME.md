# La Mazmorra de los Comandos

Juego de terminal para aprender Linux, para el módulo Sistemas Operativos Monopuesto (SMR 1.º).
El alumno recorre una mazmorra que **es un árbol de carpetas real** en su `~`, usando su
terminal de verdad: `cd`, `ls`, `cat`, `cp`, `mv`, `rm`, `mkdir`, `touch`, `echo`, `>`, `>>`,
`head`, `tail`, `wc`, comodines y `ls -a`. El juego solo añade seis comandos de «grimorio»
(`mirar`, `mapa`, `inventario`, `lanzar`, `pista`, `estado`) que leen el estado real del disco
y guían con una checklist y pistas progresivas.

- **Nivel 1 · La Mazmorra de los Comandos Perdidos**: 9 salas, 8 hechizos (crear, leer,
  copiar, mover, borrar, unir ficheros). CM3, CM4.
- **Nivel 2 · Las Catacumbas de los Permisos** (dificultad extra): 6 salas sobre `ls -l`,
  `chmod` simbólico y octal, permisos en carpetas, `chmod -R`, ejecutar scripts. CM6.

Al terminar cada nivel genera un certificado con un código verificable (entregable de Moodle).

## Carpetas

```text
juego comandos/
├── LEEME.md                    ← este fichero
├── instalar.sh                 ← el alumno lo ejecuta una vez (sin sudo)
├── desinstalar.sh
├── mazmorra/                   ← el juego (Python 3, sin dependencias)
│   ├── motor.py                ← motor: estado, comprobaciones, mapa, mensajes
│   ├── mundo_nivel1.py         ← TODO el contenido del nivel 1 (salas, textos, pistas)
│   ├── mundo_nivel2.py         ← TODO el contenido del nivel 2
│   ├── arte.py                 ← ASCII art y fuente de rótulos
│   ├── colores.py              ← colores ANSI
│   ├── mazmorra.sh             ← enganche al terminal (PATH, mirar automático al cd, Tab)
│   └── __main__.py             ← python3 -m mazmorra ORDEN
├── docs/
│   ├── guia-alumno.md          ← instrucciones para el alumno (va dentro del zip)
│   └── soluciones-docente.md   ← soluciones, errores detectados, evaluación, cómo ampliar
├── herramientas/
│   ├── empaquetar.sh           ← crea dist/mazmorra-juego.zip para Moodle
│   ├── verificar_codigo.py     ← comprueba el código de un certificado
│   ├── solucion_nivel1.sh      ← partida automática completa (prueba + solución)
│   └── solucion_nivel2.sh
└── dist/
    └── mazmorra-juego.zip      ← lo que se sube a Moodle
```

## Flujo del profesor

1. (Opcional) Cambia `SECRETO` en `mazmorra/motor.py` para que los códigos de tu grupo sean
   únicos.
2. `bash herramientas/empaquetar.sh` → sube `dist/mazmorra-juego.zip` a Moodle junto con
   `docs/guia-alumno.md` (o su HTML).
3. Los alumnos: descomprimir → `bash instalar.sh` → terminal nuevo → `mazmorra iniciar`.
4. Entregan `~/mazmorra/certificado_nivel1.txt`; tú lo compruebas con
   `python3 herramientas/verificar_codigo.py certificado.txt`.

## Probarlo tú

En cualquier Linux con Python 3, **como usuario normal** (root se salta los permisos y las
puertas no se cierran):

```bash
bash instalar.sh
source ~/.bashrc
bash herramientas/solucion_nivel1.sh        # partida completa, con errores a propósito
bash herramientas/solucion_nivel2.sh --rapido
```

O jugar a mano: `mazmorra iniciar` y `cd ~/mazmorra/entrada`.

Detalles de diseño, soluciones y cómo añadir salas: `docs/soluciones-docente.md`.
