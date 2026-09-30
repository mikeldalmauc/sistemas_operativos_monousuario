// Servicio de ranking · Pruebas de comandos SOM
// Recibe los resultados que envía prueba.sh y los sirve ordenados por puntos.
// Sin dependencias (solo Node). Almacenamiento: un fichero JSON en /datos (volumen de Docker).

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PUERTO = parseInt(process.env.PUERTO || '3000', 10);
const DATOS = process.env.DATOS || '/datos';
const FICHERO = path.join(DATOS, 'resultados.json');
const CLAVE = process.env.CLAVE || 'som-2026';          // la misma que en config.env del alumno
const CLAVE_ADMIN = process.env.CLAVE_ADMIN || '';      // para borrar envíos (vacía = desactivado)
const MAX_COMANDOS = 1000;

// misma fórmula que en lib/comun.sh
const puntos = (tiempo_s, num_comandos) => Math.floor(100000 / (tiempo_s + 5 * num_comandos + 60));

// ---------- persistencia ----------
fs.mkdirSync(DATOS, { recursive: true });
let resultados = [];
try { resultados = JSON.parse(fs.readFileSync(FICHERO, 'utf8')); } catch { resultados = []; }
function guardar() {
  const tmp = FICHERO + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(resultados, null, 1));
  fs.renameSync(tmp, FICHERO);
}

// ---------- utilidades ----------
function json(res, codigo, cuerpo) {
  res.writeHead(codigo, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(cuerpo));
}
function leerCuerpo(req) {
  return new Promise((resolve, reject) => {
    let d = '';
    req.on('data', c => { d += c; if (d.length > 1e6) { reject(new Error('demasiado grande')); req.destroy(); } });
    req.on('end', () => { try { resolve(d ? JSON.parse(d) : {}); } catch { reject(new Error('JSON inválido')); } });
    req.on('error', reject);
  });
}
const posicion = r => resultados.filter(x => x.nivel === r.nivel && x.puntos > r.puntos).length + 1;

// ---------- rutas ----------
async function recibirResultado(req, res) {
  if ((req.headers['x-clave'] || '') !== CLAVE) return json(res, 401, { error: 'clave incorrecta' });
  let b;
  try { b = await leerCuerpo(req); } catch (e) { return json(res, 400, { error: e.message }); }
  const nombre = String(b.nombre || '').trim().slice(0, 60);
  const nivel = parseInt(b.nivel, 10);
  const tiempo_s = parseInt(b.tiempo_s, 10);
  const comandos = Array.isArray(b.comandos) ? b.comandos.slice(0, MAX_COMANDOS).map(c => String(c).slice(0, 500)) : [];
  const num_comandos = Number.isInteger(b.num_comandos) ? b.num_comandos : comandos.length;
  if (nombre.length < 2) return json(res, 400, { error: 'nombre inválido' });
  if (![1, 2, 3].includes(nivel)) return json(res, 400, { error: 'nivel inválido' });
  if (!(tiempo_s >= 1 && tiempo_s < 86400 * 7)) return json(res, 400, { error: 'tiempo inválido' });
  if (num_comandos < 1) return json(res, 400, { error: 'sin comandos' });

  const r = {
    id: crypto.randomBytes(6).toString('hex'),
    nombre, nivel, tiempo_s, num_comandos,
    puntos: puntos(tiempo_s, num_comandos),
    fecha: new Date().toISOString(),
    fecha_alumno: String(b.fecha || '').slice(0, 40),
    usuario: String(b.usuario || '').slice(0, 40),
    equipo: String(b.equipo || '').slice(0, 60),
    comandos,
  };
  resultados.push(r);
  guardar();
  console.log(`[envío] nivel ${nivel} · ${nombre} · ${tiempo_s}s · ${num_comandos} cmd · ${r.puntos} pts`);
  json(res, 201, { ok: true, id: r.id, puntos: r.puntos, posicion: posicion(r) });
}

function ranking(res, nivel) {
  const lista = resultados
    .filter(r => r.nivel === nivel)
    .sort((a, b) => b.puntos - a.puntos || a.tiempo_s - b.tiempo_s || a.fecha.localeCompare(b.fecha))
    .map(({ comandos, ...resto }) => resto);            // sin el histórico, que pesa
  json(res, 200, lista);
}

function detalle(res, id) {
  const r = resultados.find(x => x.id === id);
  r ? json(res, 200, r) : json(res, 404, { error: 'no existe' });
}

function borrar(req, res, id) {  // profesor: curl -X DELETE -H "X-Clave-Admin: …" http://…/api/resultados/ID
  if (!CLAVE_ADMIN || (req.headers['x-clave-admin'] || '') !== CLAVE_ADMIN) return json(res, 401, { error: 'no autorizado' });
  const antes = resultados.length;
  resultados = resultados.filter(x => x.id !== id);
  if (resultados.length === antes) return json(res, 404, { error: 'no existe' });
  guardar();
  json(res, 200, { ok: true });
}

// ---------- servidor ----------
http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  const p = url.pathname.replace(/\/+$/, '');
  let m;
  if (req.method === 'OPTIONS') { res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': 'GET,POST,DELETE' }); return res.end(); }
  if (req.method === 'GET'    && p === '/api/salud')                         return json(res, 200, { ok: true, envios: resultados.length });
  if (req.method === 'POST'   && p === '/api/resultados')                    return recibirResultado(req, res);
  if (req.method === 'GET'    && (m = p.match(/^\/api\/ranking\/([123])$/))) return ranking(res, parseInt(m[1], 10));
  if (req.method === 'GET'    && (m = p.match(/^\/api\/resultados\/(\w+)$/)))return detalle(res, m[1]);
  if (req.method === 'DELETE' && (m = p.match(/^\/api\/resultados\/(\w+)$/)))return borrar(req, res, m[1]);
  json(res, 404, { error: 'ruta desconocida' });
}).listen(PUERTO, () => console.log(`Ranking SOM escuchando en :${PUERTO} · ${resultados.length} envíos cargados de ${FICHERO}`));
