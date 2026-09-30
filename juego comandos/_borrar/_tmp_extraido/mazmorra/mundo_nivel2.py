"""Nivel 2 · Las Catacumbas de los Permisos (dificultad extra).

Aquí no hay pergaminos ni hechizos: la «magia» son los permisos de Linux.
Cada sala plantea una situación real (un fichero que no se puede leer, una
carpeta en la que no se puede entrar o escribir, un programa que no arranca)
y se cierra con un ritual: un script que hay que hacer ejecutable y lanzar
con ./ritual.sh. El ritual comprueba las condiciones de la sala y da un sello.

Las puertas son carpetas con permisos 000: las abre el propio alumno con chmod.
"""

_RITUAL = """#!/bin/bash
# Ritual de {sala}.
#
# Este pergamino es un PROGRAMA. Comprueba que has completado la sala y,
# si es así, te entrega su sello.
#
# Solo tiene poder si puede EJECUTARSE:
#     chmod u+x ritual.sh      (le das permiso de ejecución)
#     ./ritual.sh              (lo ejecutas; ./ significa «el de esta carpeta»)

if command -v mazmorra >/dev/null 2>&1; then
    exec mazmorra ritual "$0"
else
    exec "$HOME/.mazmorra/bin/mazmorra" ritual "$0"
fi
"""


def _ritual(sala: str) -> str:
    return _RITUAL.format(sala=sala)


SALAS = [
    # ----------------------------------------------------------- VESTÍBULO
    {
        "id": "vestibulo",
        "padre": None,
        "carpeta": "vestibulo",
        "titulo": "El Vestíbulo",
        "mapa": "VESTÍBULO",
        "pos": (0, 0),
        "arte": "vestibulo",
        "descripcion": (
            "Un vestíbulo húmedo, con el techo tan bajo que casi lo tocas. En la pared hay una "
            "inscripción, pero está cubierta por una capa negra: no puedes leerla. Aquí abajo todo se "
            "rige por PERMISOS, y los ves con `ls -l`.\n\n"
            "Cada fichero y carpeta tiene tres llaves: r (leer), w (escribir) y x (ejecutar). Y "
            "tres dueños posibles de cada llave: u (el usuario dueño, tú), g (su grupo) y o (los "
            "otros). `ls -l` te enseña las nueve casillas: rwxr-xr-- se lee «el dueño puede todo, "
            "el grupo leer y ejecutar, los demás solo leer». Y ---------- significa que nadie "
            "puede nada.\n\n"
            "Como eres el dueño de todo lo que hay en estas catacumbas, tú decides: `chmod u+r "
            "fichero` te da (+) la llave de lectura (r) como dueño (u). `chmod u-r` te la quita."
        ),
        "objetivo": (
            "Consigue leer inscripcion.txt, y después celebra el ritual: hazlo ejecutable y lánzalo "
            "con ./ritual.sh"
        ),
        "ficheros": {
            "inscripcion.txt": (
                "EL VESTÍBULO\n"
                "\n"
                "Si lees esto, ya has usado chmod por primera vez. Bien.\n"
                "\n"
                "Lo que has visto en ls -l:\n"
                "    -rw-r--r--  1 alumno alumno  ...  fichero\n"
                "    │└┬┘└┬┘└┬┘\n"
                "    │ u  g  o        u = dueño, g = grupo, o = otros\n"
                "    └ tipo: - fichero, d carpeta\n"
                "\n"
                "    chmod u+r fichero     añade r al dueño\n"
                "    chmod u-w fichero     quita w al dueño\n"
                "    chmod u=rw fichero    fija exactamente rw para el dueño\n"
                "    chmod +x fichero      añade x a todos (u, g y o)\n"
                "\n"
                "Ahora el ritual. ritual.sh es un programa, pero un programa solo arranca si\n"
                "tiene permiso de ejecución (x). Analogía: la x es la llave de contacto de un\n"
                "coche: sin ella, el coche existe pero no arranca.\n"
                "\n"
                "    chmod u+x ritual.sh\n"
                "    ./ritual.sh\n"
                "\n"
                "El ./ significa «el que está en esta carpeta». Sin él, el terminal buscaría un\n"
                "programa llamado ritual.sh instalado en el sistema, y no lo encontraría.\n"
            ),
            "ritual.sh": _ritual("El Vestíbulo"),
        },
        "permisos": {"inscripcion.txt": 0o000, "ritual.sh": 0o644, "galeria": 0o000},
        "condiciones": [
            {"tipo": "modo", "ruta": "inscripcion.txt", "bits": 0o400,
             "texto": "Puedes leer inscripcion.txt (chmod u+r inscripcion.txt)"},
        ],
        "pistas": [
            "`ls -l` muestra los permisos. Fíjate en las diez primeras letras de cada línea: "
            "---------- quiere decir que nadie puede nada, ni siquiera tú, que eres el dueño.",
            "`chmod u+r inscripcion.txt` te da permiso de lectura (r) como dueño (u). "
            "Luego `cat inscripcion.txt`.",
            "`chmod u+r inscripcion.txt` → `cat inscripcion.txt` → `chmod u+x ritual.sh` → "
            "`./ritual.sh`. Después abre la puerta: `chmod u+rwx galeria` y `cd galeria`.",
        ],
        "exito": (
            "El sello del vestíbulo se enciende en tu mano. Ya sabes lo básico: mirar permisos con "
            "ls -l, darlos y quitarlos con chmod, y que un programa necesita la x para arrancar."
        ),
    },
    # -------------------------------------------------------------- GALERÍA
    {
        "id": "galeria",
        "padre": "vestibulo",
        "carpeta": "galeria",
        "titulo": "La Galería de los Espejos",
        "mapa": "GALERÍA",
        "pos": (1, 0),
        "arte": "galeria",
        "descripcion": (
            "Una galería larga con espejos a ambos lados. El más grande, espejo/, es una carpeta. "
            "Puedes ver lo que hay dentro (`ls espejo`), pero no puedes entrar (`cd espejo` falla) "
            "ni leer nada de lo que contiene. Es un escaparate: miras, pero no tocas.\n\n"
            "En una CARPETA las llaves significan otra cosa: r = ver la lista de lo que hay, w = "
            "crear y borrar cosas dentro, x = ATRAVESARLA (entrar con cd o llegar a lo que hay "
            "dentro). Sin x, la carpeta es solo una lista. `ls -ld espejo` te enseña los permisos "
            "de la carpeta en sí (la d de -ld es para que no te enseñe su contenido)."
        ),
        "objetivo": (
            "Consigue entrar en espejo/ y leer espejo/reflejo.txt. Luego, el ritual."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA GALERÍA\n"
                "\n"
                "En una carpeta:\n"
                "    r    listar lo que hay          (ls carpeta)\n"
                "    w    crear y borrar dentro      (touch, mkdir, rm, mv)\n"
                "    x    entrar y atravesar         (cd carpeta, cat carpeta/fichero)\n"
                "\n"
                "    ls -ld espejo        permisos de la carpeta espejo (no de su contenido)\n"
                "    chmod u+x espejo     ya puedes entrar\n"
                "    cat espejo/reflejo.txt\n"
            ),
            "ritual.sh": _ritual("La Galería de los Espejos"),
        },
        "carpetas": {
            "espejo": {
                "reflejo.txt": (
                    "Te ves a ti mismo, pero al revés. En el reflejo, tú tienes todas las llaves.\n"
                    "Siempre las has tenido: eres el dueño.\n"
                ),
            },
        },
        "permisos": {"espejo": 0o444, "ritual.sh": 0o644, "escriba": 0o000},
        "condiciones": [
            {"tipo": "sello", "sala": "vestibulo", "texto": "Ritual del vestíbulo completado"},
            {"tipo": "modo", "ruta": "espejo", "bits": 0o100,
             "texto": "Puedes entrar en espejo/ (chmod u+x espejo)"},
        ],
        "pistas": [
            "`ls -ld espejo` → dr--r--r--. Tiene r (puedes listar) pero no x: no puedes entrar ni "
            "llegar a lo que hay dentro.",
            "`chmod u+x espejo` añade la x al dueño. Comprueba con `cd espejo` (y vuelve con `cd ..`) "
            "o directamente `cat espejo/reflejo.txt`.",
            "`chmod u+x espejo` → `cat espejo/reflejo.txt` → `chmod u+x ritual.sh` → `./ritual.sh` "
            "→ `chmod 700 escriba` → `cd escriba`.",
        ],
        "exito": (
            "Los espejos se apagan uno a uno. Regla grabada a fuego: en una carpeta, sin x no se "
            "entra, por mucho r que tenga."
        ),
    },
    # -------------------------------------------------------------- ESCRIBA
    {
        "id": "escriba",
        "padre": "galeria",
        "carpeta": "escriba",
        "titulo": "La Sala del Escriba",
        "mapa": "ESCRIBA",
        "pos": (2, 0),
        "arte": "escriba",
        "descripcion": (
            "Un pupitre, una pluma seca y una carpeta de documentos: archivo/. Puedes entrar y "
            "mirar (tiene r y x), pero no puedes crear nada dentro ni borrar: le falta la w. En una "
            "carpeta, la w es la llave para meter y sacar cosas.\n\n"
            "Dentro hay un fichero viejo, polvo.txt, protegido contra escritura (r--r--r--). Fíjate "
            "en algo importante: para BORRAR un fichero no hace falta poder escribir en el "
            "fichero, sino en la CARPETA que lo contiene. rm te preguntará si estás seguro; "
            "contesta y (o usa `rm -f` para que no pregunte)."
        ),
        "objetivo": (
            "Da permiso de escritura sobre archivo/, borra archivo/polvo.txt y deja tu firma en "
            "archivo/firma.txt (con tu nombre dentro). Luego, el ritual."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA SALA DEL ESCRIBA\n"
                "\n"
                "    chmod u+w archivo               ahora puedes crear y borrar dentro\n"
                "    rm archivo/polvo.txt            pregunta porque el fichero es r--; contesta y\n"
                "    echo Tu Nombre > archivo/firma.txt\n"
                "    ls -l archivo                   comprueba\n"
                "\n"
                "Borrar = modificar la carpeta (quitar una entrada de su lista).\n"
                "Por eso manda la w de la carpeta, no la del fichero.\n"
            ),
            "ritual.sh": _ritual("La Sala del Escriba"),
        },
        "carpetas": {
            "archivo": {
                "polvo.txt": "Polvo. Siglos de polvo.\n",
            },
        },
        "permisos": {"archivo/polvo.txt": 0o444, "archivo": 0o555, "ritual.sh": 0o644,
                     "numeros": 0o000},
        "condiciones": [
            {"tipo": "sello", "sala": "galeria", "texto": "Ritual de la galería completado"},
            {"tipo": "modo", "ruta": "archivo", "bits": 0o200,
             "texto": "archivo/ admite escritura del dueño (chmod u+w archivo)"},
            {"tipo": "no_existe", "ruta": "archivo/polvo.txt",
             "texto": "polvo.txt borrado (rm archivo/polvo.txt)"},
            {"tipo": "existe", "ruta": "archivo/firma.txt", "no_vacio": True,
             "texto": "archivo/firma.txt existe y tiene tu nombre dentro"},
        ],
        "pistas": [
            "`ls -ld archivo` → dr-xr-xr-x: sin w no se puede crear ni borrar dentro. "
            "`chmod u+w archivo`.",
            "`rm archivo/polvo.txt` (contesta y cuando pregunte). Después "
            "`echo TuNombre > archivo/firma.txt`.",
            "`chmod u+w archivo` → `rm -f archivo/polvo.txt` → `echo Ane > archivo/firma.txt` → "
            "`chmod u+x ritual.sh` → `./ritual.sh` → `chmod 700 numeros` → `cd numeros`.",
        ],
        "exito": (
            "La pluma seca se moja sola y firma en el aire. Segunda regla: quien manda sobre lo "
            "que hay dentro de una carpeta es la w de la carpeta."
        ),
    },
    # -------------------------------------------------------------- NÚMEROS
    {
        "id": "numeros",
        "padre": "escriba",
        "carpeta": "numeros",
        "titulo": "La Cámara de los Números",
        "mapa": "NÚMEROS",
        "pos": (2, 1),
        "arte": "numeros",
        "descripcion": (
            "Las paredes están cubiertas de números. Los antiguos no escribían rwx: usaban "
            "cifras. Cada llave vale: r = 4, w = 2, x = 1. Se suman por grupo: rwx = 7, rw- = 6, "
            "r-x = 5, r-- = 4, --- = 0. Y los tres grupos (u, g, o) forman un código de tres "
            "cifras: 755 = rwxr-xr-x, 644 = rw-r--r--, 700 = rwx------.\n\n"
            "Analogía: cada grupo es un bolsillo con monedas de 4, 2 y 1. El número dice cuánto "
            "hay en cada bolsillo. `chmod 750 carpeta` fija los tres bolsillos de golpe: aquí no se "
            "añade ni se quita, se DEJA EXACTAMENTE así.\n\n"
            "Tres encargos: la cámara del tesoro (tesoro/) tiene que quedar rwxr-x---: tú todo, "
            "el grupo entra y mira, los demás nada. El diario secreto (secreto.txt): solo tú "
            "puedes leerlo y escribirlo, nadie más nada. El pergamino publico.txt: todo el mundo "
            "puede leerlo, pero solo tú modificarlo."
        ),
        "objetivo": "Deja tesoro/, secreto.txt y publico.txt con los permisos exactos. Luego, el ritual.",
        "ficheros": {
            "inscripcion.txt": (
                "LA CÁMARA DE LOS NÚMEROS\n"
                "\n"
                "    r = 4   w = 2   x = 1        rwx = 7   rw- = 6   r-x = 5   r-- = 4   --- = 0\n"
                "\n"
                "    tesoro/       rwx r-x ---   →  7 5 0   →  chmod 750 tesoro\n"
                "    secreto.txt   rw- --- ---   →  ?\n"
                "    publico.txt   rw- r-- r--   →  ?\n"
                "\n"
                "    ls -l           comprueba ficheros\n"
                "    ls -ld tesoro   comprueba la carpeta\n"
            ),
            "secreto.txt": "Aquí van cosas que nadie más debería leer. Contraseñas, por ejemplo.\n",
            "publico.txt": "Aviso para todos los habitantes de las catacumbas: no toquéis nada.\n",
            "ritual.sh": _ritual("La Cámara de los Números"),
        },
        "carpetas": {"tesoro": {"moneda.txt": "Una moneda de oro.\n"}},
        "permisos": {"tesoro": 0o777, "secreto.txt": 0o666, "publico.txt": 0o600,
                     "ritual.sh": 0o644, "boveda": 0o000},
        "condiciones": [
            {"tipo": "sello", "sala": "escriba", "texto": "Ritual del escriba completado"},
            {"tipo": "modo", "ruta": "tesoro", "igual": 0o750,
             "texto": "tesoro/ es rwxr-x--- (750)"},
            {"tipo": "modo", "ruta": "secreto.txt", "igual": 0o600,
             "texto": "secreto.txt es rw------- (600)"},
            {"tipo": "modo", "ruta": "publico.txt", "igual": 0o644,
             "texto": "publico.txt es rw-r--r-- (644)"},
        ],
        "pistas": [
            "Calcula bolsillo a bolsillo: rwx r-x --- → 7 5 0. `chmod 750 tesoro`. "
            "Comprueba con `ls -ld tesoro`.",
            "«Solo tú lees y escribes»: rw- --- --- → 6 0 0. «Todos leen, solo tú escribes»: "
            "rw- r-- r-- → 6 4 4.",
            "`chmod 750 tesoro` → `chmod 600 secreto.txt` → `chmod 644 publico.txt` → "
            "`chmod u+x ritual.sh` → `./ritual.sh` → `chmod 700 boveda` → `cd boveda`.",
        ],
        "exito": (
            "Los números de las paredes se ordenan solos: 750, 600, 644. Ya piensas en octal, como "
            "los antiguos (y como cualquier administrador de sistemas)."
        ),
    },
    # --------------------------------------------------------------- BÓVEDA
    {
        "id": "boveda",
        "padre": "numeros",
        "carpeta": "boveda",
        "titulo": "La Bóveda de los Antiguos",
        "mapa": "BÓVEDA",
        "pos": (1, 1),
        "arte": "boveda",
        "descripcion": (
            "Una bóveda enorme. En el centro, tres ofrendas: ofrenda_1.txt, ofrenda_2.txt y "
            "ofrenda_3.txt. Al fondo, un templo (templo/) con dos alas y varios pergaminos dentro.\n\n"
            "Dos encargos. Primero: las ofrendas no deben poder leerlas los «otros» (o). Con los "
            "comodines del nivel 1 lo haces de un golpe: `chmod o-r ofrenda_*.txt`. Segundo: todo "
            "lo que hay en el templo debe poder leerlo el grupo (g+r), y todas sus carpetas deben "
            "poder atravesarse (g+x). `chmod -R` aplica el cambio a la carpeta y a TODO lo que hay "
            "dentro. Y la X mayúscula (`chmod -R g+rX templo`) pone la x solo a las carpetas y a lo "
            "que ya era ejecutable, no a los ficheros normales."
        ),
        "objetivo": (
            "Quita la lectura de otros a las tres ofrendas y da al grupo lectura en todo el templo "
            "y paso por sus carpetas. Luego, el ritual."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA BÓVEDA\n"
                "\n"
                "    chmod o-r ofrenda_*.txt      a las tres a la vez (comodín)\n"
                "    ls -l ofrenda_*              comprueba: rw-r----- (o sin r)\n"
                "\n"
                "    chmod -R g+rX templo         -R = recursivo; X = x solo en carpetas\n"
                "    ls -lR templo                comprueba todo el árbol\n"
            ),
            "ofrenda_1.txt": "Pan.\n",
            "ofrenda_2.txt": "Sal.\n",
            "ofrenda_3.txt": "Vino.\n",
            "ritual.sh": _ritual("La Bóveda de los Antiguos"),
        },
        "carpetas": {
            "templo": {
                "norte": {"salmo_1.txt": "Primer salmo.\n", "salmo_2.txt": "Segundo salmo.\n"},
                "sur": {"himno.txt": "Un himno.\n", "plegaria.txt": "Una plegaria.\n"},
                "leeme.txt": "El templo tiene dos alas: norte y sur.\n",
            },
        },
        "permisos": {
            "ofrenda_1.txt": 0o644, "ofrenda_2.txt": 0o644, "ofrenda_3.txt": 0o644,
            "templo": 0o700, "templo/norte": 0o700, "templo/sur": 0o700,
            "templo/leeme.txt": 0o600, "templo/norte/salmo_1.txt": 0o600,
            "templo/norte/salmo_2.txt": 0o600, "templo/sur/himno.txt": 0o600,
            "templo/sur/plegaria.txt": 0o600,
            "ritual.sh": 0o644, "altar": 0o000,
        },
        "condiciones": [
            {"tipo": "sello", "sala": "numeros", "texto": "Ritual de los números completado"},
            {"tipo": "modo", "ruta": ".", "patron": "ofrenda_*.txt", "sin_bits": 0o004,
             "texto": "Ninguna ofrenda es legible por otros (chmod o-r ofrenda_*.txt)"},
            {"tipo": "modo", "ruta": "templo", "recursivo": True, "que": "ficheros", "bits": 0o040,
             "texto": "Todos los ficheros del templo son legibles por el grupo (g+r)"},
            {"tipo": "modo", "ruta": "templo", "recursivo": True, "que": "carpetas", "bits": 0o050,
             "texto": "Todas las carpetas del templo se pueden listar y atravesar por el grupo (g+rx)"},
        ],
        "pistas": [
            "`chmod o-r ofrenda_*.txt` quita (−) la lectura (r) a los otros (o) en los tres ficheros "
            "de golpe. Comprueba con `ls -l ofrenda_*`.",
            "`chmod -R g+rX templo`: -R baja por todas las carpetas; g+r da lectura al grupo; X pone "
            "la x solo en las carpetas. `ls -lR templo` lo enseña todo.",
            "`chmod o-r ofrenda_*.txt` → `chmod -R g+rX templo` → `chmod u+x ritual.sh` → "
            "`./ritual.sh` → `chmod 700 altar` → `cd altar`.",
        ],
        "exito": (
            "Las ofrendas se consumen en una llama sin humo. Ya dominas el chmod en masa: comodines "
            "y -R. Con eso se administra una carpeta de departamento entera en un solo comando."
        ),
    },
    # ---------------------------------------------------------------- ALTAR
    {
        "id": "altar",
        "padre": "boveda",
        "carpeta": "altar",
        "titulo": "El Altar",
        "mapa": "ALTAR",
        "pos": (0, 1),
        "arte": "altar",
        "arte_victoria": "catacumbas_victoria",
        "descripcion": (
            "El altar final. Sobre la piedra, un único fichero: guardian.sh, el programa que rompe "
            "el último sello. Está bloqueado del todo: ----------.\n\n"
            "Antes de ejecutar un programa que no conoces, LÉELO. Es la regla de oro de cualquier "
            "administrador: un script puede hacer cualquier cosa que tú puedas hacer, incluido "
            "borrar tu carpeta personal. Dale permiso de lectura, míralo con cat, y solo si te "
            "fías, dale permiso de ejecución y lánzalo."
        ),
        "objetivo": "Lee guardian.sh, hazlo ejecutable y ejecútalo con ./guardian.sh",
        "ficheros": {
            "guardian.sh": (
                "#!/bin/bash\n"
                "# EL GUARDIÁN DEL ALTAR\n"
                "#\n"
                "# Este programa NO borra nada ni toca nada fuera de las catacumbas.\n"
                "# Comprueba que tienes los cinco sellos y rompe el último sello.\n"
                "#\n"
                "# Bien hecho por leerlo antes de ejecutarlo: nunca lances un script sin\n"
                "# saber qué hace. Un script puede hacer todo lo que tú puedes hacer.\n"
                "#\n"
                "#     chmod u+x guardian.sh\n"
                "#     ./guardian.sh\n"
                "\n"
                "if command -v mazmorra >/dev/null 2>&1; then\n"
                "    exec mazmorra ritual \"$0\"\n"
                "else\n"
                "    exec \"$HOME/.mazmorra/bin/mazmorra\" ritual \"$0\"\n"
                "fi\n"
            ),
        },
        "permisos": {"guardian.sh": 0o000},
        "condiciones": [
            {"tipo": "sello", "sala": "vestibulo", "texto": "Sello del vestíbulo"},
            {"tipo": "sello", "sala": "galeria", "texto": "Sello de la galería"},
            {"tipo": "sello", "sala": "escriba", "texto": "Sello del escriba"},
            {"tipo": "sello", "sala": "numeros", "texto": "Sello de los números"},
            {"tipo": "sello", "sala": "boveda", "texto": "Sello de la bóveda"},
            {"tipo": "modo", "ruta": "guardian.sh", "bits": 0o500,
             "texto": "guardian.sh se puede leer y ejecutar (chmod u+rx guardian.sh)"},
        ],
        "pistas": [
            "`ls -l` → ---------- guardian.sh. Primero léelo: `chmod u+r guardian.sh` y "
            "`cat guardian.sh`.",
            "Si te fías de lo que has leído: `chmod u+x guardian.sh`.",
            "`chmod u+rx guardian.sh` → `cat guardian.sh` → `./guardian.sh`.",
        ],
        "victoria": True,
        "exito": (
            "El último sello se rompe con un chasquido seco. Las catacumbas se iluminan: has "
            "aprendido a leer permisos, a darlos y quitarlos letra a letra y en octal, a distinguir "
            "lo que significan en un fichero y en una carpeta, a cambiarlos en masa y a ejecutar "
            "programas con cabeza."
        ),
    },
]


NIVEL = {
    "numero": 2,
    "nombre": "Las Catacumbas de los Permisos",
    "rotulo": "CATACUMBAS",
    "raiz": "catacumbas",
    "inventario": None,
    "tipo": "permisos",
    "certificado": "certificado_nivel2.txt",
    "salas": SALAS,
    "intro": (
        "Bajo la mazmorra hay unas catacumbas donde los pergaminos no sirven de nada. Allí la "
        "magia son los PERMISOS: cada fichero y cada carpeta tiene un dueño y unas llaves que "
        "dicen quién puede leer (r), escribir (w) y ejecutar o entrar (x). Tú eres el dueño de "
        "todo lo que hay ahí abajo, así que tú decides: chmod es tu nuevo hechizo. Cada sala se "
        "cierra con un ritual, un programa que hay que hacer ejecutable y lanzar. Y las puertas "
        "las abres tú."
    ),
    "comandos": [
        ("mirar", "describe la sala y qué te falta"),
        ("mapa", "mapa de las catacumbas"),
        ("inventario", "sellos conseguidos"),
        ("pista", "una ayuda; cada vez más concreta"),
        ("estado", "tu progreso"),
        ("ls -l", "(de Linux) ver los permisos"),
        ("chmod", "(de Linux) cambiar los permisos"),
    ],
    "primer_paso": "cd ~/catacumbas/vestibulo",
    "siguiente": (
        "Has completado los dos niveles. Entrega tus certificados en Moodle: "
        "~/mazmorra/certificado_nivel1.txt y ~/catacumbas/certificado_nivel2.txt"
    ),
}
