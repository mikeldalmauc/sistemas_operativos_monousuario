#!/usr/bin/env bash
# Despliegue del ranking en el servidor: trae el repo, reconstruye lo que haya cambiado y comprueba.
# Se ejecuta EN EL SERVIDOR (a mano, por SSH desde desplegar.ps1, o desde GitHub Actions):
#     bash ~/sistemas_operativos_monousuario/prueba_comandos/ranking/servidor/desplegar.sh
set -u
REPO_DIR="${REPO_DIR:-$HOME/sistemas_operativos_monousuario}"
R="$REPO_DIR/prueba_comandos/ranking"
C_V=$'\e[1;32m'; C_R=$'\e[1;31m'; C_M=$'\e[1;35m'; C_F=$'\e[0m'
ok(){ echo "${C_V}✔${C_F} $*"; }; fallo(){ echo "${C_R}✘ $*${C_F}"; }

echo "${C_M}══ Despliegue $(date '+%Y-%m-%d %H:%M') ══${C_F}"
cd "$REPO_DIR" || { fallo "No existe $REPO_DIR"; exit 1; }
antes="$(git rev-parse --short HEAD)"
git pull -q --ff-only || { fallo "git pull ha fallado (¿cambios locales en el servidor?). Mira: git status"; exit 1; }
ahora="$(git rev-parse --short HEAD)"
[ "$antes" = "$ahora" ] && ok "Repo ya al día ($ahora)" || ok "Repo actualizado: $antes → $ahora"
git log --oneline "$antes..$ahora" 2>/dev/null | sed 's/^/    /'

[ -f "$R/.env" ] || { fallo "Falta $R/.env (cp .env.ejemplo .env y pon las claves)"; exit 1; }
cd "$R"
# compose reconstruye solo las imágenes cuyo contexto ha cambiado y recrea solo los contenedores afectados
docker compose up -d --build --remove-orphans 2>&1 | grep -vE '^\s*$' | sed 's/^/    /'
docker image prune -f >/dev/null 2>&1

sleep 2
if curl -sf -m 5 http://localhost/ranking-comandos/api/salud >/dev/null; then
  ok "Ranking OK: $(curl -s -m 5 http://localhost/ranking-comandos/api/salud)"
else
  fallo "El ranking no responde tras el despliegue. Logs:"; docker compose logs --tail=20 | sed 's/^/    /'; exit 1
fi
docker compose ps --format 'table {{.Service}}\t{{.Status}}' | sed 's/^/    /'
