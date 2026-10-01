# Notas para el docente · Pruebas de comandos

> No se publica a los alumnos (aunque esté en el repo, no enlazarlo desde Moodle).

## Qué hay

```text
prueba_comandos/
├── prueba.sh            ← punto de entrada (iniciar / continuar / reiniciar / borrar / estado / mision)
├── config.env           ← URL del servidor, clave, ENVIAR=si|no (se sube a git)
├── config.local.env     ← nombre del alumno (lo crea prueba.sh; ignorado por git)
├── lib/
│   ├── comun.sh         ← cronómetro, recuento de comandos, puntuación, envío, predicados de comprobación
│   ├── rc.sh            ← el "terminal de la prueba": registra cada comando en .prueba/historial
│   ├── nivel1.sh        ← cada nivel: preparar · misión · comprobar · limpiar
│   ├── nivel2.sh
│   └── nivel3.sh
├── resultados/          ← JSON de cada intento completado (ignorado por git)
├── docs/notas-docente.md
└── ranking/             ← servidor Node + web + docker compose (ver más abajo)
```

Cada prueba vive en `~/prueba_nivelN/` del alumno. Dentro, `.prueba/` guarda el instante de
inicio, el historial de comandos y los datos aleatorios de la partida (palabra clave, código
del tesoro…). `MISION.md` es el enunciado.

## Cómo funciona el registro de comandos

`prueba.sh iniciar` lanza `bash --rcfile lib/rc.sh -i`: un bash normal cuyo `HISTFILE` apunta
a `.prueba/historial` y con `PROMPT_COMMAND='history -a'`, de modo que cada línea que el
alumno ejecuta se escribe al instante. Al contar se descartan las líneas vacías y las órdenes
propias (`mision`, `comprobar`, `reiniciar`, `salir`, `clear`, `history`).

Limitaciones honestas:
- Lo que se teclea **dentro de `su ana`** o de un `sudo -i` no queda registrado (es otro
  shell). La comprobación se basa siempre en el **estado real del sistema**, no en el historial,
  así que el resultado es fiable aunque el recuento de comandos sea algo menor.
- Un alumno con ganas puede editar `.prueba/historial` o `.prueba/inicio`. La prueba es una
  herramienta de práctica y el ranking un aliciente, no una nota; si quieres usarla como nota,
  hazla presencial y mira el JSON (`usuario`, `equipo`, comandos) en el modal de la web: un
  historial de 3 comandos para el nivel 3 canta.
- La comprobación del paso "con nano" (nivel 1) solo mira que `nano` aparezca en el historial.

## Puntuación

`puntos = 100000 / (segundos + 5·comandos + 60)`, entera. Implementada dos veces con la misma
fórmula: `lib/comun.sh` (`calcular_puntos`) y `ranking/api/server.js` (`puntos`). El servidor
**recalcula** los puntos, no se fía del cliente. Si la cambias, cámbiala en los dos sitios.

Referencia de tiempos razonables tras un par de repeticiones:

| Nivel | Comandos mínimos aprox. | Tiempo con soltura | Puntos |
|---|---|---|---|
| 1 | 11–14 | 2–3 min | 350–450 |
| 2 | 14–18 | 4–6 min | 200–280 |
| 3 | 12–16 | 6–10 min | 130–200 |

## Soluciones de referencia

### Nivel 1
```bash
mkdir -p taller/{documentos,imagenes,copias}
echo "Primera nota" > taller/documentos/notas.txt
echo "Segunda nota" >> taller/documentos/notas.txt
sed -n 7p pistas/secreto.txt                 # o head -n 7 | tail -n 1
echo cometa > taller/documentos/clave.txt    # la palabra cambia en cada partida
cp datos/informe.txt taller/copias/informe_copia.txt
mv datos/*.jpg taller/imagenes/
ls taller/imagenes > taller/listado.txt
nano datos/config.ini                        # modo=lento → modo=rapido
rm -r basura datos/borrame.tmp
echo "127.0.0.1 prueba.local" | sudo tee -a /etc/hosts    # o sudo nano /etc/hosts
```

### Nivel 2
```bash
sudo groupadd taller
sudo useradd -m -G taller ana
sudo useradd -m ben
sudo mkdir /srv/taller && sudo chown root:taller /srv/taller && sudo chmod 770 /srv/taller
sudo -u ana touch /srv/taller/ana.txt        # o: su ana → touch /srv/taller/ana.txt → exit
chmod 600 privado.txt
sudo chgrp taller compartido.txt && chmod 640 compartido.txt
chmod +x scripts/saludo.sh && ./scripts/saludo.sh
sudo systemctl enable --now prueba-servicio
sudo systemctl disable --now prueba-ruido
sudo nano /etc/prueba/prueba.conf            # nivel=bajo → nivel=alto  (o sudo sed -i)
```
Los servicios `prueba-servicio` y `prueba-ruido` son `sleep infinity`; se crean en la
preparación y se borran con `borrar 2`. `chgrp` a un grupo al que el alumno no pertenece
requiere sudo: es intencionado (paso 4).

### Nivel 3
```bash
mkdir logs && find bosque -name '*.log' -exec mv {} logs/ \;
grep -rhoE 'TESORO-[0-9]{4}' bosque > respuestas/tesoro.txt
find bosque -type f -perm /111 -exec chmod -x {} \;
find bosque -type f -printf '%s %f\n' | sort -n | tail -1 | cut -d' ' -f2 > respuestas/grande.txt
printf '#!/bin/bash\nfind "$1" -type f | wc -l\n' > scripts/contar.sh
printf '#!/bin/bash\nmkdir -p copia_seguridad\nfind bosque -name "*.txt" -exec cp {} copia_seguridad/ \\;\n' > scripts/copia.sh
chmod +x scripts/*.sh && ./scripts/copia.sh
sudo chattr +i respuestas/tesoro.txt && sudo chattr +a registro.log
sudo useradd -m ana
echo 'ana ALL=(ALL) NOPASSWD: /usr/bin/systemctl' | sudo tee /etc/sudoers.d/ana   # o sudo visudo -f /etc/sudoers.d/ana
```
Los scripts los escribirán normalmente con `nano`; lo que se comprueba es que funcionen
(`contar.sh` se ejecuta sobre un árbol temporal con 5 ficheros; `copia.sh` se ejecuta y se
compara con los `.txt` reales). `chattr` exige ext4 (el `/home` de Mint y Arch lo es).

## Reinicio y limpieza

- `reiniciar N` = `limpiar` + `preparar`: deshace **también** los cambios en el sistema
  (línea de /etc/hosts, usuarios, grupo, /srv/taller, /etc/prueba, servicios, sudoers,
  atributos inmutables).
- `borrar N` hace solo la limpieza. Recomienda a los alumnos ejecutarlo al acabar el curso.
- Nivel 3 borra el usuario `ana`: si un alumno tiene los niveles 2 y 3 a medias a la vez,
  se pisarán. Están pensados para hacerse por separado.

## Servidor de ranking

```bash
cd ranking
docker compose up -d --build     # web + API en http://<tu-IP>:8080
```

- `ranking/api`: Node 20 sin dependencias, guarda todo en `ranking/datos/resultados.json`
  (volumen; sobrevive a reinicios de los contenedores). Rutas:
  `POST /api/resultados` (cabecera `X-Clave`), `GET /api/ranking/{1,2,3}`,
  `GET /api/resultados/ID` (con comandos), `DELETE /api/resultados/ID` (cabecera
  `X-Clave-Admin`), `GET /api/salud`.
- `ranking/web`: nginx sirve la web y hace de proxy de `/api/` hacia el contenedor `api`.
  Así los alumnos solo necesitan una URL (`http://IP:8080`) y no hay problemas de CORS.
- La web: tres pestañas (una por nivel), todos los envíos ordenados por puntos, filtro por
  nombre, "solo el mejor intento de cada alumno", y al pinchar un envío, modal con el
  histórico de comandos (los `sudo` en rojo). Se refresca sola cada 30 s: sirve para
  proyectarla.

Antes de la clase:
1. En el servidor, copia `ranking/.env.ejemplo` a `ranking/.env` y pon ahí `CLAVE` y `CLAVE_ADMIN`
   (el `.env` está en `.gitignore`: la clave de admin nunca viaja en el repo). Pon la misma `CLAVE` en
   `config.env` y haz commit.
2. Pon en `config.env` la IP del equipo del profesor en la red del aula (`SERVIDOR_URL`).
   Las VMs deben poder llegar a ella (NAT de VirtualBox llega a la red del host sin tocar nada;
   si el equipo del profe tiene cortafuegos, abrir el 8080).
3. `curl http://IP:8080/api/salud` desde una VM para comprobarlo.

Borrar un envío trucado:
```bash
curl -X DELETE -H "X-Clave-Admin: cambia-esto" http://localhost:8080/api/resultados/ID
```
(el ID se ve en la URL de la petición del modal o en `datos/resultados.json`).

## Ampliar

Un nivel nuevo = un `lib/nivelN.sh` con cuatro funciones (`nivelN_preparar`, `nivelN_mision`,
`nivelN_comprobar`, `nivelN_limpiar`) y añadir el número a `requiere_nivel` en `comun.sh`, a
la expresión `[123]` de `server.js` y una pestaña en `index.html`. Los pasos se declaran con
`paso "descripción" comando…`: el paso está hecho si el comando devuelve 0.
