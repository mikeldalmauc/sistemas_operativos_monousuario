# Servidor del ranking · instalación desde cero

Ubuntu Server (escritorio de IsardVDI) con dos redes: la Default de Isard (internet) y **2SMA**
(switch compartido con los escritorios de los alumnos). Un solo script lo deja todo:

```bash
git clone https://github.com/mikeldalmauc/sistemas_operativos_monousuario
bash sistemas_operativos_monousuario/prueba_comandos/ranking/servidor/instalar-servidor.sh
```

Como usuario normal con sudo (no root). Se puede repetir sin miedo: cada paso comprueba lo que ya hay.
Al acabar: cerrar sesión y volver a entrar. La primera vez que entre zsh arranca el asistente de
powerlevel10k; en la consola de Isard no hay Nerd Font, así que contesta que **no** ves los iconos.

| Paso | Qué deja | Saltarlo |
|---|---|---|
| 1 | git, curl, dnsmasq, zsh, fzf, bat, eza, htop…; idioma `es_ES.UTF-8`; teclado `es` | — |
| 2 | NetworkManager único gestor; `enp2s0` = `192.168.2.1/24` sin puerta de enlace; dnsmasq reparte `192.168.2.50-250` solo por esa interfaz, sin router ni DNS | `SALTAR_RED=1` |
| 3 | docker.io + compose v2; tu usuario en el grupo `docker` | `SALTAR_DOCKER=1` |
| 4 | clona/actualiza el repo, crea `ranking/.env` (CLAVE_ADMIN aleatoria) si no existe, `docker compose up -d --build` | `SALTAR_RANKING=1` |
| 5 | zsh + oh-my-zsh + powerlevel10k + autosugerencias + resaltado + `sudo` (Esc Esc) + `eza` con iconos + fzf (Ctrl+R) | `SALTAR_ZSH=1` |

Si la interfaz de 2SMA no es `enp2s0` (míralo con `ip -br a`): `IFAZ_2SMA=enp3s0 bash instalar-servidor.sh`.
Otras variables: `IP_2SMA`, `DHCP_RANGO`, `REPO_URL`, `CLAVE_ALUMNOS`.

Después: `bash ../admin.sh listar` para administrar, `cat ../.env` para ver las claves.
