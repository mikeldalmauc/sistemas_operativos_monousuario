// Ranking · lógica de la web (sin dependencias)
const API = 'api';   // relativo: funciona en / y bajo /ranking-comandos/
let nivelActual = 1;
let datos = [];

const $ = s => document.querySelector(s);
const tbody = $('#tabla tbody');

function tiempo(s) { return `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`; }
function fecha(iso) {
  const d = new Date(iso);
  return isNaN(d) ? '' : d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}
const medalla = i => ['🥇', '🥈', '🥉'][i] || String(i + 1);

async function cargar() {
  tbody.innerHTML = '<tr><td colspan="6" class="cargando">Cargando…</td></tr>';
  try {
    const r = await fetch(`${API}/ranking/${nivelActual}`);
    datos = await r.json();
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="6" class="cargando">No se puede hablar con el servidor.</td></tr>';
    return;
  }
  pintar();
}

function pintar() {
  const filtro = $('#filtro').value.trim().toLowerCase();
  const soloMejor = $('#soloMejor').checked;
  let lista = datos;                                     // ya viene ordenada por puntos desc
  if (soloMejor) {
    const vistos = new Set();
    lista = lista.filter(r => { const k = r.nombre.toLowerCase(); if (vistos.has(k)) return false; vistos.add(k); return true; });
  }
  if (filtro) lista = lista.filter(r => r.nombre.toLowerCase().includes(filtro));

  $('#resumen').textContent = `${lista.length} envío${lista.length === 1 ? '' : 's'} · ${new Set(datos.map(r => r.nombre.toLowerCase())).size} alumnos`;
  $('#vacio').hidden = lista.length > 0;
  tbody.innerHTML = '';
  lista.forEach((r, i) => {
    const tr = document.createElement('tr');
    tr.className = i < 3 ? 'podio' : '';
    tr.innerHTML = `
      <td class="pos">${medalla(i)}</td>
      <td class="nombre">${escapar(r.nombre)}</td>
      <td class="puntos">${r.puntos}</td>
      <td>${tiempo(r.tiempo_s)}</td>
      <td>${r.num_comandos}</td>
      <td class="fecha">${fecha(r.fecha)}</td>`;
    tr.title = 'Ver los comandos usados';
    tr.addEventListener('click', () => abrirModal(r, i));
    tbody.appendChild(tr);
  });
}

// --- claves por nivel (se recuerdan en este navegador) ---
const claves = { get: n => { try { return localStorage.getItem(`clave_nivel_${n}`) || ''; } catch { return ''; } },
                 set: (n, v) => { try { localStorage.setItem(`clave_nivel_${n}`, v); } catch {} },
                 borrar: n => { try { localStorage.removeItem(`clave_nivel_${n}`); } catch {} } };
let pendiente = null;   // envío que se quería abrir cuando se pidió la clave

function pedirClave(r, pos, error) {
  pendiente = { r, pos };
  $('#cNivel').textContent = r.nivel;
  $('#inputClave').value = '';
  $('#errorClave').hidden = !error;
  $('#modalClave').hidden = false;
  $('#inputClave').focus();
}
$('#formClave').addEventListener('submit', e => {
  e.preventDefault();
  const v = $('#inputClave').value.trim().toUpperCase();
  if (!pendiente || v.length < 8) return;
  claves.set(pendiente.r.nivel, v);
  $('#modalClave').hidden = true;
  abrirModal(pendiente.r, pendiente.pos);
});
$('#cerrarClave').addEventListener('click', () => { $('#modalClave').hidden = true; });
$('#modalClave').addEventListener('click', e => { if (e.target.id === 'modalClave') $('#modalClave').hidden = true; });
$('#olvidarClaves').addEventListener('click', () => { [1, 2, 3].forEach(claves.borrar); actualizarCandado(); });
function actualizarCandado() { $('#olvidarClaves').hidden = ![1, 2, 3].some(n => claves.get(n)); }

async function abrirModal(r, pos) {
  const clave = claves.get(r.nivel);
  if (!clave) return pedirClave(r, pos, false);
  $('#mTitulo').textContent = `${medalla(pos)} ${r.nombre} · Nivel ${r.nivel}`;
  $('#mDatos').textContent = `${r.puntos} puntos · ${tiempo(r.tiempo_s)} · ${r.num_comandos} comandos · ${fecha(r.fecha)}` + (r.usuario ? ` · usuario ${r.usuario}` : '');
  const ol = $('#mComandos');
  ol.innerHTML = '<li class="cargando">Cargando…</li>';
  $('#modal').hidden = false;
  try {
    const resp = await fetch(`${API}/resultados/${r.id}`, { headers: { 'X-Clave-Ver': clave } });
    if (resp.status === 401) {            // clave caducada o falsa: se olvida y se vuelve a pedir
      claves.borrar(r.nivel); actualizarCandado();
      $('#modal').hidden = true;
      return pedirClave(r, pos, true);
    }
    const det = await resp.json();
    actualizarCandado();
    ol.innerHTML = '';
    (det.comandos || []).forEach(c => {
      const li = document.createElement('li');
      li.innerHTML = `<code>${escapar(c)}</code>`;
      if (/^\s*sudo\b/.test(c)) li.classList.add('sudo');
      ol.appendChild(li);
    });
    if (!ol.children.length) ol.innerHTML = '<li class="cargando">Este envío no trae comandos.</li>';
  } catch {
    ol.innerHTML = '<li class="cargando">No se ha podido cargar el detalle.</li>';
  }
}
function cerrarModal() { $('#modal').hidden = true; }

function escapar(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

// --- eventos ---
document.querySelectorAll('.pestana').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('.pestana').forEach(x => x.classList.remove('activa'));
  b.classList.add('activa');
  nivelActual = parseInt(b.dataset.nivel, 10);
  cargar();
}));
$('#soloMejor').addEventListener('change', pintar);
$('#filtro').addEventListener('input', pintar);
$('#recargar').addEventListener('click', cargar);
$('#cerrar').addEventListener('click', cerrarModal);
$('#modal').addEventListener('click', e => { if (e.target.id === 'modal') cerrarModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarModal(); });

actualizarCandado();
cargar();
setInterval(cargar, 30000);   // se refresca solo cada 30 s (para proyectarlo en clase)
