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

Configuración: copia `.env.ejemplo` a `.env` y pon ahí `CLAVE` y `CLAVE_ADMIN` (el `.env` no se sube a git). La `CLAVE` debe coincidir con la de
`../config.env` que usan los alumnos. Detalles en `../docs/notas-docente.md`.
