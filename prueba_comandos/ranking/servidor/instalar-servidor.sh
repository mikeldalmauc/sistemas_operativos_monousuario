#!/usr/bin/env bash
# =============================================================================
#  Instalación del SERVIDOR del ranking (Ubuntu Server en IsardVDI) desde cero.
#  Idempotente: se puede ejecutar las veces que haga falta.
#
#  Uso (como usuario normal con sudo, NO como root):
#     git clone https://github.com/mikeldalmauc/sistemas_operativos_monousuario
#     bash sistemas_operativos_monousuario/prueba_comandos/ranking/servidor/instalar-servidor.sh
#
#  Hace, en este orden:
#    1. paquetes base + idioma castellano + teclado es
#    2. red: NetworkManager único gestor, IP fija en la red 2SMA, DHCP (dnsmasq) para los alumnos
#    3. Docker + compose v2, usuario en el grupo docker
#    4. ranking: .env con claves, docker compose up
#    5. terminal: zsh + oh-my-zsh + powerlevel10k + autosugerencias + resaltado + sudo (Esc Esc) + eza (iconos)
#  Cada paso se puede saltar con SALTAR_RED=1, SALTAR_DOCKER=1, SALTAR_RANKING=1, SALTAR_ZSH=1
# =============================================================================
set -u

# ---------------------------- CONFIGURACIÓN ----------------------------------
IFAZ_2SMA="${IFAZ_2SMA:-enp2s0}"            # interfaz conectada a la red 2SMA (ip -br a)
IP_2SMA="${IP_2SMA:-192.168.2.1/24}"          # IP fija del servidor en 2SMA
DHCP_RANGO="${DHCP_RANGO:-192.168.2.50,192.168.2.250,12h}"
REPO_URL="${REPO_URL:-https://github.com/mikeldalmauc/sistemas_operativos_monousuario}"
REPO_DIR="${REPO_DIR:-$HOME/sistemas_operativos_monousuario}"
CLAVE_ALUMNOS="${CLAVE_ALUMNOS:-som-2026}"    # debe coincidir con CLAVE en prueba_comandos/config.env
# -----------------------------------------------------------------------------

C_V=$'\e[1;32m'; C_A=$'\e[1;33m'; C_R=$'\e[1;31m'; C_M=$'\e[1;35m'; C_F=$'\e[0m'
paso()  { echo; echo "${C_M}══ $* ══${C_F}"; }
ok()    { echo "${C_V}✔${C_F} $*"; }
aviso() { echo "${C_A}!${C_F} $*"; }
fallo() { echo "${C_R}✘ $*${C_F}"; }

[ "$(id -u)" -eq 0 ] && { fallo "Ejecútalo como tu usuario normal, no como root (el script usa sudo cuando toca)."; exit 1; }
sudo -v || { fallo "Necesito sudo."; exit 1; }
export DEBIAN_FRONTEND=noninteractive

# ============================ 1. PAQUETES E IDIOMA ============================
paso "1/5 Paquetes base e idioma"
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ca-certificates dnsmasq locales console-setup \
  zsh fzf bat tree htop unzip fonts-powerline zsh-autosuggestions zsh-syntax-highlighting >/dev/null
# eza (ls con iconos) está en Ubuntu 24.04; si no, se intenta desde su repo oficial
if ! command -v eza >/dev/null; then
  if ! sudo apt-get install -y -qq eza >/dev/null 2>&1; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg 2>/dev/null \
      && echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list >/dev/null \
      && sudo apt-get update -qq && sudo apt-get install -y -qq eza >/dev/null || aviso "eza no disponible; se usará ls normal"
  fi
fi
ok "Paquetes instalados"

# Castellano + teclado español
sudo sed -i 's/^# *es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen
grep -q '^es_ES.UTF-8' /etc/locale.gen || echo 'es_ES.UTF-8 UTF-8' | sudo tee -a /etc/locale.gen >/dev/null
sudo locale-gen >/dev/null
sudo update-locale LANG=es_ES.UTF-8 LC_ALL=
sudo sed -i 's/^XKBLAYOUT=.*/XKBLAYOUT="es"/' /etc/default/keyboard
sudo localectl set-keymap es 2>/dev/null || true
sudo localectl set-x11-keymap es 2>/dev/null || true
ok "Idioma es_ES.UTF-8 y teclado es (efectivo al volver a entrar)"

# ================================= 2. RED ====================================
if [ "${SALTAR_RED:-0}" != 1 ]; then
  paso "2/5 Red: IP fija en $IFAZ_2SMA ($IP_2SMA) y DHCP para los alumnos"
  if ! ip link show "$IFAZ_2SMA" >/dev/null 2>&1; then
    fallo "No existe la interfaz $IFAZ_2SMA. Mira 'ip -br a' y vuelve a lanzar con IFAZ_2SMA=xxx bash $0"; exit 1
  fi
  if command -v nmcli >/dev/null; then
    # NetworkManager como único gestor (evita el doble DHCP de systemd-networkd + NM)
    [ -d /etc/cloud ] && echo 'network: {config: disabled}' | sudo tee /etc/cloud/cloud.cfg.d/99-nonet.cfg >/dev/null
    for f in /etc/netplan/*.yaml; do
      case "$(basename "$f")" in 90-NM-*) ;; *) grep -q 'renderer: NetworkManager' "$f" 2>/dev/null && ! grep -q 'dhcp4' "$f" || \
        printf 'network:\n  version: 2\n  renderer: NetworkManager\n' | sudo tee "$f" >/dev/null ;; esac
    done
    sudo netplan apply 2>/dev/null
    # perfil de NM para la interfaz 2SMA
    if nmcli -g NAME con show | grep -qx 2sma; then con=2sma
    else con="$(nmcli -g NAME,DEVICE con show | awk -F: -v d="$IFAZ_2SMA" '$2==d{print $1; exit}')"; fi
    if [ -z "$con" ]; then sudo nmcli con add type ethernet ifname "$IFAZ_2SMA" con-name 2sma >/dev/null; con=2sma; fi
    sudo nmcli con mod "$con" connection.id 2sma connection.interface-name "$IFAZ_2SMA" \
      ipv4.method manual ipv4.addresses "$IP_2SMA" ipv4.never-default yes ipv6.method disabled
    sudo nmcli con up 2sma >/dev/null && ok "NetworkManager: 2sma = $IP_2SMA (sin puerta de enlace, internet sigue por la otra red)"
  else
    # sin NetworkManager: netplan con systemd-networkd
    sudo tee /etc/netplan/60-2sma.yaml >/dev/null <<EOF
network:
  version: 2
  ethernets:
    $IFAZ_2SMA:
      dhcp4: false
      addresses: [$IP_2SMA]
EOF
    sudo chmod 600 /etc/netplan/60-2sma.yaml; sudo netplan apply && ok "netplan: $IFAZ_2SMA = $IP_2SMA"
  fi
  # dnsmasq solo como DHCP (sin DNS), solo por la interfaz 2SMA, sin router ni DNS para los clientes
  sudo tee /etc/dnsmasq.d/2sma.conf >/dev/null <<EOF
port=0
interface=$IFAZ_2SMA
bind-dynamic
dhcp-range=$DHCP_RANGO
dhcp-option=3
dhcp-option=6
EOF
  # que arranque después de que la interfaz tenga IP (si no, falla en el arranque)
  sudo mkdir -p /etc/systemd/system/dnsmasq.service.d
  printf '[Unit]\nAfter=network-online.target\nWants=network-online.target\n' | sudo tee /etc/systemd/system/dnsmasq.service.d/esperar-red.conf >/dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable dnsmasq >/dev/null 2>&1; sudo systemctl restart dnsmasq && ok "dnsmasq reparte $DHCP_RANGO por $IFAZ_2SMA"
  command -v ufw >/dev/null && sudo ufw status | grep -q active && { sudo ufw allow 8080/tcp >/dev/null; sudo ufw allow in on "$IFAZ_2SMA" to any port 67 proto udp >/dev/null; ok "ufw: 8080 y DHCP abiertos"; }
fi

# ================================ 3. DOCKER ===================================
if [ "${SALTAR_DOCKER:-0}" != 1 ]; then
  paso "3/5 Docker y compose v2"
  command -v docker >/dev/null || sudo apt-get install -y -qq docker.io >/dev/null
  docker compose version >/dev/null 2>&1 || sudo apt-get install -y -qq docker-compose-v2 >/dev/null
  sudo systemctl enable --now docker >/dev/null 2>&1
  id -nG "$USER" | grep -qw docker || { sudo usermod -aG docker "$USER"; aviso "Añadido al grupo docker: cierra sesión y vuelve a entrar para usar docker sin sudo"; }
  ok "Docker $(docker --version | cut -d' ' -f3 | tr -d ,) · $(docker compose version --short 2>/dev/null)"
fi

# =============================== 4. RANKING ===================================
if [ "${SALTAR_RANKING:-0}" != 1 ]; then
  paso "4/5 Ranking (repo, claves y contenedores)"
  if [ -d "$REPO_DIR/.git" ]; then git -C "$REPO_DIR" pull -q && ok "Repo actualizado"; else git clone -q "$REPO_URL" "$REPO_DIR" && ok "Repo clonado en $REPO_DIR"; fi
  R="$REPO_DIR/prueba_comandos/ranking"
  if [ ! -f "$R/.env" ]; then
    admin="$(tr -dc 'a-z0-9' </dev/urandom | head -c 20)"
    printf 'CLAVE=%s\nCLAVE_ADMIN=%s\n' "$CLAVE_ALUMNOS" "$admin" > "$R/.env"; chmod 600 "$R/.env"
    aviso "Creado $R/.env con una CLAVE_ADMIN nueva (la ves con: cat $R/.env)"
  else ok "Ya existe $R/.env, se conserva"; fi
  mkdir -p "$R/datos"
  ( cd "$R" && sudo docker compose up -d --build 2>&1 | tail -3 )
  sleep 2
  if curl -sf -m 5 http://localhost:8080/api/salud >/dev/null; then ok "Ranking en marcha: http://${IP_2SMA%/*}:8080"; else fallo "El ranking no responde; mira: cd $R && docker compose logs"; fi
fi

# ================================= 5. ZSH ====================================
if [ "${SALTAR_ZSH:-0}" != 1 ]; then
  paso "5/5 Terminal: zsh + oh-my-zsh + powerlevel10k"
  OMZ="$HOME/.oh-my-zsh"; ZC="$OMZ/custom"
  [ -d "$OMZ" ] || git clone -q --depth 1 https://github.com/ohmyzsh/ohmyzsh "$OMZ"
  [ -d "$ZC/themes/powerlevel10k" ]        || git clone -q --depth 1 https://github.com/romkatv/powerlevel10k "$ZC/themes/powerlevel10k"
  [ -d "$ZC/plugins/zsh-autosuggestions" ] || git clone -q --depth 1 https://github.com/zsh-users/zsh-autosuggestions "$ZC/plugins/zsh-autosuggestions"
  [ -d "$ZC/plugins/zsh-syntax-highlighting" ] || git clone -q --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting "$ZC/plugins/zsh-syntax-highlighting"
  [ -f "$HOME/.zshrc" ] && ! grep -q 'instalar-servidor' "$HOME/.zshrc" && cp "$HOME/.zshrc" "$HOME/.zshrc.antes-$(date +%Y%m%d)"
  cat > "$HOME/.zshrc" <<'EOF'
# .zshrc generado por instalar-servidor.sh (ranking SOM). Edita lo que quieras.
# --- powerlevel10k: arranque instantáneo ---
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
# sudo: pulsa Esc dos veces y añade/quita sudo al principio de la línea
# zsh-autosuggestions: sugiere en gris el comando del historial; → para aceptarlo
# zsh-syntax-highlighting: comandos en verde si existen, rojo si no
# fzf: Ctrl+R busca en el historial, Ctrl+T busca ficheros
plugins=(git sudo docker docker-compose fzf command-not-found colored-man-pages zsh-autosuggestions zsh-syntax-highlighting)
source $ZSH/oh-my-zsh.sh

export LANG=es_ES.UTF-8
export EDITOR=nano
export PATH="$HOME/.local/bin:$PATH"

# --- ls con iconos y colores (eza) ---
if command -v eza >/dev/null; then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza -lah --icons --group-directories-first --git'
  alias la='eza -a --icons --group-directories-first'
  alias lt='eza --tree --level=2 --icons'
else
  alias ll='ls -lah --color=auto'
fi
command -v batcat >/dev/null && alias cat='batcat --paging=never --style=plain'
alias dc='docker compose'
alias ranking='cd ~/sistemas_operativos_monousuario/prueba_comandos/ranking'

# --- historial ---
HISTSIZE=50000; SAVEHIST=50000
setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY

[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
EOF
  [ "$(getent passwd "$USER" | cut -d: -f7)" = "$(command -v zsh)" ] || sudo chsh -s "$(command -v zsh)" "$USER"
  ok "zsh es tu shell. La primera vez que entres arranca el asistente de powerlevel10k (p10k configure)"
fi

# ================================ RESUMEN ====================================
paso "Resumen"
ip -br a | grep -E "^$IFAZ_2SMA" || true
echo "  Ranking:        http://${IP_2SMA%/*}:8080   (los alumnos: SERVIDOR_URL en config.env)"
echo "  Claves:         cat $REPO_DIR/prueba_comandos/ranking/.env"
echo "  Administrar:    cd $REPO_DIR/prueba_comandos/ranking && bash admin.sh listar"
echo "  Comprobar DHCP: en un cliente, ip -br a → su interfaz 2SMA debe tener ${IP_2SMA%.*}.x"
echo
aviso "Cierra sesión y vuelve a entrar (o reinicia) para que apliquen idioma, teclado, grupo docker y zsh."
echo "  Nota sobre los iconos: powerlevel10k y eza usan una fuente Nerd Font. En la consola de Isard"
echo "  no se puede cambiar la fuente, así que en el asistente de p10k contesta que NO ves los iconos"
echo "  y elige un estilo sin ellos; por SSH desde un equipo con la fuente MesloLGS NF se ven todos."
