"""Nivel 1 · La Mazmorra de los Comandos Perdidos.

Aquí está TODO el contenido del nivel: salas, textos, objetos, puzles y pistas.
El motor (motor.py) no sabe nada de la historia: solo interpreta estas tablas.
Para cambiar una pista, una palabra de poder o añadir una sala, se edita este
fichero y nada más.

Convenciones de rutas en las condiciones:
  "fichero.txt"        → relativo a la carpeta de la sala que enseña el hechizo
  "@inventario/x.txt"  → relativo a la raíz de la mazmorra (~/mazmorra)
"""

# ---------------------------------------------------------------------------
# Contenido generado (libros, tomo, diario)
# ---------------------------------------------------------------------------

_FRASES_LIBROS = [
    "Los magos antiguos guardaban sus hechizos en pergaminos, uno por fichero.",
    "Una carpeta vacía no pesa nada, pero puede contener un mundo.",
    "El que no sabe dónde está, que pregunte: pwd.",
    "Dos puntos seguidos (..) son siempre la sala anterior.",
    "El asterisco es la runa más poderosa: significa «lo que sea».",
    "No leas un tomo entero si solo necesitas su última línea.",
    "Copiar (cp) deja el original; mover (mv) se lo lleva.",
    "Un solo > borra y escribe. Dos >> añaden al final.",
    "Lo que empieza por punto está oculto a los ojos perezosos.",
    "rm no tiene vuelta atrás. Piensa antes de borrar.",
    "Tab completa los nombres. Los sabios no teclean de más.",
    "La flecha arriba recuerda lo que escribiste antes.",
    "Ctrl+C detiene lo que se haya quedado colgado.",
    "man es el manual; q sirve para salir de él.",
    "Las mayúsculas y minúsculas NO son lo mismo: Luz.txt no es luz.txt.",
    "Los espacios en los nombres traen problemas; usa guiones_bajos.",
    "Una ruta que empieza por / o por ~ es absoluta: vale desde cualquier sala.",
    "Una ruta que no empieza por / ni ~ es relativa: cuenta desde donde estás.",
    "ls -l enseña quién puede leer, escribir y ejecutar cada cosa.",
    "mkdir -p crea de golpe todas las carpetas de una ruta.",
    "touch crea ficheros vacíos, o actualiza la fecha de los que existen.",
    "less lee página a página; head y tail, solo el principio o el final.",
    "wc -l cuenta líneas. Útil antes de leer un tomo infinito.",
    "Este libro no dice nada útil. Como muchos.",
]


def _libros():
    return {
        f"libro_{i:02d}.txt": f"Libro {i:02d} de la Biblioteca de la Mazmorra\n\n{frase}\n"
        for i, frase in enumerate(_FRASES_LIBROS, start=1)
    }


_PALABRAS_TOMO = (
    "umbra silva ferrum aqua terra ventus nox lux ignis glacies petra arbor "
    "murus porta clavis turris rex regina draco corvus lupus serpens hortus "
    "flumen mons vallis nubes stella luna sol tempus fatum somnus"
).split()


def _tomo_infinito(lineas=300):
    filas = ["TOMO INFINITO · No intentes leerlo entero. Nadie lo ha conseguido."]
    for i in range(2, lineas):
        # Pseudolatín determinista: siempre sale igual, sin azar.
        a = _PALABRAS_TOMO[(i * 7) % len(_PALABRAS_TOMO)]
        b = _PALABRAS_TOMO[(i * 11 + 3) % len(_PALABRAS_TOMO)]
        d = _PALABRAS_TOMO[(i * 13 + 5) % len(_PALABRAS_TOMO)]
        filas.append(f"{i:03d}  {a} {b} {d} {a}{b} {d}{a}...")
    filas.append("La palabra de poder del SILENCIO es: SILENTIUM")
    return "\n".join(filas) + "\n"


_DIARIO = """Diario del Guardián del Abismo
Día 1. Me han puesto a vigilar una puerta helada. Qué aburrimiento.
Día 2. Mi nombre verdadero, el que me hace dormir, es SOMNUS. No se lo cuentes a nadie.
Día 3. Ha pasado un aprendiz. Se ha ido llorando por el cd ..
Día 4. He probado a leer el tomo infinito. He llegado a la línea 40.
Día 5. Nadie cruza el abismo sin puente. Nadie cruza el hielo sin fuego.
Día 6. He soñado con un terminal que hablaba. Decía «command not found».
Día 7. Otro aprendiz. Ha borrado su mochila con rm -r. Pobre.
Día 8. He aprendido que head -n 3 muestra solo 3 líneas. Qué comodidad.
Día 9. Mañana me toca limpiar la cripta. Hay telarañas hasta en las telarañas.
Día 10. Sigo aquí. Sigo vigilando. Sigo sin saber para qué.
Día 11. Si lees esto, es que has llegado más lejos que la mayoría.
"""


# ---------------------------------------------------------------------------
# Las salas
# ---------------------------------------------------------------------------

SALAS = [
    # ------------------------------------------------------------- ENTRADA
    {
        "id": "entrada",
        "padre": None,
        "carpeta": "entrada",
        "titulo": "La Entrada de la Mazmorra",
        "mapa": "ENTRADA",
        "pos": (2, 2),
        "arte": "entrada",
        "descripcion": (
            "Te despiertas en una sala oscura y húmeda. Huele a piedra vieja. Apenas ves nada, "
            "pero notas un pergamino bajo tus pies y una pesada puerta al norte: gran_sala/. "
            "Está sellada, y en el marco hay grabada una sola palabra: LUZ.\n\n"
            "Cada carpeta de esta mazmorra es una sala y cada fichero, un objeto. Tu terminal es "
            "tu grimorio: con él miras (ls), lees (cat) y coges cosas (cp). Los hechizos que "
            "aprendas irán a tu mochila, que está siempre en ~/mazmorra/inventario."
        ),
        "objetivo": "Guarda el pergamino luz.txt en la mochila y lanza el hechizo LUZ.",
        "ficheros": {
            "inscripcion.txt": (
                "Bienvenido, aprendiz.\n"
                "\n"
                "Este terminal es tu grimorio. Cada carpeta es una sala; cada fichero, un objeto.\n"
                "\n"
                "En el suelo hay un pergamino: luz.txt. Léelo con:\n"
                "    cat luz.txt\n"
                "\n"
                "Para llevarlo contigo, cópialo a tu mochila, que es la carpeta ~/mazmorra/inventario:\n"
                "    cp luz.txt ~/mazmorra/inventario/\n"
                "\n"
                "Y después lanza el hechizo:\n"
                "    lanzar luz\n"
                "\n"
                "Si te pierdes, escribe: pista. Si quieres ver el mapa: mapa.\n"
            ),
            "luz.txt": (
                "~ Pergamino de la Luz ~\n"
                "\n"
                "Palabra de poder: LUMEN\n"
                "\n"
                "(Un hechizo es un fichero en tu mochila con su palabra de poder dentro.)\n"
            ),
        },
        "puertas": {"gran_sala": ["luz"]},
        "hechizo": "luz",
        "palabra": "LUMEN",
        "pistas": [
            "Mira qué hay en el suelo con `ls`. Lee las cosas con `cat nombre_del_fichero`. "
            "Empieza por `cat inscripcion.txt`.",
            "La mochila es la carpeta ~/mazmorra/inventario. Para copiar un fichero a una carpeta: "
            "`cp fichero carpeta/`. La ~ significa «mi carpeta personal», así que esa ruta vale "
            "desde cualquier sala.",
            "Escribe exactamente:  `cp luz.txt ~/mazmorra/inventario/`  y después  `lanzar luz`.",
        ],
        "exito": (
            "¡LUMEN! Las antorchas de la pared se encienden una tras otra. Ahora ves la sala entera: "
            "piedra, musgo... y la puerta del norte, que cruje y se abre."
        ),
        "tras_abrir": {"gran_sala": "Entra en la Gran Sala con:  cd gran_sala"},
    },
    # ----------------------------------------------------------- GRAN SALA
    {
        "id": "gran_sala",
        "padre": "entrada",
        "carpeta": "gran_sala",
        "titulo": "La Gran Sala",
        "mapa": "GRAN SALA",
        "pos": (2, 1),
        "arte": "gran_sala",
        "descripcion": (
            "Una sala enorme, con columnas y cuatro puertas. Al OESTE, la biblioteca/ (abierta). "
            "Al ESTE, la cripta/, sellada con la palabra APERTURA. Al NORTE, la torre/, sellada con "
            "la palabra MAESTRO. Al sur, la entrada por la que has venido.\n\n"
            "Esta sala es el centro de la mazmorra: volverás aquí muchas veces. Para subir a la sala "
            "anterior se usa `cd ..` (dos puntos = la carpeta de arriba). Para saber dónde estás, "
            "`pwd`. Y desde cualquier sitio puedes volver aquí con la ruta completa:  "
            "cd ~/mazmorra/entrada/gran_sala"
        ),
        "objetivo": (
            "Explora las salas y reúne los siete hechizos. Cuando los tengas todos, une sus pergaminos "
            "en uno solo (maestro.txt) para abrir la torre."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA GRAN SALA\n"
                "\n"
                "Una ruta es como una dirección postal:\n"
                "    ~/mazmorra/entrada/gran_sala\n"
                "~ es tu casa; cada / es una puerta que atraviesas.\n"
                "\n"
                "  cd biblioteca      entra en la biblioteca (ruta relativa: desde aquí)\n"
                "  cd ..              vuelve a la sala anterior\n"
                "  cd ~/mazmorra/entrada/gran_sala   vuelve aquí desde donde sea (ruta absoluta)\n"
                "  pwd                te dice dónde estás\n"
                "\n"
                "Puertas:\n"
                "  biblioteca/   abierta\n"
                "  cripta/       sellada: APERTURA\n"
                "  torre/        sellada: MAESTRO — la unión de TODOS los hechizos aprendidos.\n"
                "                Cuando tengas los siete, crea en la mochila un pergamino maestro.txt\n"
                "                que contenga todas las palabras de poder. Pista: cat une ficheros.\n"
            ),
        },
        "puertas": {"biblioteca": [], "cripta": ["apertura"], "torre": ["maestro"]},
        "hechizo": "maestro",
        "palabras": ["LUMEN", "APERIRE", "SILENTIUM", "PONS", "SOMNUS", "PURGO", "IGNIS"],
        "pistas": [
            "Empieza por la biblioteca: `cd biblioteca`. Para volver aquí, `cd ..`. El `mapa` te "
            "enseña qué salas hay y cuáles tienes ya.",
            "Para la torre necesitas los siete hechizos: luz, apertura, silencio, puente, dormir, "
            "purificar y fuego. `estado` te dice cuáles tienes y cuáles faltan.",
            "Cuando tengas los siete: `cd ~/mazmorra/inventario`, luego `cat *.txt > maestro.txt` "
            "(une todos los pergaminos en uno), vuelve a la Gran Sala y `lanzar maestro`.",
        ],
        "exito": (
            "Las siete palabras de poder resuenan a la vez. El suelo tiembla, las columnas brillan "
            "y la puerta de la torre, que nadie había abierto en siglos, se desliza hacia un lado."
        ),
        "tras_abrir": {
            "biblioteca": "Entra con:  cd biblioteca",
            "cripta": "La cripta está abierta. Entra con:  cd cripta",
            "torre": "Sube a la torre con:  cd torre",
        },
    },
    # ---------------------------------------------------------- BIBLIOTECA
    {
        "id": "biblioteca",
        "padre": "gran_sala",
        "carpeta": "biblioteca",
        "titulo": "La Biblioteca",
        "mapa": "BIBLIOTECA",
        "pos": (1, 1),
        "arte": "biblioteca",
        "descripcion": (
            "Estanterías hasta el techo, llenas de libros polvorientos. Entre tantos volúmenes, "
            "tres runas de piedra: runa_a.txt, runa_b.txt y runa_c.txt. Cada una tiene grabada una "
            "sílaba; juntas, en orden (a, b, c), forman la palabra que ABRE puertas.\n\n"
            "Consejo del bibliotecario: los comodines ahorran tiempo. `ls runa_*` muestra solo lo que "
            "empieza por runa_ (el * significa «lo que sea»). Y `cat` puede leer varios ficheros "
            "seguidos: `cat uno dos tres`. Si al final añades `> nuevo.txt`, en vez de mostrarse en "
            "pantalla, el resultado se guarda en ese fichero."
        ),
        "objetivo": (
            "Crea en la mochila el pergamino apertura.txt uniendo las tres runas en orden."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA BIBLIOTECA\n"
                "\n"
                "Tres runas, tres sílabas, una palabra. El orden es a, b, c.\n"
                "\n"
                "  ls runa_*                              solo las runas\n"
                "  cat runa_a.txt runa_b.txt runa_c.txt   las lee seguidas\n"
                "  cat ... > fichero                      guarda en un fichero lo que saldría por pantalla\n"
                "\n"
                "El pergamino tiene que llamarse apertura.txt y estar en la mochila.\n"
            ),
            "runa_a.txt": "APE\n",
            "runa_b.txt": "RI\n",
            "runa_c.txt": "RE\n",
            **_libros(),
        },
        "puertas": {"archivo": ["apertura"]},
        "hechizo": "apertura",
        "palabra": "APERIRE",
        "pistas": [
            "`ls runa_*` te enseña solo las runas. Léelas con `cat runa_a.txt`, etc.",
            "`cat runa_a.txt runa_b.txt runa_c.txt` las muestra seguidas. Si añades `> fichero` al "
            "final, el resultado se guarda en el fichero en vez de salir por pantalla. El fichero "
            "tiene que estar en la mochila: ~/mazmorra/inventario/apertura.txt",
            "Escribe:  `cat runa_*.txt > ~/mazmorra/inventario/apertura.txt`  y luego  "
            "`lanzar apertura`.",
        ],
        "exito": (
            "¡APERIRE! Una estantería entera gira sobre sí misma y deja ver una puerta escondida: "
            "archivo/. Este hechizo abre puertas... también la de la cripta, en la Gran Sala."
        ),
        "tras_abrir": {"archivo": "Entra en el archivo con:  cd archivo"},
    },
    # ------------------------------------------------------------- ARCHIVO
    {
        "id": "archivo",
        "padre": "biblioteca",
        "carpeta": "archivo",
        "titulo": "El Archivo Secreto",
        "mapa": "ARCHIVO",
        "pos": (0, 1),
        "arte": "archivo",
        "descripcion": (
            "Archivadores de madera, polvo y silencio. La sala parece vacía... pero los archiveros "
            "eran gente desconfiada y escondían lo importante.\n\n"
            "En Linux, todo lo que empieza por punto (.) está OCULTO: `ls` no lo muestra, salvo que "
            "se lo pidas con `ls -a`. Aquí hay un tomo escondido. Es enorme: no intentes leerlo "
            "entero. `wc -l fichero` cuenta sus líneas, `head -n 5 fichero` muestra las 5 primeras y "
            "`tail -n 1 fichero`, solo la última. La palabra de poder del silencio está al final."
        ),
        "objetivo": (
            "Encuentra el tomo oculto, lee su última línea y escribe el pergamino silencio.txt en "
            "la mochila con la palabra de poder."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "EL ARCHIVO\n"
                "\n"
                "¿Vacío? Los archiveros escondían lo importante. Lo oculto empieza por punto.\n"
                "\n"
                "  ls -a              muestra también lo oculto\n"
                "  wc -l fichero      cuenta las líneas\n"
                "  tail -n 1 fichero  enseña solo la última línea\n"
                "  head -n 5 fichero  enseña las 5 primeras\n"
                "  less fichero       lo lee página a página (q para salir)\n"
                "\n"
                "Para escribir un pergamino nuevo con una palabra dentro:\n"
                "  echo PALABRA > ~/mazmorra/inventario/nombre.txt\n"
            ),
            ".tomo_infinito.txt": _tomo_infinito(),
        },
        "puertas": {"abismo": ["silencio"]},
        "hechizo": "silencio",
        "palabra": "SILENTIUM",
        "pistas": [
            "`ls -a` muestra también los ficheros ocultos (los que empiezan por punto).",
            "No leas el tomo entero: `wc -l .tomo_infinito.txt` te dice cuántas líneas tiene y "
            "`tail -n 1 .tomo_infinito.txt` te enseña solo la última. `echo PALABRA > fichero` "
            "escribe esa palabra dentro de un fichero nuevo.",
            "Escribe:  `tail -n 1 .tomo_infinito.txt`  →  "
            "`echo SILENTIUM > ~/mazmorra/inventario/silencio.txt`  →  `lanzar silencio`.",
        ],
        "exito": (
            "¡SILENTIUM! El polvo deja de flotar. Todo se queda quieto. Y en ese silencio oyes un "
            "chasquido bajo tus pies: una trampilla. Unas escaleras bajan hacia el abismo/."
        ),
        "tras_abrir": {"abismo": "Baja al abismo con:  cd abismo"},
    },
    # -------------------------------------------------------------- ABISMO
    {
        "id": "abismo",
        "padre": "archivo",
        "carpeta": "abismo",
        "titulo": "El Abismo",
        "mapa": "ABISMO",
        "pos": (0, 2),
        "arte": "abismo",
        "descripcion": (
            "Un tajo negro te separa de la puerta de la guarida/, al otro lado. No hay puente. "
            "Tendrás que construirlo: en Linux, construir es crear. `mkdir nombre` crea una carpeta "
            "y `touch nombre` crea un fichero vacío (o varios: `touch a b c`).\n\n"
            "Necesitas una carpeta puente con al menos tres tablones dentro: puente/tablon_1.txt, "
            "puente/tablon_2.txt y puente/tablon_3.txt. Y para cruzar, la palabra de poder del "
            "puente, que los enanos grabaron en la roca: PONS. Escríbela en un pergamino "
            "puente.txt de la mochila."
        ),
        "objetivo": (
            "Construye puente/ con tres tablones dentro y escribe el pergamino puente.txt (PONS)."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "EL ABISMO\n"
                "\n"
                "Grabado en la roca por los enanos:  P O N S\n"
                "\n"
                "  mkdir puente                          crea la carpeta\n"
                "  touch puente/tablon_1.txt             crea un fichero vacío dentro (ruta relativa)\n"
                "  touch puente/tablon_2.txt puente/tablon_3.txt   varios de golpe\n"
                "  ls puente                             comprueba\n"
                "  echo PONS > ~/mazmorra/inventario/puente.txt\n"
                "\n"
                "Al otro lado, la puerta de la guarida está cubierta de hielo. Hará falta FUEGO.\n"
            ),
        },
        "puertas": {"guarida": ["puente", "fuego"]},
        "hechizo": "puente",
        "palabra": "PONS",
        "condiciones": [
            {"tipo": "existe", "ruta": "puente", "dir": True,
             "texto": "La carpeta puente/ existe (mkdir puente)"},
            {"tipo": "cuenta", "ruta": "puente", "patron": "*tablon*", "minimo": 3,
             "texto": "Al menos tres tablones dentro de puente/ (touch puente/tablon_1.txt ...)"},
        ],
        "pistas": [
            "`mkdir puente` crea la carpeta. Los tablones son ficheros vacíos dentro de ella: "
            "`touch puente/tablon_1.txt` (la ruta puente/... es relativa: cuenta desde aquí).",
            "`touch` acepta varios nombres a la vez: "
            "`touch puente/tablon_1.txt puente/tablon_2.txt puente/tablon_3.txt`. "
            "Comprueba con `ls puente`. Luego escribe la palabra PONS en un pergamino de la mochila.",
            "`mkdir puente` → `touch puente/tablon_1.txt puente/tablon_2.txt puente/tablon_3.txt` → "
            "`echo PONS > ~/mazmorra/inventario/puente.txt` → `lanzar puente`.",
        ],
        "exito": (
            "¡PONS! Los tablones se unen solos y el puente se tiende sobre el vacío. Al otro lado, "
            "la puerta de la guarida está cubierta de una capa de hielo azul."
        ),
        "tras_abrir": {"guarida": "El hielo se derrite. Cruza el puente con:  cd guarida"},
    },
    # ------------------------------------------------------------- GUARIDA
    {
        "id": "guarida",
        "padre": "abismo",
        "carpeta": "guarida",
        "titulo": "La Guarida del Guardián",
        "mapa": "GUARIDA",
        "pos": (0, 3),
        "arte": "guarida",
        "descripcion": (
            "Un guardián enorme ronca sobre un cofre. A su lado, su diario: diario.txt. Es largo, "
            "y pasar páginas podría despertarlo. `head -n 3 diario.txt` muestra solo las tres "
            "primeras líneas.\n\n"
            "Cuentan que el nombre verdadero del guardián, escrito en su diario, es la palabra que "
            "lo dormirá para siempre. Escríbela en un pergamino dormir.txt de la mochila."
        ),
        "objetivo": (
            "Descubre el nombre verdadero del guardián (línea 3 del diario) y escribe el pergamino "
            "dormir.txt."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA GUARIDA\n"
                "\n"
                "No lo despiertes. Su nombre verdadero está en la tercera línea de su diario.\n"
                "\n"
                "  head -n 3 diario.txt    las tres primeras líneas\n"
                "  echo NOMBRE > ~/mazmorra/inventario/dormir.txt\n"
            ),
            "diario.txt": _DIARIO,
        },
        "puertas": {},
        "hechizo": "dormir",
        "palabra": "SOMNUS",
        "pistas": [
            "`head -n 3 diario.txt` enseña las tres primeras líneas. Su nombre está ahí, en mayúsculas.",
            "Escribe ese nombre dentro de un pergamino nuevo de la mochila: "
            "`echo NOMBRE > ~/mazmorra/inventario/dormir.txt`.",
            "`echo SOMNUS > ~/mazmorra/inventario/dormir.txt`  y luego  `lanzar dormir`.",
        ],
        "exito": (
            "¡SOMNUS! El guardián suspira, se da la vuelta y cae en un sueño del que no despertará. "
            "El camino de vuelta es largo: `cd ~/mazmorra/entrada/gran_sala` te lleva directo a la "
            "Gran Sala (o sube sala a sala con cd ..)."
        ),
    },
    # -------------------------------------------------------------- CRIPTA
    {
        "id": "cripta",
        "padre": "gran_sala",
        "carpeta": "cripta",
        "titulo": "La Cripta",
        "mapa": "CRIPTA",
        "pos": (3, 1),
        "arte": "cripta",
        "descripcion": (
            "Nichos, huesos y un olor que prefieres no describir. La puerta de la cámara/ está "
            "bloqueada por una carpeta de escombros/ (vacía) y otra de telarañas/ (llena de bichos). "
            "Aquí toca limpiar.\n\n"
            "`rm fichero` borra un fichero. `rmdir carpeta` borra una carpeta, pero solo si está "
            "VACÍA. `rm -r carpeta` borra una carpeta con todo lo que tiene dentro, sin preguntar: "
            "cuidado con lo que escribes. En el suelo hay un pergamino purificar.txt: esta vez "
            "MUÉVELO a la mochila (mv), no lo copies. Los pergaminos de cripta no soportan copias."
        ),
        "objetivo": (
            "Quita la maldición de la mochila, retira escombros/ y telarañas/, mueve purificar.txt "
            "a la mochila y lanza PURIFICAR."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA CRIPTA\n"
                "\n"
                "  rm fichero          borra un fichero\n"
                "  rmdir carpeta       borra una carpeta VACÍA\n"
                "  rm -r carpeta       borra una carpeta y todo lo de dentro (no pregunta)\n"
                "  mv fichero carpeta/ mueve el fichero a la carpeta (no deja copia)\n"
                "\n"
                "Cuidado con las maldiciones: si algo raro aparece en tu mochila, bórralo.\n"
                "  inventario          mira qué llevas\n"
            ),
            "purificar.txt": "~ Pergamino de la Purificación ~\n\nPalabra de poder: PURGO\n",
        },
        "carpetas": {
            "escombros": {},
            "telarañas": {
                "telaraña_1.txt": "pegajosa\n",
                "telaraña_2.txt": "más pegajosa\n",
                "araña.txt": "ocho patas, muy enfadada\n",
            },
        },
        "al_entrar": [
            {
                "accion": "crear",
                "ruta": "@inventario/maldicion.txt",
                "contenido": (
                    "MALDICIÓN DE LA CRIPTA\n"
                    "Mientras este fichero esté en tu mochila, ningún hechizo funcionará.\n"
                    "Bórralo:  rm ~/mazmorra/inventario/maldicion.txt\n"
                ),
                "mensaje": (
                    "¡TRAMPA! Algo frío se te ha metido en la mochila: maldicion.txt. Mientras "
                    "ese fichero esté ahí, ningún hechizo funcionará. Bórralo con rm."
                ),
            }
        ],
        "puertas": {"camara": ["purificar"]},
        "hechizo": "purificar",
        "palabra": "PURGO",
        "condiciones": [
            {"tipo": "no_existe", "ruta": "@inventario/maldicion.txt",
             "texto": "Sin maldición en la mochila (rm ~/mazmorra/inventario/maldicion.txt)"},
            {"tipo": "no_existe", "ruta": "escombros",
             "texto": "Escombros retirados (rmdir escombros)"},
            {"tipo": "no_existe", "ruta": "telarañas",
             "texto": "Telarañas retiradas (rm -r telarañas)"},
            {"tipo": "no_existe", "ruta": "purificar.txt",
             "texto": "El pergamino ya no está en el suelo: lo has movido, no copiado (mv)"},
        ],
        "pistas": [
            "Primero la maldición: `rm ~/mazmorra/inventario/maldicion.txt`. Comprueba con "
            "`inventario`.",
            "`rmdir escombros` (está vacía) y `rm -r telarañas` (tiene cosas dentro). "
            "Mira con `ls` qué va quedando.",
            "`mv purificar.txt ~/mazmorra/inventario/`  y luego  `lanzar purificar`.",
        ],
        "exito": (
            "¡PURGO! Una ráfaga de aire limpio recorre la cripta. Los huesos se quedan donde están, "
            "pero al menos ya no huele. La puerta de la cámara queda libre."
        ),
        "tras_abrir": {"camara": "Entra en la cámara con:  cd camara"},
    },
    # -------------------------------------------------------------- CÁMARA
    {
        "id": "camara",
        "padre": "cripta",
        "carpeta": "camara",
        "titulo": "La Cámara Sellada",
        "mapa": "CÁMARA",
        "pos": (4, 1),
        "arte": "camara",
        "descripcion": (
            "Sobre un altar de piedra, un pergamino medio quemado: borroso.txt. Se lee IGN... y ahí "
            "se corta. Los sabios dicen que la palabra completa del FUEGO es IGNIS.\n\n"
            "Para que funcione, el pergamino tiene que llamarse fuego.txt y estar en la mochila. "
            "`mv` sirve para mover Y para renombrar: `mv viejo.txt carpeta/nuevo.txt` hace las dos "
            "cosas a la vez. Y le falta el final: `echo IS >> fichero` AÑADE al final sin borrar lo "
            "que había. Ojo: con un solo > lo borrarías todo y solo quedaría IS."
        ),
        "objetivo": (
            "Mueve borroso.txt a la mochila con el nombre fuego.txt y complétalo con la sílaba IS."
        ),
        "ficheros": {
            "inscripcion.txt": (
                "LA CÁMARA SELLADA\n"
                "\n"
                "La palabra del fuego es IGNIS. El pergamino dice IGN. Le falta IS.\n"
                "\n"
                "  mv borroso.txt ~/mazmorra/inventario/fuego.txt   mueve y renombra a la vez\n"
                "  echo IS >> ~/mazmorra/inventario/fuego.txt       >> añade al final\n"
                "  cat ~/mazmorra/inventario/fuego.txt              comprueba\n"
                "\n"
                "Un solo > BORRA lo que había y escribe. Dos >> AÑADEN al final.\n"
            ),
            "borroso.txt": "IGN\n",
        },
        "puertas": {},
        "hechizo": "fuego",
        "palabra": "IGNIS",
        "pistas": [
            "`mv borroso.txt ~/mazmorra/inventario/fuego.txt` lo mueve a la mochila y lo renombra "
            "en un solo paso.",
            "`echo IS >> ~/mazmorra/inventario/fuego.txt` añade IS al final (dos > para añadir; uno "
            "solo borraría lo que hay). Comprueba con `cat ~/mazmorra/inventario/fuego.txt`.",
            "`mv borroso.txt ~/mazmorra/inventario/fuego.txt` → "
            "`echo IS >> ~/mazmorra/inventario/fuego.txt` → `lanzar fuego`.",
        ],
        "exito": (
            "¡IGNIS! Una llama azul te baila en la palma de la mano y no quema. Con ella podrás "
            "derretir el hielo de la guarida (abismo, tras el archivo de la biblioteca). Vuelve a la "
            "Gran Sala:  cd ../.."
        ),
    },
    # --------------------------------------------------------------- TORRE
    {
        "id": "torre",
        "padre": "gran_sala",
        "carpeta": "torre",
        "titulo": "La Torre",
        "mapa": "TORRE",
        "pos": (2, 0),
        "arte": "torre",
        "descripcion": (
            "Subes una escalera de caracol que parece no acabar nunca. Arriba, una sala redonda con "
            "ventanas a todos los lados y, en el centro, sobre un cojín de terciopelo, el Tesoro de "
            "la Mazmorra: corona.txt."
        ),
        "objetivo": "Lee el tesoro:  cat corona.txt",
        "ficheros": {
            "corona.txt": (
                "LA CORONA DEL ADMINISTRADOR\n"
                "\n"
                "Quien llega hasta aquí ya sabe moverse por un sistema de ficheros,\n"
                "crear, copiar, mover, borrar, leer y escribir. Lo que cualquier\n"
                "administrador de sistemas hace cien veces al día.\n"
                "\n"
                "Tu certificado está en ~/mazmorra/certificado_nivel1.txt\n"
                "Bajo la mazmorra hay unas catacumbas. Ahí los pergaminos no valen:\n"
                "allí la magia son los PERMISOS.      mazmorra iniciar --nivel 2\n"
            ),
        },
        "puertas": {},
        "hechizo": None,
        "victoria": True,
        "pistas": ["Ya has ganado. Lee la corona:  `cat corona.txt`"],
    },
]


NIVEL = {
    "numero": 1,
    "nombre": "La Mazmorra de los Comandos Perdidos",
    "rotulo": "MAZMORRA",
    "raiz": "mazmorra",
    "inventario": "inventario",
    "tipo": "hechizos",
    "certificado": "certificado_nivel1.txt",
    "salas": SALAS,
    "intro": (
        "Te despiertas en la entrada de una mazmorra. No recuerdas cómo has llegado. Solo tienes "
        "una cosa: tu grimorio, este terminal. Con él podrás mirar, leer, coger objetos, construir y "
        "lanzar hechizos. La mazmorra es un laberinto de salas (carpetas) y objetos (ficheros). "
        "La única forma de salir es llegar a la torre."
    ),
    "comandos": [
        ("mirar", "describe la sala en la que estás y qué te falta"),
        ("mapa", "mapa de la mazmorra y cómo llegar a cada sala"),
        ("inventario", "qué llevas en la mochila"),
        ("lanzar HECHIZO", "lanza un hechizo (necesitas su pergamino en la mochila)"),
        ("pista", "una ayuda; cada vez que la pidas, más concreta"),
        ("estado", "tu progreso"),
    ],
    "primer_paso": "cd ~/mazmorra/entrada",
    "siguiente": (
        "Bajo la mazmorra hay unas catacumbas donde los pergaminos no valen: allí la magia son "
        "los PERMISOS. Cuando quieras, baja:  `mazmorra iniciar --nivel 2`"
    ),
}
