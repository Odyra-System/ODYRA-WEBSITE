// Menu mobile.
const nav = document.getElementById('nav')
const burger = document.getElementById('burger')
burger?.addEventListener('click', () => {
  const open = nav.classList.toggle('open')
  burger.setAttribute('aria-expanded', String(open))
  document.body.style.overflow = open ? 'hidden' : ''
})
nav?.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => {
  nav.classList.remove('open'); burger?.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''
}))

const PAGE_LANG = document.documentElement.lang

// Demo: lo stesso agente dentro un gestionale con due marchi diversi.
const app = document.getElementById('demo')
if (app) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  const slot = app.querySelector('.slot')
  const lines = [...app.querySelectorAll('.l')]
  const fresh = app.querySelector('.new')
  const wa = app.querySelector('.wa-chip')
  const SKINS = {
    boss: () => '<img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><b>GoAgent</b>',
    partner: () => `<div class="slot-empty">${app.dataset.slotEmpty}</div>`,
  }
  let timers = []
  const reset = () => { lines.forEach((l) => l.classList.remove('on')); fresh.classList.remove('on'); wa.classList.remove('on'); app.classList.remove('call-on') }
  const play = () => {
    timers.forEach(clearTimeout); timers = []; reset()
    if (reduce) { lines.forEach((l) => l.classList.add('on')); fresh.classList.add('on'); wa.classList.add('on'); return }
    app.classList.add('call-on')
    const at = (ms, fn) => timers.push(setTimeout(fn, ms))
    lines.forEach((l, i) => at(700 + i * 1500, () => l.classList.add('on')))
    const end = 700 + lines.length * 1500
    at(end, () => fresh.classList.add('on'))
    at(end + 200, () => wa.classList.add('on'))
    at(end + 6000, play)
  }
  const setSkin = (s) => {
    app.dataset.skin = s; slot.innerHTML = SKINS[s]()
    document.querySelectorAll('.demo-tabs button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.skin === s)))
    play()
  }
  document.querySelectorAll('.demo-tabs button').forEach((b) => b.addEventListener('click', () => setSkin(b.dataset.skin)))
  setSkin('boss')
}

// Video: se in assets/video/ esiste NOME.mp4 sostituisce il segnaposto.
// Sottotitoli: NOME.it.vtt, NOME.es.vtt, NOME.en.vtt, NOME.de.vtt, NOME.fr.vtt (compaiono nel menu del lettore).
const exists = (u) => fetch(u, { method: 'HEAD', cache: 'no-cache' }).then((r) => r.ok).catch(() => false)
const SUB = { it: 'Italiano', es: 'Español', en: 'English', de: 'Deutsch', fr: 'Français' }
document.querySelectorAll('.vid[data-vid]').forEach(async (box) => {
  const n = box.dataset.vid, base = `/assets/video/${n}`
  if (!(await exists(`${base}.mp4`))) return
  const v = document.createElement('video')
  v.controls = true; v.playsInline = true; v.preload = 'metadata'
  if (await exists(`${base}.jpg`)) v.poster = `${base}.jpg`
  v.src = `${base}.mp4`
  for (const l of Object.keys(SUB)) {
    if (!(await exists(`${base}.${l}.vtt`))) continue
    const t = document.createElement('track')
    t.kind = 'subtitles'; t.srclang = l; t.label = SUB[l]; t.src = `${base}.${l}.vtt`
    if (l === PAGE_LANG && l !== 'it') t.default = true
    v.appendChild(t)
  }
  box.replaceChildren(v)
})

// Modulo contatti.
// Finché FORM_ENDPOINT è vuoto la richiesta si apre nel client di posta, già scritta.
// Con un webhook (per esempio n8n) basta incollarne l'indirizzo: i dati partono in POST come JSON.
const FORM_ENDPOINT = ''
const FORM_EMAIL = 'team@odyrasystemautomation.it'
const form = document.getElementById('form-contatti')
if (form) {
  const msg = document.getElementById('form-msg')
  const q = new URLSearchParams(location.search).get('interesse')
  if (q && form.interesse) form.interesse.value = q
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    if (form.company_site.value) return
    if (!form.checkValidity()) { form.reportValidity(); return }
    const d = Object.fromEntries(new FormData(form)); delete d.company_site
    const es = PAGE_LANG === 'es'
    if (!FORM_ENDPOINT) {
      const body = Object.entries(d).map(([k, v]) => `${k}: ${v}`).join('\n')
      location.href = `mailto:${FORM_EMAIL}?subject=${encodeURIComponent((es ? 'Solicitud web: ' : 'Richiesta dal sito: ') + d.interesse)}&body=${encodeURIComponent(body)}`
      msg.className = 'form-msg ok'; msg.textContent = es ? 'Abrimos tu correo con la solicitud ya escrita.' : 'Abbiamo aperto la tua posta con la richiesta già scritta.'
      return
    }
    try {
      const r = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...d, lingua: PAGE_LANG, pagina: location.href }) })
      if (!r.ok) throw new Error(r.status)
      form.reset(); msg.className = 'form-msg ok'; msg.textContent = es ? 'Gracias. Te respondemos en un día laborable.' : 'Grazie. Ti rispondiamo entro un giorno lavorativo.'
    } catch {
      msg.className = 'form-msg err'; msg.textContent = es ? `No se pudo enviar. Escríbenos a ${FORM_EMAIL}.` : `Invio non riuscito. Scrivici a ${FORM_EMAIL}.`
    }
  })
}
