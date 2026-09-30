"""Motor del juego.

El motor no sabe nada de la historia: lee las tablas de mundo_nivelN.py,
crea las carpetas y ficheros reales en el disco, y en cada comando (mirar,
mapa, lanzar...) inspecciona el estado REAL del sistema de ficheros para
decidir qué ha conseguido el alumno.

Nada de lo que hace el alumno pasa por aquí: usa su terminal de verdad.
"""

import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

from . import colores as C
from .arte import arte, rotulo

VERSION = "1.0"

# Cambia esta frase si quieres que los códigos de certificado de tu grupo
# sean distintos de los de otro profesor. herramientas/verificar_codigo.py
# la lee de aquí.
SECRETO = "SOM-SMR1-2026-mazmorra"

_COLOR_ARTE = {
    "entrada": "gris", "gran_sala": "blanco", "biblioteca": "amarillo",
    "archivo": "gris", "abismo": "azul+", "puente": "azul+", "guarida": "verde",
    "cripta": "magenta", "camara": "rojo+", "torre": "cian+", "victoria": "amarillo+",
    "hechizo": "magenta+", "trampa": "rojo+", "pergamino": "amarillo",
    "vestibulo": "gris", "galeria": "cian", "escriba": "amarillo", "numeros": "verde+",
    "boveda": "azul+", "altar": "magenta+", "catacumbas_victoria": "amarillo+",
}

SIMB = {
    "ok": "✓", "mal": "✗", "superada": "★", "actual": "●", "abierta": "○",
    "sellada": "▒", "flecha": "▸", "punto": "·",
}
if os.environ.get("MAZMORRA_ASCII") == "1":
    SIMB.update({"ok": "+", "mal": "x", "superada": "*", "actual": "@", "abierta": "o",
                 "sellada": "#", "flecha": ">", "punto": "-"})


# ---------------------------------------------------------------------------
# Utilidades de salida
# ---------------------------------------------------------------------------

def ancho_terminal() -> int:
    cols = shutil.get_terminal_size((80, 24)).columns
    return max(60, min(cols, 100))


_RE_CODIGO = re.compile(r"`([^`]+)`")


def formatear(texto: str) -> str:
    """Colorea los fragmentos entre `acentos graves` como comandos."""
    return _RE_CODIGO.sub(lambda m: C.cmd(m.group(1)), texto)


def parrafos(texto: str, sangria: int = 2, ancho: int | None = None,
             color: str | None = None) -> str:
    """Ajusta el texto al ancho del terminal, párrafo a párrafo.

    Los fragmentos entre acentos graves no se parten entre dos líneas y se
    pintan como comandos. `color` tiñe el resto del texto.
    """
    ancho = ancho or ancho_terminal()
    salida = []
    for p in C.sin_ansi(texto).split("\n\n"):
        p = " ".join(p.split())
        # Un espacio duro dentro de `...` evita que el ajuste parta un comando.
        p = _RE_CODIGO.sub(lambda m: "`" + m.group(1).replace(" ", " ") + "`", p)
        lineas = textwrap.wrap(p, width=ancho - sangria, break_on_hyphens=False,
                               break_long_words=False)
        for ln in lineas:
            ln = ln.replace(" ", " ")
            if color:
                trozos = _RE_CODIGO.split(ln)  # alterna texto normal / comando
                ln = "".join(C.cmd(t) if i % 2 else C.c(t, color) for i, t in enumerate(trozos))
            else:
                ln = formatear(ln)
            salida.append(" " * sangria + ln)
        salida.append("")
    return "\n".join(salida).rstrip("\n")


def pintar_arte(nombre: str) -> str:
    color = _COLOR_ARTE.get(nombre, "blanco")
    return "\n".join(C.c(l, color) for l in arte(nombre))


def caja(izquierda: str, derecha: str = "", color: str = "amarillo+") -> str:
    w = ancho_terminal()
    interior = w - 4
    izq = izquierda
    der = derecha
    hueco = interior - C.ancho(izq) - C.ancho(der)
    if hueco < 2 and der:
        # La ruta no cabe: se acorta por el medio (~/a/…/y/z).
        partes = C.sin_ansi(der).split("/")
        if len(partes) > 3:
            partes.insert(1, "…")
        # Quita componentes tras el «…» hasta que quepa (siempre deja los dos últimos).
        while len(partes) > 4 and interior - C.ancho(izq) - len("/".join(partes)) < 2:
            del partes[2]
        der = C.tenue("/".join(partes))
        hueco = interior - C.ancho(izq) - C.ancho(der)
    if hueco < 1:
        der = ""
        hueco = max(1, interior - C.ancho(izq))
    linea = f"{izq}{' ' * hueco}{der}"
    b = lambda s: C.c(s, color)
    return "\n".join([
        b("╭" + "─" * (interior + 2) + "╮"),
        b("│") + " " + C.rellenar(linea, interior) + " " + b("│"),
        b("╰" + "─" * (interior + 2) + "╯"),
    ])


def abreviar_home(ruta: Path) -> str:
    try:
        return "~/" + str(ruta.relative_to(Path.home()))
    except ValueError:
        return str(ruta)


def normalizar(texto: str) -> str:
    """Mayúsculas, sin espacios ni saltos de línea, sin acentos."""
    tabla = str.maketrans("ÁÉÍÓÚÑÜáéíóúñü", "AEIOUNUAEIOUNU")
    return "".join(texto.translate(tabla).upper().split())


def leer(ruta: Path) -> str | None:
    try:
        return ruta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def modo(ruta: Path) -> int | None:
    try:
        return stat.S_IMODE(os.lstat(ruta).st_mode)
    except OSError:
        return None


def modo_texto(ruta: Path) -> str:
    try:
        return stat.filemode(os.lstat(ruta).st_mode)
    except OSError:
        return "??????????"


# ---------------------------------------------------------------------------
# Niveles
# ---------------------------------------------------------------------------

def cargar_niveles() -> list[dict]:
    niveles = []
    from . import mundo_nivel1
    niveles.append(mundo_nivel1.NIVEL)
    try:
        from . import mundo_nivel2
        niveles.append(mundo_nivel2.NIVEL)
    except ImportError:
        pass
    return niveles


class Sala:
    def __init__(self, d: dict, juego: "Juego"):
        self.d = d
        self.juego = juego
        self.id = d["id"]
        self.padre = d.get("padre")
        self.carpeta = d["carpeta"]
        self.titulo = d["titulo"]
        self.hechizo = d.get("hechizo")
        self.puertas = d.get("puertas", {})
        self.condiciones = d.get("condiciones", [])
        self.pistas = d.get("pistas", [])
        self.victoria = d.get("victoria", False)
        self.hijos: list["Sala"] = []
        self.dir: Path = Path()  # se calcula en Juego

    def __getattr__(self, nombre):
        # Acceso cómodo al resto de claves del diccionario.
        try:
            return self.d[nombre]
        except KeyError:
            raise AttributeError(nombre)

    def get(self, clave, defecto=None):
        return self.d.get(clave, defecto)

    @property
    def palabras(self) -> list[str]:
        if "palabras" in self.d:
            return list(self.d["palabras"])
        if self.d.get("palabra"):
            return [self.d["palabra"]]
        return []

    @property
    def ruta_corta(self) -> str:
        return abreviar_home(self.dir)


class Juego:
    def __init__(self, nivel: dict):
        self.n = nivel
        self.raiz = Path.home() / nivel["raiz"]
        self.dir_juego = self.raiz / ".juego"
        self.inventario = (self.raiz / nivel["inventario"]) if nivel.get("inventario") else None
        self.salas: dict[str, Sala] = {}
        for d in nivel["salas"]:
            self.salas[d["id"]] = Sala(d, self)
        for s in self.salas.values():
            if s.padre:
                self.salas[s.padre].hijos.append(s)
        # Calcular rutas en orden (los padres antes que los hijos).
        for s in self.ordenadas():
            s.dir = (self.salas[s.padre].dir / s.carpeta) if s.padre else (self.raiz / s.carpeta)
        self._estado = None

    # ---- estado ------------------------------------------------------------
    @property
    def estado(self) -> dict:
        if self._estado is None:
            self._estado = self._cargar_estado()
        return self._estado

    def _estado_nuevo(self, nombre: str) -> dict:
        return {
            "version": VERSION, "nivel": self.n["numero"], "nombre": nombre,
            "inicio": time.time(), "fin": None, "terminado": False,
            "hechizos": [], "puertas_abiertas": [], "visitadas": [],
            "trampas": [], "sellos": [], "pistas": {},
        }

    def _cargar_estado(self) -> dict:
        f = self.dir_juego / "estado.json"
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            est = self._estado_nuevo(os.environ.get("USER", "aprendiz"))
            if self.raiz.exists():
                self._estado = est
                self.guardar()
            return est

    def guardar(self):
        self.dir_juego.mkdir(parents=True, exist_ok=True)
        (self.dir_juego / "estado.json").write_text(
            json.dumps(self.estado, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- salas ---------------------------------------------------------------
    def ordenadas(self) -> list[Sala]:
        """Salas de arriba abajo (cada padre antes que sus hijos)."""
        out, pendientes = [], [s for s in self.salas.values() if not s.padre]
        while pendientes:
            s = pendientes.pop(0)
            out.append(s)
            pendientes = s.hijos + pendientes
        return out

    def profundidad(self, s: Sala) -> int:
        n = 0
        while s.padre:
            s = self.salas[s.padre]
            n += 1
        return n

    def sala_actual(self) -> Sala | None:
        try:
            cwd = Path(os.getcwd()).resolve()
        except OSError:
            return None
        mejor = None
        for s in self.salas.values():
            d = s.dir.resolve()
            if cwd == d or d in cwd.parents:
                if mejor is None or len(d.parts) > len(mejor.dir.resolve().parts):
                    mejor = s
        return mejor

    def dentro(self) -> bool:
        try:
            cwd = Path(os.getcwd()).resolve()
        except OSError:
            return False
        r = self.raiz.resolve()
        return cwd == r or r in cwd.parents

    def sala_por_hechizo(self, nombre: str) -> Sala | None:
        for s in self.salas.values():
            if s.hechizo == nombre:
                return s
        return None

    def resolver(self, ruta: str, sala: Sala) -> Path:
        if ruta.startswith("@"):
            return self.raiz / ruta[1:]
        return sala.dir / ruta

    # ---- estado lógico de salas y puertas ------------------------------------
    def puerta_abierta(self, padre: Sala, hijo: Sala) -> bool:
        if self.n["tipo"] == "hechizos":
            req = padre.puertas.get(hijo.id, [])
            return not req or f"{padre.id}/{hijo.id}" in self.estado["puertas_abiertas"]
        m = modo(hijo.dir)
        return m is not None and bool(m & 0o100)

    def alcanzable(self, s: Sala) -> bool:
        if not s.padre:
            return True
        padre = self.salas[s.padre]
        return self.alcanzable(padre) and self.puerta_abierta(padre, s)

    def superada(self, s: Sala) -> bool:
        if s.victoria:
            return bool(self.estado["terminado"])
        if self.n["tipo"] == "hechizos":
            return bool(s.hechizo) and s.hechizo in self.estado["hechizos"]
        return s.id in self.estado["sellos"]

    def situacion(self, s: Sala, actual: Sala | None) -> str:
        if actual is not None and s.id == actual.id:
            return "actual"
        if self.superada(s):
            return "superada"
        if self.alcanzable(s):
            return "abierta"
        return "sellada"

    # ---- creación del mundo --------------------------------------------------
    def existe(self) -> bool:
        return self.raiz.is_dir()

    def crear_mundo(self, nombre: str):
        if self.raiz.exists():
            _desbloquear(self.raiz)
            shutil.rmtree(self.raiz)
        self.raiz.mkdir(parents=True)
        self.dir_juego.mkdir()
        if self.inventario:
            self.inventario.mkdir()
        self._estado = self._estado_nuevo(nombre)
        self.guardar()
        for s in self.ordenadas():
            s.dir.mkdir(parents=True, exist_ok=True)
            self._crear_contenido(s)
        self._aplicar_permisos()

    def _crear_contenido(self, s: Sala):
        for nombre, contenido in s.get("ficheros", {}).items():
            (s.dir / nombre).write_text(contenido, encoding="utf-8")
        self._crear_arbol(s.dir, s.get("carpetas", {}))

    def _crear_arbol(self, base: Path, arbol: dict):
        for nombre, contenido in arbol.items():
            p = base / nombre
            if isinstance(contenido, dict):
                p.mkdir(exist_ok=True)
                self._crear_arbol(p, contenido)
            else:
                p.write_text(contenido, encoding="utf-8")

    def _permisos_pendientes(self, solo: Sala | None = None) -> list[tuple[Path, int]]:
        lista = []
        for s in self.salas.values():
            if solo is not None and s.id != solo.id:
                continue
            for ruta, m in s.get("permisos", {}).items():
                lista.append((s.dir / ruta, m))
            if self.n["tipo"] == "hechizos":
                for hijo in s.hijos:
                    if not self.puerta_abierta(s, hijo):
                        lista.append((hijo.dir, 0o000))
        # Los más profundos primero: si cerráramos el padre antes,
        # no podríamos tocar lo de dentro.
        lista.sort(key=lambda par: len(par[0].parts), reverse=True)
        return lista

    def _aplicar_permisos(self, solo: Sala | None = None):
        for ruta, m in self._permisos_pendientes(solo):
            try:
                os.chmod(ruta, m)
            except OSError:
                pass

    def reiniciar_sala(self, s: Sala):
        _desbloquear(s.dir)
        self._crear_contenido(s)
        # Si el alumno ha borrado o renombrado una puerta, se recrea esa sala
        # y todas las que cuelgan de ella (con su contenido original).
        pendientes = list(s.hijos)
        while pendientes:
            h = pendientes.pop(0)
            if not h.dir.is_dir():
                h.dir.mkdir(parents=True)
                self._crear_contenido(h)
                self._aplicar_permisos(solo=h)
            pendientes += h.hijos
        self._aplicar_permisos(solo=s)

    def abrir_puerta(self, padre: Sala, hijo: Sala):
        clave = f"{padre.id}/{hijo.id}"
        if clave not in self.estado["puertas_abiertas"]:
            self.estado["puertas_abiertas"].append(clave)
        try:
            os.chmod(hijo.dir, 0o755)
        except OSError:
            pass
        self.guardar()

    # ---- comprobaciones ------------------------------------------------------
    def comprobar_pergamino(self, s: Sala) -> tuple[bool, str, str | None]:
        """Comprueba que el pergamino del hechizo de la sala está en la mochila y bien escrito.

        Devuelve (ok, texto de la casilla, explicación del fallo o None).
        """
        nombre = s.hechizo
        palabras = s.palabras
        if len(palabras) > 1:
            texto = f"Pergamino {nombre}.txt en la mochila con las {len(palabras)} palabras de poder"
        else:
            texto = f"Pergamino {nombre}.txt en la mochila con la palabra de poder"
        f = self.inventario / f"{nombre}.txt"
        if not f.is_file():
            # ¿Está en el suelo de la sala actual, o mal escrito en la mochila?
            actual = self.sala_actual()
            if actual and (actual.dir / f"{nombre}.txt").is_file():
                return False, texto, (
                    f"{nombre}.txt está en el suelo de esta sala, no en la mochila. "
                    f"Guárdalo con `cp {nombre}.txt ~/mazmorra/inventario/` (o mv para moverlo).")
            parecidos = [p.name for p in self.inventario.iterdir()
                         if p.is_file() and nombre in p.name.lower() and p.name != f"{nombre}.txt"]
            if parecidos:
                return False, texto, (
                    f"En la mochila hay «{parecidos[0]}», pero el pergamino tiene que llamarse "
                    f"exactamente {nombre}.txt. Renómbralo: "
                    f"`mv ~/mazmorra/inventario/{parecidos[0]} ~/mazmorra/inventario/{nombre}.txt`")
            return False, texto, (
                f"No tienes el pergamino {nombre}.txt en la mochila "
                f"({abreviar_home(self.inventario)}). Mira qué llevas con `inventario`.")
        contenido = leer(f)
        if contenido is None:
            return False, texto, f"No se puede leer {nombre}.txt (¿permisos?)."
        norm = normalizar(contenido)
        if not norm:
            return False, texto, (
                f"El pergamino {nombre}.txt está EN BLANCO. Escribe la palabra de poder dentro: "
                f"`echo PALABRA > ~/mazmorra/inventario/{nombre}.txt`")
        faltan = [p for p in palabras if p not in norm]
        if not faltan:
            return True, texto, None
        if len(palabras) == 1:
            esperada = palabras[0]
            muestra = contenido.strip().replace("\n", " ")[:40]
            if norm and esperada.startswith(norm):
                return False, texto, (
                    f"El pergamino pone «{muestra}»: le falta el final. Añade lo que falta sin "
                    f"borrar lo que hay: `echo RESTO >> ~/mazmorra/inventario/{nombre}.txt` "
                    f"(dos > para añadir).")
            if norm and esperada.endswith(norm):
                return False, texto, (
                    f"El pergamino solo pone «{muestra}»: has borrado el principio. Un solo > "
                    f"sobrescribe; para AÑADIR al final se usan dos: >>. Vuelve a escribirlo entero.")
            if sorted(norm) == sorted(esperada):
                return False, texto, (
                    f"El pergamino pone «{muestra}»: son las letras correctas pero en otro orden. "
                    f"En `cat a b c` el orden de los ficheros importa.")
            return False, texto, (
                f"El pergamino pone «{muestra}», y esa no es la palabra de poder. "
                f"Relee la inscripción de la sala: `cat inscripcion.txt`.")
        return False, texto, (
            "Al pergamino le faltan estas palabras: " + ", ".join(faltan) +
            ". Cada una está en el pergamino de su hechizo; `cat *.txt > maestro.txt` dentro de la "
            "mochila los une todos.")

    def evaluar(self, s: Sala) -> list[tuple[bool, str, str | None]]:
        """Evalúa las condiciones extra de una sala. Lista de (ok, texto, ayuda)."""
        res = []
        for c in s.condiciones:
            tipo = c["tipo"]
            texto = c.get("texto", tipo)
            ayuda = c.get("ayuda")
            if tipo == "existe":
                p = self.resolver(c["ruta"], s)
                ok = p.is_dir() if c.get("dir") else p.exists()
                if c.get("no_vacio") and ok:
                    ok = p.stat().st_size > 0
            elif tipo == "no_existe":
                ok = not self.resolver(c["ruta"], s).exists()
            elif tipo == "cuenta":
                p = self.resolver(c["ruta"], s)
                try:
                    n = sum(1 for e in p.iterdir()
                            if fnmatch.fnmatch(e.name.lower(), c["patron"].lower()))
                except OSError:
                    n = 0
                ok = n >= c.get("minimo", 1)
                if not ok and p.is_dir():
                    ayuda = ayuda or f"De momento hay {n}; hacen falta {c.get('minimo', 1)}."
            elif tipo == "modo":
                ok, ayuda = self._evaluar_modo(c, s, ayuda)
            elif tipo == "sello":
                ok = c["sala"] in self.estado["sellos"]
            elif tipo == "hechizo":
                ok = c["hechizo"] in self.estado["hechizos"]
            else:
                ok = False
            res.append((ok, texto, ayuda))
        return res

    def _evaluar_modo(self, c: dict, s: Sala, ayuda):
        base = self.resolver(c["ruta"], s)
        objetivos: list[Path] = []
        if c.get("patron"):
            # "ruta" es la carpeta donde buscar; "patron", el comodín (ofrenda_*.txt).
            objetivos = sorted(base.glob(c["patron"])) if base.is_dir() else []
        elif c.get("recursivo"):
            que = c.get("que", "todo")
            for raiz, dirs, ficheros in os.walk(base):
                r = Path(raiz)
                if que in ("carpetas", "todo"):
                    objetivos += [r / d for d in dirs]
                if que in ("ficheros", "todo"):
                    objetivos += [r / f for f in ficheros]
            if que in ("carpetas", "todo") and base.is_dir():
                objetivos.append(base)
        else:
            objetivos = [base]
        if not objetivos:
            return False, ayuda or "No encuentro nada que comprobar (¿has borrado algo? `mazmorra reiniciar sala`)."
        malos = []
        for p in objetivos:
            m = modo(p)
            if m is None:
                malos.append((p, "no existe"))
                continue
            if "igual" in c and m != c["igual"]:
                malos.append((p, f"tiene {modo_texto(p)[1:]} = {m:o}"))
            if "bits" in c and (m & c["bits"]) != c["bits"]:
                malos.append((p, f"tiene {modo_texto(p)[1:]}"))
            if "sin_bits" in c and (m & c["sin_bits"]):
                malos.append((p, f"tiene {modo_texto(p)[1:]}"))
        if malos:
            p, por = malos[0]
            extra = f" (y {len(malos) - 1} más)" if len(malos) > 1 else ""
            return False, ayuda or f"{abreviar_relativo(p, s.dir)} {por}{extra}"
        return True, None

    def checklist(self, s: Sala) -> list[tuple[bool, str, str | None]]:
        """Checklist completa de la sala: condiciones + pergamino (nivel de hechizos)."""
        items = self.evaluar(s)
        if self.n["tipo"] == "hechizos" and s.hechizo:
            if s.hechizo in self.estado["hechizos"]:
                items.append((True, f"Hechizo {s.hechizo.upper()} aprendido", None))
            else:
                items.append(self.comprobar_pergamino(s))
        return items

    def maldito(self) -> bool:
        return bool(self.inventario) and (self.inventario / "maldicion.txt").exists()

    # ---- certificado -----------------------------------------------------------
    def pistas_usadas(self) -> int:
        return sum(self.estado["pistas"].values())

    def codigo(self) -> str:
        return codigo_certificado(self.n["numero"], self.estado["nombre"], self.pistas_usadas())

    def duracion(self) -> str:
        fin = self.estado["fin"] or time.time()
        seg = int(fin - self.estado["inicio"])
        h, m = divmod(seg // 60, 60)
        return f"{h} h {m:02d} min" if h else f"{m} min"

    def escribir_certificado(self) -> Path:
        e = self.estado
        fecha = datetime.fromtimestamp(e["fin"] or time.time()).strftime("%d/%m/%Y %H:%M")
        texto = "\n".join([
            "=" * 60,
            f"  CERTIFICADO · Nivel {self.n['numero']} superado",
            f"  {self.n['nombre']}",
            "-" * 60,
            f"  Aprendiz:       {e['nombre']}",
            f"  Fecha:          {fecha}",
            f"  Tiempo de juego: {self.duracion()}",
            f"  Pistas usadas:  {self.pistas_usadas()}",
            f"  Código:         {self.codigo()}",
            "=" * 60,
            "  Entrega este fichero (o el código) en la tarea de Moodle.",
            "",
        ])
        f = self.raiz / self.n["certificado"]
        f.write_text(texto, encoding="utf-8")
        return f


def codigo_certificado(nivel: int, nombre: str, pistas: int) -> str:
    base = f"{SECRETO}|{nivel}|{' '.join(nombre.lower().split())}|{pistas}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:8].upper()


def abreviar_relativo(p: Path, base: Path) -> str:
    try:
        return str(p.relative_to(base))
    except ValueError:
        return abreviar_home(p)


def _desbloquear(ruta: Path):
    """Da permisos rwx al dueño sobre todo el árbol (de arriba abajo)."""
    try:
        m = modo(ruta)
        if m is None:
            return
        if ruta.is_dir() and not ruta.is_symlink():
            os.chmod(ruta, m | 0o700)
            for hijo in ruta.iterdir():
                _desbloquear(hijo)
        else:
            os.chmod(ruta, m | 0o600)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Localizar la mazmorra en la que está el alumno
# ---------------------------------------------------------------------------

def juego_actual() -> Juego | None:
    for nivel in cargar_niveles():
        j = Juego(nivel)
        if j.existe() and j.dentro():
            return j
    return None


def juegos_creados() -> list[Juego]:
    return [j for j in (Juego(n) for n in cargar_niveles()) if j.existe()]


def sin_mazmorra():
    creados = juegos_creados()
    if creados:
        print(C.aviso("No estás dentro de ninguna mazmorra."))
        for j in creados:
            primera = j.ordenadas()[0]
            print(f"  {SIMB['flecha']} Nivel {j.n['numero']} · {j.n['nombre']}:  "
                  f"{C.cmd('cd ' + primera.ruta_corta)}")
    else:
        print(C.aviso("Todavía no has creado ninguna mazmorra."))
        print(f"  {SIMB['flecha']} Empieza con:  {C.cmd('mazmorra iniciar')}")


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

def cmd_iniciar(args: list[str]):
    nivel_num, nombre, si = 1, None, False
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--nivel", "-n") and i + 1 < len(args):
            nivel_num = int(args[i + 1]); i += 1
        elif a.startswith("--nivel="):
            nivel_num = int(a.split("=", 1)[1])
        elif a == "--nombre" and i + 1 < len(args):
            nombre = args[i + 1]; i += 1
        elif a in ("--si", "-y"):
            si = True
        elif a.isdigit():
            nivel_num = int(a)
        i += 1
    niveles = {n["numero"]: n for n in cargar_niveles()}
    if nivel_num not in niveles:
        print(C.mal(f"No existe el nivel {nivel_num}. Niveles disponibles: "
                    + ", ".join(str(k) for k in niveles)))
        return 1
    j = Juego(niveles[nivel_num])
    interactivo = sys.stdin.isatty()
    if j.existe() and not si:
        print(C.aviso(f"Ya existe una mazmorra del nivel {nivel_num} en {abreviar_home(j.raiz)} "
                      f"(aprendiz: {j.estado['nombre']})."))
        if not interactivo:
            print("Usa  mazmorra iniciar --si  para empezar de cero.")
            return 1
        r = input("¿Empezar de cero? Se perderá el progreso. (s/N) ").strip().lower()
        if r not in ("s", "si", "sí", "y"):
            print("Nada cambia. Sigue jugando.")
            return 0
        nombre = nombre or j.estado["nombre"]
    if not nombre:
        nombre = os.environ.get("USER", "aprendiz")
        if interactivo:
            r = input(f"¿Cómo te llamas, aprendiz? [{nombre}] ").strip()
            nombre = r or nombre
    j.crear_mundo(nombre)
    print()
    for l in rotulo(j.n["rotulo"]):
        print("  " + C.c(l, "amarillo+"))
    print()
    print("  " + C.titulo(j.n["nombre"]) + C.tenue(f"   ·   nivel {j.n['numero']}"))
    print()
    print(parrafos(j.n["intro"]))
    print()
    print("  " + C.c("Comandos del grimorio:", "negrita"))
    for cmd, desc in j.n["comandos"]:
        print(f"    {C.cmd(cmd):<32} {desc}")
    print()
    print(f"  Para empezar, escribe:  {C.cmd(j.n['primer_paso'])}")
    print(C.tenue("  (La mazmorra está en " + abreviar_home(j.raiz) + ". Nombre guardado: " + nombre + ")"))
    print()
    return 0


def cmd_mirar(args: list[str]):
    auto = "--auto" in args
    j = juego_actual()
    if j is None:
        if not auto:
            sin_mazmorra()
        return 0
    s = j.sala_actual()
    if s is None:
        _mirar_fuera_de_sala(j, auto)
        return 0
    primera = s.id not in j.estado["visitadas"]
    if primera:
        j.estado["visitadas"].append(s.id)
        j.guardar()
    mensajes_trampa = _ejecutar_al_entrar(j, s)
    # En el nivel de hechizos, llegar a la sala final ya es ganar; en el de
    # permisos hay que completar el ritual final (leer y ejecutar el script).
    if s.victoria and not j.estado["terminado"] and j.n["tipo"] == "hechizos":
        _victoria(j, s)
        return 0
    compacto = auto and not primera
    print()
    marca = SIMB["superada"] + " " if j.superada(s) else ""
    print(caja(C.titulo(marca + s.titulo.upper()), C.tenue(s.ruta_corta)))
    if not compacto:
        if s.get("arte"):
            print(pintar_arte(s.arte))
            print()
        print(parrafos(s.descripcion))
        print()
    for m in mensajes_trampa:
        print(pintar_arte("trampa"))
        print(parrafos(m, sangria=2, color="rojo+"))
        print()
    print("  " + C.c("OBJETIVO", "negrita", "amarillo+"))
    print(parrafos(s.objetivo, sangria=4))
    print()
    if s.hechizo or s.condiciones:
        _imprimir_checklist(j, s)
    _imprimir_contenido(j, s, compacto)
    if compacto:
        print(C.tenue(f"  (Escribe {C.cmd('mirar')}{C.tenue(' para ver la sala entera)')}"))
    else:
        print(C.tenue("  ¿Atascado? ") + C.cmd("pista") + C.tenue("   Mapa: ") + C.cmd("mapa")
              + (C.tenue("   Mochila: ") + C.cmd("inventario") if j.inventario else ""))
    print()
    return 0


def _mirar_fuera_de_sala(j: Juego, auto: bool):
    cwd = Path(os.getcwd()).resolve()
    primera = j.ordenadas()[0]
    if j.inventario and (cwd == j.inventario.resolve() or j.inventario.resolve() in cwd.parents):
        print(C.c("  Estás en la mochila.", "negrita") + C.tenue(
            f"  Aquí guardas los pergaminos. {SIMB['flecha']} inventario los lista. "
            f"Vuelve a la mazmorra con  cd {primera.ruta_corta}"))
        return
    print(C.c(f"  Estás en la puerta de la mazmorra ({abreviar_home(j.raiz)}).", "negrita"))
    print(f"  {SIMB['flecha']} Entra con:  {C.cmd('cd ' + primera.carpeta)}")


def _ejecutar_al_entrar(j: Juego, s: Sala) -> list[str]:
    mensajes = []
    for i, acc in enumerate(s.get("al_entrar", [])):
        clave = f"{s.id}/{i}"
        if clave in j.estado["trampas"]:
            continue
        if acc["accion"] == "crear":
            p = j.resolver(acc["ruta"], s)
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(acc.get("contenido", ""), encoding="utf-8")
            except OSError:
                continue
        j.estado["trampas"].append(clave)
        j.guardar()
        if acc.get("mensaje"):
            mensajes.append(acc["mensaje"])
    return mensajes


def _imprimir_checklist(j: Juego, s: Sala):
    items = j.checklist(s)
    if not items:
        return
    print("  " + C.c("Progreso de la sala:", "negrita"))
    for ok, texto, ayuda in items:
        simb = C.ok(SIMB["ok"]) if ok else C.mal(SIMB["mal"])
        print(f"    {simb} {formatear(texto)}")
        if not ok and ayuda:
            print(parrafos(ayuda, sangria=8))
    if len(s.palabras) > 1 and s.hechizo not in j.estado["hechizos"]:
        aprendidos = [h for h in j.estado["hechizos"] if h != s.hechizo]
        print(f"    {C.tenue('Hechizos reunidos: ' + str(len(aprendidos)) + '/' + str(len(s.palabras)))}")
    print()


def _imprimir_contenido(j: Juego, s: Sala, compacto: bool):
    try:
        entradas = sorted(p for p in s.dir.iterdir() if not p.name.startswith("."))
    except OSError:
        print(C.mal("  No puedo ver el contenido de esta sala (¿permisos?)."))
        return
    hijos = {h.carpeta: h for h in s.hijos}
    permisos = j.n["tipo"] == "permisos"
    esperados = set(s.get("ficheros", {})) | set(s.get("carpetas", {})) | set(hijos) \
        | set(s.get("permitidos", []))
    print("  " + C.c("Ves:" if not compacto else "Puertas:", "negrita"))
    extranos, sueltos = [], []
    for p in entradas:
        perm = C.tenue(modo_texto(p)) + "  " if permisos else ""
        if p.name in hijos:
            h = hijos[p.name]
            if j.superada(h):
                est = C.ok(SIMB["superada"] + " sala superada")
            elif j.puerta_abierta(s, h):
                est = C.c(SIMB["abierta"] + " puerta abierta", "verde")
            elif permisos:
                est = C.tenue(SIMB["sellada"] + " cerrada: sin permiso para entrar (x)")
            else:
                req = s.puertas.get(h.id, [])
                est = C.tenue(SIMB["sellada"] + " sellada · hechizo: ") + C.magia(
                    " + ".join(r.upper() for r in req))
            print(f"    {perm}{C.carpeta(p.name + '/'):<32} {est}")
            continue
        if compacto:
            continue
        if p.is_dir():
            nota = ""
            if permisos:
                m = modo(p) or 0
                if not m & 0o100:
                    nota = C.tenue("no puedes entrar (falta x)")
                elif not m & 0o200:
                    nota = C.tenue("no puedes crear ni borrar dentro (falta w)")
                elif not m & 0o400:
                    nota = C.tenue("no puedes listar (falta r)")
            print(f"    {perm}{C.carpeta(p.name + '/'):<32} {nota}")
        else:
            nota = ""
            if p.name == "inscripcion.txt":
                nota = C.tenue("léela: ") + C.cmd("cat inscripcion.txt")
            if permisos:
                m = modo(p) or 0
                if not m & 0o400:
                    nota = C.tenue("no puedes leerlo (falta r)")
                elif p.suffix == ".sh" and not m & 0o100:
                    nota = C.tenue("no se puede ejecutar (falta x)")
                elif p.suffix == ".sh":
                    nota = C.tenue("ejecutable: ") + C.cmd("./" + p.name)
            if not nota and not permisos:
                sueltos.append(p.name)   # se imprimen en columnas al final
            else:
                print(f"    {perm}{C.fichero(p.name):<32} {nota}")
        if p.name not in esperados:
            extranos.append(p.name)
    if sueltos:
        _imprimir_columnas(sueltos)
    if not entradas:
        print(C.tenue("    (nada a la vista... o eso parece)"))
    if extranos and not compacto and j.n["tipo"] == "hechizos":
        print(parrafos(
            "Cosas que no estaban aquí al principio: " + ", ".join(extranos) + ". "
            "Si son un error (por ejemplo, un `mv` con la ruta mal escrita), puedes borrarlas con "
            "`rm`.", sangria=4))
    print()


def _imprimir_columnas(nombres: list[str], sangria: int = 4):
    """Imprime nombres en columnas, como hace ls."""
    ancho = ancho_terminal() - sangria
    col = max(len(n) for n in nombres) + 2
    por_fila = max(1, ancho // col)
    for i in range(0, len(nombres), por_fila):
        fila = nombres[i:i + por_fila]
        print(" " * sangria + "".join(C.fichero(n) + " " * (col - len(n)) for n in fila).rstrip())


def cmd_mapa(args: list[str]):
    j = juego_actual()
    if j is None:
        creados = juegos_creados()
        if not creados:
            sin_mazmorra()
            return 0
        j = creados[-1]
    actual = j.sala_actual()
    print()
    print("  " + C.titulo(j.n["nombre"].upper()) + C.tenue(f"  ·  nivel {j.n['numero']}"))
    print()
    for linea in dibujar_mapa(j, actual):
        print("  " + linea)
    print()
    print("  " + "   ".join([
        C.ok(SIMB["superada"] + " superada"), C.c(SIMB["actual"] + " estás aquí", "amarillo+"),
        C.c(SIMB["abierta"] + " abierta", "blanco"), C.tenue(SIMB["sellada"] + " sellada"),
    ]))
    print()
    print("  " + C.c("Cómo se llega (el mapa es un árbol de carpetas):", "negrita"))
    print("  " + C.carpeta(abreviar_home(j.raiz)))
    if j.inventario:
        print("  ├── " + C.carpeta(j.inventario.name + "/") + C.tenue("   la mochila"))
    raices = [s for s in j.salas.values() if not s.padre]
    for i, s in enumerate(raices):
        _imprimir_rama(j, s, "  ", i == len(raices) - 1, actual)
    print()
    return 0


def _imprimir_rama(j: Juego, s: Sala, prefijo: str, ultimo: bool, actual: Sala | None):
    sit = j.situacion(s, actual)
    color = {"superada": "verde+", "actual": "amarillo+", "abierta": "blanco", "sellada": "gris"}[sit]
    marca = SIMB[sit]
    nombre = C.c(s.carpeta + "/", color, "negrita") if sit != "sellada" else C.tenue(s.carpeta + "/")
    extra = C.c("  ← estás aquí", "amarillo+") if sit == "actual" else ""
    print(f"{prefijo}{'└── ' if ultimo else '├── '}{nombre}  {C.c(marca, color)} "
          f"{C.tenue(s.titulo)}{extra}")
    nuevo = prefijo + ("    " if ultimo else "│   ")
    for i, h in enumerate(s.hijos):
        _imprimir_rama(j, h, nuevo, i == len(s.hijos) - 1, actual)


def dibujar_mapa(j: Juego, actual: Sala | None) -> list[str]:
    """Dibuja las salas en una rejilla de cajas unidas por líneas."""
    W, H = 14, 3           # caja
    CX, CY = W + 2, H + 1  # paso de la rejilla
    salas = [s for s in j.salas.values() if s.get("pos")]
    maxc = max(s.pos[0] for s in salas)
    maxr = max(s.pos[1] for s in salas)
    filas = (maxr + 1) * CY - 1
    cols = (maxc + 1) * CX - 2
    lienzo = [[(" ", None) for _ in range(cols)] for _ in range(filas)]

    def poner(f, c, ch, estilo):
        if 0 <= f < filas and 0 <= c < cols:
            lienzo[f][c] = (ch, estilo)

    estilos = {"superada": ("verde+",), "actual": ("amarillo+", "negrita"),
               "abierta": ("blanco",), "sellada": ("gris",)}
    for s in salas:
        col, fila = s.pos
        f0, c0 = fila * CY, col * CX
        est = estilos[j.situacion(s, actual)]
        etiqueta = f"{SIMB[j.situacion(s, actual)]} {s.mapa}"
        etiqueta = C.rellenar(etiqueta, W - 2, "^")
        poner(f0, c0, "┌", est); poner(f0, c0 + W - 1, "┐", est)
        poner(f0 + 2, c0, "└", est); poner(f0 + 2, c0 + W - 1, "┘", est)
        for k in range(1, W - 1):
            poner(f0, c0 + k, "─", est); poner(f0 + 2, c0 + k, "─", est)
        poner(f0 + 1, c0, "│", est); poner(f0 + 1, c0 + W - 1, "│", est)
        for k, ch in enumerate(etiqueta):
            poner(f0 + 1, c0 + 1 + k, ch, est)
    for s in salas:
        if not s.padre:
            continue
        p = j.salas[s.padre]
        if not p.get("pos"):
            continue
        est = ("gris",) if j.situacion(s, actual) == "sellada" else ("blanco",)
        (c1, f1), (c2, f2) = p.pos, s.pos
        if f1 == f2 and abs(c1 - c2) == 1:
            izq, der = (p, s) if c1 < c2 else (s, p)
            fi = izq.pos[1] * CY + 1
            ci = izq.pos[0] * CX + W - 1
            poner(fi, ci, "├", est); poner(fi, ci + 1, "─", est); poner(fi, ci + 2, "─", est)
            poner(fi, ci + 3, "┤", est)
        elif c1 == c2 and abs(f1 - f2) == 1:
            arriba, abajo = (p, s) if f1 < f2 else (s, p)
            cc = arriba.pos[0] * CX + W // 2
            fa = arriba.pos[1] * CY + 2
            poner(fa, cc, "┬", est); poner(fa + 1, cc, "│", est); poner(fa + 2, cc, "┴", est)
    lineas = []
    for fila in lienzo:
        out, actual_est, buf = "", None, ""
        for ch, est in fila:
            if est != actual_est:
                out += C.c(buf, *actual_est) if actual_est else buf
                buf, actual_est = "", est
            buf += ch
        out += C.c(buf, *actual_est) if actual_est else buf
        lineas.append(out.rstrip())
    return lineas


def cmd_inventario(args: list[str]):
    j = juego_actual()
    if j is None:
        creados = juegos_creados()
        if not creados:
            sin_mazmorra()
            return 0
        j = creados[-1]
    print()
    if j.n["tipo"] != "hechizos" or not j.inventario:
        print("  " + C.c("Sellos conseguidos en las catacumbas:", "negrita"))
        if not j.estado["sellos"]:
            print(C.tenue("    (ninguno todavía; cada sala da un sello al completar su ritual)"))
        for sid in j.estado["sellos"]:
            print(f"    {C.ok(SIMB['superada'])} {j.salas[sid].titulo}")
        print()
        return 0
    print("  " + C.c("Tu mochila", "negrita") + C.tenue("  " + abreviar_home(j.inventario)))
    if not j.inventario.is_dir():
        print(C.mal("  ¡La mochila ha desaparecido! La vuelvo a crear vacía."))
        j.inventario.mkdir(parents=True, exist_ok=True)
    entradas = sorted(p for p in j.inventario.iterdir() if not p.name.startswith("."))
    if not entradas:
        print(C.tenue("    (vacía)"))
    for p in entradas:
        if p.is_dir():
            print(f"    {C.carpeta(p.name + '/'):<28} " + C.tenue(
                "una carpeta dentro de la mochila; los pergaminos tienen que estar sueltos"))
            continue
        if p.name == "maldicion.txt":
            print(f"    {C.mal(p.name):<28} " + C.mal("¡MALDICIÓN! Bórrala: rm ~/mazmorra/inventario/maldicion.txt"))
            continue
        nombre = p.stem.lower() if p.suffix == ".txt" else None
        s = j.sala_por_hechizo(nombre) if nombre else None
        if s is None:
            print(f"    {C.fichero(p.name):<28} " + C.tenue("no es un hechizo conocido"))
            continue
        ok, _, ayuda = j.comprobar_pergamino(s)
        if ok:
            aprendido = nombre in j.estado["hechizos"]
            est = C.ok(f"{SIMB['ok']} hechizo {nombre.upper()} " + ("aprendido" if aprendido else "listo para lanzar"))
        else:
            est = C.mal(f"{SIMB['mal']} incompleto")
        print(f"    {C.magia(p.name):<28} {est}")
        if not ok and ayuda:
            print(parrafos(ayuda, sangria=8))
    total = sum(1 for s in j.salas.values() if s.hechizo)
    print()
    print(f"  Hechizos aprendidos: {C.ok(str(len(j.estado['hechizos'])))}/{total}"
          + ("  " + C.magia(", ".join(h.upper() for h in j.estado["hechizos"])) if j.estado["hechizos"] else ""))
    print()
    return 0


def cmd_lanzar(args: list[str]):
    j = juego_actual()
    if j is None:
        sin_mazmorra()
        return 0
    if j.n["tipo"] != "hechizos":
        print()
        print(parrafos("Aquí abajo los pergaminos no sirven de nada. En las catacumbas la magia "
                       "son los PERMISOS: `chmod` es tu hechizo y `./ritual.sh` tu conjuro. "
                       "Escribe `mirar` para ver qué te pide la sala.", color="amarillo"))
        print()
        return 0
    conocidos = sorted(s.hechizo for s in j.salas.values() if s.hechizo)
    if not args:
        print()
        print("  Uso:  " + C.cmd("lanzar NOMBRE_DEL_HECHIZO"))
        if j.estado["hechizos"]:
            print("  Hechizos que ya dominas: " + C.magia(", ".join(j.estado["hechizos"])))
        print(C.tenue("  Un hechizo es un fichero NOMBRE.txt en la mochila con su palabra de poder dentro."))
        print()
        return 0
    nombre = args[0].strip().lower()
    if nombre.endswith(".txt"):
        nombre = nombre[:-4]
    s = j.sala_por_hechizo(nombre)
    print()
    if s is None:
        print(C.mal(f"  Nunca has oído hablar del hechizo «{nombre}»."))
        pista = [h for h in conocidos if h.startswith(nombre[:2])] if len(nombre) >= 2 else []
        if pista:
            print(C.tenue("  ¿Querías decir " + " o ".join(pista) + "?"))
        print(C.tenue("  Los hechizos se nombran por el pergamino: luz.txt → lanzar luz"))
        print()
        return 1
    print("  " + C.magia(f"✦ Lanzas {nombre.upper()}..."))
    if j.maldito():
        print(pintar_arte("trampa"))
        print(parrafos(
            "La maldición te ahoga la voz y el hechizo se apaga. Mientras maldicion.txt esté en tu "
            "mochila no funcionará ninguno. Bórrala:  `rm ~/mazmorra/inventario/maldicion.txt`",
            color="rojo+"))
        print()
        return 1
    ok, texto, ayuda = j.comprobar_pergamino(s)
    if not ok:
        print(f"    {C.mal(SIMB['mal'])} {texto}")
        print(parrafos(ayuda or "", sangria=6, color="amarillo"))
        print()
        return 1
    fallos = [(t, a) for ok2, t, a in j.evaluar(s) if not ok2]
    if fallos:
        print(parrafos("El pergamino es correcto, pero el hechizo chisporrotea y se apaga. "
                       "Todavía falta:", color="amarillo"))
        for t, a in fallos:
            print(f"    {C.mal(SIMB['mal'])} {formatear(t)}")
            if a:
                print(parrafos(a, sangria=8))
        print()
        return 1
    nuevo = nombre not in j.estado["hechizos"]
    if nuevo:
        j.estado["hechizos"].append(nombre)
        j.guardar()
        print(pintar_arte("hechizo"))
        total = len(conocidos)
        print("  " + C.c(f"{SIMB['superada']} Nuevo hechizo aprendido: {nombre.upper()}", "negrita", "verde+")
              + C.tenue(f"  ({len(j.estado['hechizos'])}/{total})"))
        print()
        if s.get("exito"):
            print(parrafos(s.exito))
            print()
    actual = j.sala_actual()
    abierto_algo = False
    if actual:
        for hijo in actual.hijos:
            req = actual.puertas.get(hijo.id, [])
            if nombre not in req:
                continue
            if j.puerta_abierta(actual, hijo):
                print(C.tenue(f"  La puerta {hijo.carpeta}/ ya estaba abierta."))
                abierto_algo = True
                continue
            faltan = [r for r in req if r not in j.estado["hechizos"]]
            if faltan:
                print(parrafos(
                    f"La puerta {hijo.carpeta}/ tiembla, pero sigue cerrada: además de "
                    f"{nombre.upper()} hace falta " + " y ".join(f.upper() for f in faltan) + ".",
                    color="amarillo"))
            else:
                j.abrir_puerta(actual, hijo)
                print("  " + C.ok(f"{SIMB['flecha']} La puerta {hijo.carpeta}/ se abre."))
                msg = actual.get("tras_abrir", {}).get(hijo.id)
                if msg:
                    print(parrafos(msg, sangria=4))
            abierto_algo = True
    if not abierto_algo:
        usos = [(p, h) for p in j.salas.values() for h in p.hijos
                if nombre in p.puertas.get(h.id, []) and not j.puerta_abierta(p, h)]
        if usos:
            donde = ", ".join(f"{h.carpeta}/ (en {p.titulo})" for p, h in usos)
            print(parrafos(f"Aquí no hay ninguna puerta que responda a {nombre.upper()}. "
                           f"Este hechizo abre: {donde}.", color="gris"))
        elif not nuevo:
            print(C.tenue("  Brilla un momento y se apaga. Aquí no hay nada que abrir con él."))
    print()
    return 0


def cmd_pista(args: list[str]):
    j = juego_actual()
    if j is None:
        sin_mazmorra()
        return 0
    s = j.sala_actual()
    print()
    if s is None:
        primera = j.ordenadas()[0]
        print(parrafos(f"Las pistas se dan dentro de una sala. Entra en una: `cd {primera.ruta_corta}` "
                       f"y escribe `mirar`."))
        print()
        return 0
    if j.superada(s) and not s.victoria:
        print(parrafos("Esta sala ya está superada. Mira el `mapa` para elegir la siguiente.", color="gris"))
        print()
        return 0
    usadas = j.estado["pistas"].get(s.id, 0)
    if usadas >= len(s.pistas):
        print(parrafos("No hay más pistas para esta sala: la última ya era la solución. "
                       "Vuelve a leerlas:", color="amarillo"))
    else:
        usadas += 1
        j.estado["pistas"][s.id] = usadas
        j.guardar()
    for i, p in enumerate(s.pistas[:usadas], start=1):
        marca = C.c(f"Pista {i}/{len(s.pistas)}:", "negrita", "amarillo+" if i == usadas else "gris")
        print("  " + marca)
        print(parrafos(p, sangria=4))
        print()
    return 0


def cmd_estado(args: list[str]):
    creados = juegos_creados()
    if not creados:
        sin_mazmorra()
        return 0
    j = juego_actual() or creados[-1]
    e = j.estado
    print()
    print("  " + C.titulo(e["nombre"]) + C.tenue(f"  ·  nivel {j.n['numero']}: {j.n['nombre']}"))
    salas = [s for s in j.salas.values()]
    superadas = [s for s in salas if j.superada(s)]
    n, total = len(superadas), len(salas)
    ancho = 30
    lleno = int(ancho * n / total)
    barra = C.ok("█" * lleno) + C.tenue("░" * (ancho - lleno))
    print(f"  Salas superadas  {barra} {n}/{total}")
    if j.n["tipo"] == "hechizos":
        todos = [s.hechizo for s in j.ordenadas() if s.hechizo and len(s.palabras) <= 1] + \
                [s.hechizo for s in j.ordenadas() if s.hechizo and len(s.palabras) > 1]
        partes = [C.magia(h.upper()) if h in e["hechizos"] else C.tenue(h) for h in todos]
        print(f"  Hechizos         {' '.join(partes)}")
    else:
        todos = [s for s in j.ordenadas() if not s.victoria]
        partes = [C.ok(s.mapa) if s.id in e["sellos"] else C.tenue(s.mapa) for s in todos]
        print(f"  Sellos           {' '.join(partes)}")
    print(f"  Pistas usadas    {j.pistas_usadas()}")
    print(f"  Tiempo de juego  {j.duracion()}")
    if e["terminado"]:
        print("  " + C.ok(f"{SIMB['superada']} NIVEL SUPERADO · código {j.codigo()}")
              + C.tenue(f"  ({abreviar_home(j.raiz / j.n['certificado'])})"))
    else:
        pendientes = [s for s in j.ordenadas() if j.alcanzable(s) and not j.superada(s)]
        if pendientes:
            print("  Salas abiertas por superar: " + ", ".join(C.c(s.titulo, "blanco") for s in pendientes))
    print()
    return 0


def cmd_reiniciar(args: list[str]):
    que = args[0] if args else ""
    if que == "sala":
        j = juego_actual()
        s = j.sala_actual() if j else None
        if s is None:
            print(C.aviso("Tienes que estar dentro de una sala para reiniciarla."))
            return 1
        j.reiniciar_sala(s)
        print(C.ok(f"Sala «{s.titulo}» restaurada: sus objetos y permisos vuelven a estar como al "
                   f"principio. Tu progreso (hechizos, puertas) se conserva."))
        return 0
    if que == "todo":
        creados = juegos_creados()
        j = juego_actual() or (creados[-1] if creados else None)
        if j is None:
            sin_mazmorra()
            return 1
        if sys.stdin.isatty() and "--si" not in args:
            r = input(f"¿Borrar la mazmorra del nivel {j.n['numero']} y empezar de cero? (s/N) ").strip().lower()
            if r not in ("s", "si", "sí", "y"):
                print("Nada cambia.")
                return 0
        nombre = j.estado["nombre"]
        j.crear_mundo(nombre)
        print(C.ok(f"Mazmorra del nivel {j.n['numero']} creada de nuevo. Empieza en: ")
              + C.cmd("cd " + j.ordenadas()[0].ruta_corta))
        return 0
    print("Uso:  mazmorra reiniciar sala   (restaura la sala en la que estás)")
    print("      mazmorra reiniciar todo   (borra todo y empieza de cero)")
    return 1


def cmd_ritual(args: list[str]):
    """Lo invocan los scripts ritual.sh del nivel de permisos."""
    j = juego_actual()
    if j is None or j.n["tipo"] != "permisos":
        print(C.aviso("Los rituales solo funcionan dentro de las catacumbas."))
        return 1
    s = j.sala_actual()
    if s is None:
        print(C.aviso("Tienes que estar dentro de una sala."))
        return 1
    script = Path(args[0]) if args else (s.dir / "ritual.sh")
    if not script.is_absolute():
        script = Path(os.getcwd()) / script
    print()
    print("  " + C.magia(f"✦ Ritual de {s.titulo}..."))
    if script.resolve().parent != s.dir.resolve():
        print(parrafos("Ese ritual pertenece a otra sala. Cada ritual solo funciona en la suya.", color="amarillo"))
        print()
        return 1
    if not os.access(script, os.X_OK):
        print(parrafos(
            f"El ritual no tiene fuerza: {script.name} no tiene permiso de EJECUCIÓN (x). "
            f"Míralo con `ls -l {script.name}`, dáselo con `chmod u+x {script.name}` y lánzalo "
            f"como `./{script.name}`.", color="rojo+"))
        print()
        return 1
    fallos = [(t, a) for ok, t, a in j.evaluar(s) if not ok]
    if fallos:
        print(parrafos("El círculo se enciende... y se apaga. La sala aún no está lista:", color="amarillo"))
        for t, a in fallos:
            print(f"    {C.mal(SIMB['mal'])} {formatear(t)}")
            if a:
                print(parrafos(a, sangria=8))
        print()
        return 1
    if s.victoria:
        if j.estado["terminado"]:
            print(C.tenue("  El altar ya está abierto. Tu certificado sigue en su sitio."))
            print()
        else:
            _victoria(j, s, desde_ritual=True)
        return 0
    nuevo = s.id not in j.estado["sellos"]
    if nuevo:
        j.estado["sellos"].append(s.id)
        j.guardar()
        print(pintar_arte("hechizo"))
        total = sum(1 for x in j.salas.values() if not x.victoria)
        print("  " + C.c(f"{SIMB['superada']} Sello conseguido: {s.titulo}", "negrita", "verde+")
              + C.tenue(f"  ({len(j.estado['sellos'])}/{total})"))
        print()
        if s.get("exito"):
            print(parrafos(s.exito))
            print()
    else:
        print(C.tenue("  Este sello ya lo tenías. El ritual brilla y se apaga."))
    for h in s.hijos:
        if j.puerta_abierta(s, h):
            print(f"  {C.ok(SIMB['flecha'])} La puerta {C.carpeta(h.carpeta + '/')} está abierta:  "
                  + C.cmd("cd " + h.carpeta))
        else:
            print(parrafos(
                f"La puerta {h.carpeta}/ sigue cerrada: `ls -ld {h.carpeta}` → {modo_texto(h.dir)}. "
                f"Aquí abajo las puertas las abres tú: `chmod u+rwx {h.carpeta}` (o `chmod 700 "
                f"{h.carpeta}`) y luego `cd {h.carpeta}`."))
    print()
    return 0


def _victoria(j: Juego, s: Sala, desde_ritual: bool = False):
    e = j.estado
    if not e["terminado"]:
        e["terminado"] = True
        e["fin"] = time.time()
        j.guardar()
    print()
    for l in rotulo("VICTORIA"):
        print("  " + C.c(l, "amarillo+"))
    print()
    print(pintar_arte(s.get("arte_victoria", "victoria")))
    print()
    if not desde_ritual:
        print(parrafos(s.descripcion))
        print()
    if s.get("exito"):
        print(parrafos(s.exito))
        print()
    f = j.escribir_certificado()
    print("  " + C.c(f"{SIMB['superada']} Has superado el nivel {j.n['numero']}: {j.n['nombre']}", "negrita", "verde+"))
    print(f"    Tiempo: {j.duracion()}   Pistas usadas: {j.pistas_usadas()}")
    print(f"    Código de certificado: {C.c(j.codigo(), 'negrita', 'amarillo+')}")
    print(f"    Certificado guardado en: {C.fichero(abreviar_home(f))}")
    print()
    if not desde_ritual:
        print("  " + C.c("OBJETIVO", "negrita", "amarillo+"))
        print(parrafos(s.objetivo, sangria=4))
    siguiente = j.n.get("siguiente")
    if siguiente:
        print()
        print(parrafos(siguiente, color="cian"))
    print()


def cmd_ayuda(args: list[str]):
    print()
    print("  " + C.titulo("MAZMORRA · ayuda") + C.tenue(f"  v{VERSION}"))
    print()
    print("  " + C.c("Comandos del grimorio (valen dentro de cualquier sala):", "negrita"))
    for cmd, desc in [
        ("mirar", "describe la sala: objetivo, progreso y qué hay en ella"),
        ("mapa", "mapa de las salas y cómo llegar a cada una"),
        ("inventario", "qué llevas en la mochila (o los sellos, en las catacumbas)"),
        ("lanzar HECHIZO", "lanza un hechizo (nivel 1)"),
        ("pista", "una ayuda; cada vez más concreta"),
        ("estado", "tu progreso"),
    ]:
        print(f"    {C.cmd(cmd):<32} {desc}")
    print()
    print("  " + C.c("Gestión del juego:", "negrita"))
    for cmd, desc in [
        ("mazmorra iniciar", "crea la mazmorra del nivel 1 (~/mazmorra)"),
        ("mazmorra iniciar --nivel 2", "crea las catacumbas (~/catacumbas)"),
        ("mazmorra reiniciar sala", "deja la sala actual como al principio (sin perder progreso)"),
        ("mazmorra reiniciar todo", "borra el nivel actual y empieza de cero"),
        ("mazmorra chuleta", "resumen de los comandos de Linux que usa el juego"),
    ]:
        print(f"    {C.cmd(cmd):<32} {desc}")
    print()
    return 0


CHULETA = """
NAVEGAR                             VER
  pwd           dónde estoy           cat f         todo de golpe
  cd ruta       ir                    less f        página a página (q sale)
  cd ..         subir una sala        head -n 5 f   primeras líneas
  cd ~/mazmorra/entrada  ruta absoluta   tail -n 5 f   últimas líneas
  ls            listar                wc -l f       contar líneas
  ls -a         listar también ocultos
  ls -l         listar con permisos

CREAR                               COPIAR / MOVER / BORRAR
  touch f       fichero vacío         cp o d        copiar
  mkdir c       carpeta               mv o d        mover o renombrar
  echo x > f    escribir (borra)      rm f          borrar fichero
  echo x >> f   añadir al final       rmdir c       borrar carpeta vacía
  cat a b > f   unir en f             rm -r c       borrar carpeta y contenido

COMODINES                           PERMISOS (nivel 2)
  *             lo que sea            ls -l         ver permisos
  ?             un carácter           chmod u+x f   dar x al dueño
  runa_*.txt    empieza por runa_     chmod o-r f   quitar r a otros
                                      chmod 750 c   octal: rwx r-x ---
AYUDA                                 chmod -R g+rX c   recursivo
  Tab           completa nombres      ./programa    ejecutar (necesita x)
  ↑             comando anterior
  cmd --help    ayuda rápida
"""


def cmd_chuleta(args: list[str]):
    print(C.c(CHULETA, "cian"))
    return 0
