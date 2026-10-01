# Ranking · servidor y web

```bash
cp .env.ejemplo .env && nano .env  # claves (una sola vez; .env no se sube a git)
docker compose up -d --build      # → http://<IP-del-profesor>:8080
docker compose logs -f api        # ver los envíos llegando
docker compose down               # los datos quedan en ./datos/resultados.json
```

- `api/`  servicio Node (sin dependencias) que recibe y sirve los resultados.
- `web/`  nginx con la web del ranking; hace de proxy de `/api/` hacia `api`.
- `datos/` volumen con `resultados.json`.
- `admin.sh` administración desde el servidor (ver abajo).

Configuración: copia `.env.ejemplo` a `.env` y pon ahí `CLAVE` y `CLAVE_ADMIN` (el `.env` no se sube a git). La `CLAVE` debe coincidir con la de
`../config.env` que usan los alumnos. Detalles (solo profesor) en `../docs/notas-docente.md`, carpeta ignorada por git.

## Clave de nivel (ver comandos)

El ranking es público, pero `GET /api/resultados/ID` (los comandos de un envío) exige la cabecera
`X-Clave-Ver` con una clave válida **del mismo nivel**. El servidor genera una clave por envío
completado (`clave_ver`) y la devuelve al script del alumno, que la muestra y la guarda en
`~/…/claves.txt`. Con `X-Clave-Admin` se ve todo sin clave. Cualquier clave de un nivel abre
todos los envíos de ese nivel: la idea es "primero resuélvelo, luego mira cómo lo hicieron otros".
Un alumno puede pasar su clave a otro; eso no se puede impedir técnicamente, es cosa de clase.

## Borrar envíos

**No edites `datos/resultados.json` a mano**: el servidor lo tiene en memoria y lo sobrescribe con
el siguiente envío. Usa `admin.sh` en el servidor, desde esta carpeta (lee `CLAVE_ADMIN` de `.env`):

```bash
bash admin.sh listar              # todos los envíos, con su ID (o: listar 2 → solo nivel 2)
bash admin.sh borrar ID [ID…]     # uno o varios por ID
bash admin.sh borrar-alumno "Nombre Apellido"
bash admin.sh vaciar              # todo (pide confirmación); vaciar 1 → solo el nivel 1
```

Los cambios se ven en la web al instante (se refresca sola cada 30 s, o pulsa ⟳).
Si alguna vez tienes que tocar el JSON a mano: para el servidor antes (`docker compose stop api`),
edita, y arranca (`docker compose start api`). Si el JSON queda mal formado, el servidor se niega a
arrancar y lo dice en `docker compose logs api`, en vez de arrancar vacío.
