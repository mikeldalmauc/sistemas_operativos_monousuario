# Ranking · servidor y web

```bash
docker compose up -d --build      # → http://<IP-del-profesor>:8080
docker compose logs -f api        # ver los envíos llegando
docker compose down               # los datos quedan en ./datos/resultados.json
```

- `api/`  servicio Node (sin dependencias) que recibe y sirve los resultados.
- `web/`  nginx con la web del ranking; hace de proxy de `/api/` hacia `api`.
- `datos/` volumen con `resultados.json`.

Configuración: `CLAVE` y `CLAVE_ADMIN` en `docker-compose.yml`. La `CLAVE` debe coincidir con la de
`../config.env` que usan los alumnos. Detalles en `../docs/notas-docente.md`.
