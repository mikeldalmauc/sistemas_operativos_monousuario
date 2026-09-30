#!/usr/bin/env bash
# NIVEL 2 · Usuarios, permisos, sudo y servicios (2.º trimestre · CM6)
# Requiere: sudo, systemd (Linux Mint o Arch instalados por el alumno).

nivel2_preparar() {
  local d="$1" e="$1/.prueba"
  command -v systemctl >/dev/null || { error "Este nivel necesita systemd (systemctl). Úsalo en tu máquina virtual."; return 1; }
  echo "La preparación necesita sudo (crea dos servicios de prueba y /etc/prueba)."
  sudo -v || return 1

  mkdir -p "$d/scripts" "$e"
  printf 'contraseña de la wifi: 1234\n' > "$d/privado.txt"
  printf 'turnos del taller\nlunes: ana\nmartes: ben\n' > "$d/compartido.txt"
  cat > "$d/scripts/saludo.sh" <<'EOF'
#!/bin/bash
# Escribe un saludo en la carpeta de la prueba
echo "hola $(id -un)" > "$(dirname "$0")/../saludo.txt"
echo "Saludo escrito en saludo.txt"
EOF
  chmod 644 "$d/scripts/saludo.sh"

  # configuración del sistema
  sudo mkdir -p /etc/prueba
  printf '# configuración de la prueba\nnivel=bajo\nregistro=si\n' | sudo tee /etc/prueba/prueba.conf >/dev/null
  sudo chmod 644 /etc/prueba/prueba.conf

  # dos servicios inofensivos: uno apagado que hay que arrancar, otro encendido que hay que parar
  for s in prueba-servicio prueba-ruido; do
    sudo tee /etc/systemd/system/$s.service >/dev/null <<EOF
[Unit]
Description=Servicio de prueba SOM ($s)

[Service]
ExecStart=/bin/sleep infinity

[Install]
WantedBy=multi-user.target
EOF
  done
  sudo systemctl daemon-reload
  sudo systemctl disable --now prueba-servicio >/dev/null 2>&1
  sudo systemctl enable  --now prueba-ruido    >/dev/null 2>&1
  return 0
}

nivel2_limpiar() {
  echo "La limpieza necesita sudo (borra usuarios, grupo, /srv/taller, /etc/prueba y los servicios)."
  sudo -v || return 1
  for s in prueba-servicio prueba-ruido; do
    sudo systemctl disable --now $s >/dev/null 2>&1
    sudo rm -f /etc/systemd/system/$s.service
  done
  sudo systemctl daemon-reload
  sudo rm -rf /etc/prueba /srv/taller
  for u in ana ben; do id "$u" >/dev/null 2>&1 && sudo userdel -r "$u" 2>/dev/null; done
  getent group taller >/dev/null && sudo groupdel taller
  return 0
}

nivel2_mision() {
cat <<'EOF'
# NIVEL 2 · Usuarios, permisos, sudo y servicios

Todo lo del nivel 1 se da por sabido. Carpeta de trabajo: ~/prueba_nivel2 (tienes privado.txt,
compartido.txt y scripts/saludo.sh). Varias tareas tocan el sistema: necesitarás sudo.

 1. Crea el grupo  taller  y los usuarios  ana  y  ben  (con carpeta personal).
    ana debe pertenecer al grupo taller; ben NO.
 2. Crea la carpeta  /srv/taller  con propietario root, grupo taller y permisos 770.
 3. Actuando COMO ana (cambia de usuario), crea el fichero  /srv/taller/ana.txt .
    Debe pertenecer a ana.
 4. privado.txt: solo tu usuario puede leerlo y escribirlo (nadie más nada).
    compartido.txt: grupo taller, tú lees y escribes, el grupo solo lee, los demás nada.
 5. scripts/saludo.sh no tiene permiso de ejecución. Dáselo y ejecútalo desde la carpeta
    de la prueba con  ./scripts/saludo.sh  (debe aparecer saludo.txt).
 6. Arranca el servicio  prueba-servicio  y haz que se inicie automáticamente con el sistema.
 7. Para el servicio  prueba-ruido  y evita que arranque con el sistema.
 8. En  /etc/prueba/prueba.conf  cambia  nivel=bajo  por  nivel=alto  (fichero de root).

Puntuación: 100000 / (segundos + 5·comandos + 60).
EOF
}

nivel2_comprobar() {
  local d="$1" yo; yo="$(id -un)"
  echo "(la comprobación usa sudo para mirar dentro de /srv/taller)"; sudo -v
  paso "1. Grupo taller; ana (en taller) y ben (fuera de taller) con carpeta personal" \
       bash -c "getent group taller >/dev/null && id ana >/dev/null && id ben >/dev/null && id -nG ana | tr ' ' '\n' | grep -qx taller && ! (id -nG ben | tr ' ' '\n' | grep -qx taller) && [ -d /home/ana ] && [ -d /home/ben ]"
  paso "2. /srv/taller es root:taller con permisos 770" \
       bash -c "[ -d /srv/taller ] && [ \"\$(stat -c %U:%G:%a /srv/taller)\" = root:taller:770 ]"
  paso "3. /srv/taller/ana.txt existe y pertenece a ana" \
       bash -c "[ \"\$(sudo stat -c %U /srv/taller/ana.txt 2>/dev/null)\" = ana ]"
  paso "4. privado.txt 600 y compartido.txt 640 con grupo taller" \
       bash -c "[ \"\$(stat -c %a '$d/privado.txt')\" = 600 ] && [ \"\$(stat -c %a:%G '$d/compartido.txt')\" = 640:taller ]"
  paso "5. saludo.sh ejecutable y ejecutado (saludo.txt dice 'hola $yo')" \
       bash -c "[ -x '$d/scripts/saludo.sh' ] && grep -qx 'hola $yo' '$d/saludo.txt'"
  paso "6. prueba-servicio activo y habilitado" \
       bash -c "systemctl is-active --quiet prueba-servicio && systemctl is-enabled --quiet prueba-servicio"
  paso "7. prueba-ruido parado y deshabilitado" \
       bash -c "! systemctl is-active --quiet prueba-ruido && [ \"\$(systemctl is-enabled prueba-ruido 2>/dev/null)\" = disabled ]"
  paso "8. /etc/prueba/prueba.conf tiene nivel=alto" \
       bash -c "grep -qx 'nivel=alto' /etc/prueba/prueba.conf && ! grep -q 'nivel=bajo' /etc/prueba/prueba.conf"
}
