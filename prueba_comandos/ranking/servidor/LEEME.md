# Servidor del ranking · instalación desde cero

Ubuntu Server (escritorio de IsardVDI) con dos redes: la Default de Isard (internet) y **1SMA**
(switch compartido con los escritorios de los alumnos). Un solo script lo deja todo:

```bash
git clone https://github.com/mikeldalmauc/sistemas_operativos_monousuario
bash sistemas_operativos_monousuario/prueba_comandos/ranking/servidor/instalar-servidor.sh
```

Como usuario normal con sudo (no root). Se puede repetir sin miedo: cada paso comprueba lo que ya hay.
Al acabar: cerrar sesión y volver a entrar.

| Paso | Qué deja | Saltarlo |
|---|---|---|
| 1 | git, curl, dnsmasq, openssh-server, fzf, bat, eza, htop…; idioma `es_ES.UTF-8`; teclado `es` | — |
| 2 | NetworkManager único gestor; `enp3s0` (la de 1SMA; Default y Wireguard van antes) = `192.168.2.1/24` sin puerta de enlace; dnsmasq reparte `192.168.2.50-250` solo por esa interfaz, sin router ni DNS | `SALTAR_RED=1` |
| 3 | docker.io + compose v2; tu usuario en el grupo `docker` | `SALTAR_DOCKER=1` |
| 4 | clona/actualiza el repo, crea `ranking/.env` (CLAVE_ADMIN aleatoria) si no existe, `docker compose up -d --build` | `SALTAR_RANKING=1` |
| 5 | bash con alias (`ll` con `eza`, `cat` con `bat`), fzf (Ctrl+R) y Esc Esc → `sudo`, en `~/.bashrc.aula` | `SALTAR_ZSH=1` |
| 6 | `openssh-server` activo y las claves públicas de `github.com/mikeldalmauc.keys` en `~/.ssh/authorized_keys` (para entrar por el bastión de Isard; sube tu `.pub` a GitHub → Settings → SSH keys) | `SALTAR_SSH=1` |

Si la interfaz de 1SMA no es `enp3s0` (míralo con `ip -br a`): `IFAZ_1SMA=enp2s0 bash instalar-servidor.sh`.
Otras variables: `IP_1SMA`, `DHCP_RANGO`, `REPO_URL`, `CLAVE_ALUMNOS`, `GITHUB_USER`.

Después: `bash ../admin.sh listar` para administrar, `cat ../.env` para ver las claves.

## Despliegue

Tres formas, de menos a más automática. Todas ejecutan `desplegar.sh` en el servidor: `git pull`,
`docker compose up -d --build` (solo reconstruye lo que cambió) y comprobación de `/api/salud`.

1. **A mano, por SSH**: `ssh servidor-som 'cd ~/sistemas_operativos_monousuario && git pull --ff-only && bash prueba_comandos/ranking/servidor/desplegar.sh'`
2. **Desde Windows en un paso**: `.\prueba_comandos\ranking\servidor\desplegar.ps1 "mensaje del commit"`
   → `git add -A`, commit, push y despliegue (sin mensaje solo despliega).
3. **GitHub Actions al hacer push a `main`** (`.github/workflows/desplegar.yml`), si cambia algo en
   `prueba_comandos/ranking/`. Llega al servidor por el bastión SSH de Isard. Configuración, una vez:
   - En Windows, una clave **solo para esto**: `ssh-keygen -t ed25519 -f $HOME\.ssh\despliegue -C despliegue-github -N '""'`
   - La pública (`despliegue.pub`) → una línea más en `claves_ssh.pub` **y** en el servidor
     (`ssh servidor-som "echo '$(Get-Content $HOME\.ssh\despliegue.pub)' >> ~/.ssh/authorized_keys"`).
   - En GitHub, repo → Settings → Secrets and variables → Actions:
     - Variable `DESPLIEGUE_AUTOMATICO` = `si` (ponla en `no` para pausarlo sin borrar nada).
     - Secrets `DESPLIEGUE_SSH_KEY` (contenido completo de `despliegue`, la privada),
       `DESPLIEGUE_SSH_HOST` = `vdi.fpzornotzalh.eus`, `DESPLIEGUE_SSH_PORT` = `443`,
       `DESPLIEGUE_SSH_USER` = ID del bastión del escritorio.
   - Prueba: pestaña Actions → "Desplegar ranking" → Run workflow. Luego cada push despliega solo.
   Si el servidor está apagado, el workflow falla y lo verás en rojo en Actions: no pasa nada,
   despliega al siguiente push o con "Run workflow".
