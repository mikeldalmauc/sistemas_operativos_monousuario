# Imagen para jugar a «La Mazmorra de los Comandos» sin máquina virtual.
#
# Ubuntu 24.04 (la base de Linux Mint) + Python 3, con un usuario normal
# «alumno». NO se juega como root: root se salta los permisos y las puertas
# del nivel 2 no se cerrarían.
#
# Solo lleva lo que recibe el alumno en el zip: ni soluciones ni verificador.

FROM ubuntu:24.04

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 bash-completion less nano sudo \
    && rm -rf /var/lib/apt/lists/*

# La imagen trae un usuario «ubuntu» con el UID 1000: se cambia por «alumno».
# Contraseña de «alumno» y de root: «alumno». El alumno puede usar sudo con ella.
RUN userdel -r ubuntu 2>/dev/null || true \
    && useradd --create-home --uid 1000 --shell /bin/bash alumno \
    && echo 'alumno:alumno' | chpasswd \
    && echo 'root:alumno' | chpasswd \
    && usermod -aG sudo alumno

COPY mazmorra/ /opt/mazmorra-juego/mazmorra/
COPY instalar.sh desinstalar.sh docs/guia-alumno.md /opt/mazmorra-juego/
COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/bienvenida.sh /etc/mazmorra-bienvenida.sh

# Los ficheros viven en Windows/Drive: por si algún editor mete CRLF o Drive
# cuela sus desktop.ini. El aviso de bienvenida se carga en cada terminal.
RUN find /opt/mazmorra-juego /usr/local/bin/entrypoint.sh /etc/mazmorra-bienvenida.sh \
        -type f \( -name '*.sh' -o -name '*.py' \) -exec sed -i 's/\r$//' {} + \
    && find /opt/mazmorra-juego \( -name 'desktop.ini' -o -name '__pycache__' \) \
        -prune -exec rm -rf {} + \
    && echo '. /etc/mazmorra-bienvenida.sh' >> /etc/bash.bashrc

USER alumno
ENV USER=alumno \
    HOME=/home/alumno
WORKDIR /home/alumno

ENTRYPOINT ["entrypoint.sh"]
CMD ["bash"]
