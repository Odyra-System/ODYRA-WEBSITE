// Intestazione e menu mobile.
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
document.querySelectorAll('.dd > button').forEach((b) => b.addEventListener('click', () => {
  const o = b.parentElement.classList.toggle('open'); b.setAttribute('aria-expanded', String(o))
}))

// Demo in apertura: lo stesso agente, dentro un gestionale con due marchi diversi.
const app = document.getElementById('demo')
if (app) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  const slot = app.querySelector('.slot')
  const lines = [...app.querySelectorAll('.l')]
  const fresh = app.querySelector('.new')
  const wa = app.querySelector('.wa-chip')
  const SKINS = {
    boss: () => `<img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><b>GoAgent</b>`,
    partner: () => `<div class="slot-empty">${app.dataset.slotEmpty}</div>`,
  }
  let timers = []
  const clear = () => { timers.forEach(clearTimeout); timers = [] }
  const reset = () => { lines.forEach((l) => l.classList.remove('on')); fresh.classList.remove('on'); wa.classList.remove('on'); app.classList.remove('call-on') }
  const showAll = () => { lines.forEach((l) => l.classList.add('on')); fresh.classList.add('on'); wa.classList.add('on') }
  const play = () => {
    clear(); reset()
    if (reduce) { showAll(); return }
    app.classList.add('call-on')
    const at = (ms, fn) => timers.push(setTimeout(fn, ms))
    lines.forEach((l, i) => at(700 + i * 1500, () => l.classList.add('on')))
    at(700 + lines.length * 1500, () => fresh.classList.add('on'))
    at(900 + lines.length * 1500, () => wa.classList.add('on'))
    at(900 + lines.length * 1500 + 6000, play)
  }
  const setSkin = (s) => {
    app.dataset.skin = s; slot.innerHTML = SKINS[s]()
    document.querySelectorAll('.demo-tabs button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.skin === s)))
    play()
  }
  document.querySelectorAll('.demo-tabs button').forEach((b) => b.addEventListener('click', () => setSkin(b.dataset.skin)))
  setSkin('boss')
}

// Video e registrazioni reali: compaiono solo se i file esistono in assets/video e assets/audio.
document.querySelectorAll('.media[data-video]').forEach((box) => {
  const v = box.querySelector('video')
  v.addEventListener('loadeddata', () => { box.hidden = false }, { once: true })
  v.src = box.dataset.video
})
const audioBox = document.getElementById('audio-demo')
if (audioBox) {
  fetch('/assets/audio/chiamate.json', { cache: 'no-cache' })
    .then((r) => (r.ok ? r.json() : []))
    .then((list) => {
      if (!Array.isArray(list) || !list.length) return
      const lang = document.documentElement.lang
      const wrap = audioBox.querySelector('.audio-list')
      list.forEach((c) => {
        const d = document.createElement('div'); d.className = 'audio-item'
        const b = document.createElement('b'); b.textContent = c['titolo_' + lang] || c.titolo
        const a = document.createElement('audio'); a.controls = true; a.preload = 'none'; a.src = '/assets/audio/' + c.file
        d.append(b, a); wrap.appendChild(d)
      })
      audioBox.hidden = false
    }).catch(() => {})
}

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
    const es = document.documentElement.lang === 'es'
    if (!FORM_ENDPOINT) {
      const body = Object.entries(d).map(([k, v]) => `${k}: ${v}`).join('\n')
      location.href = `mailto:${FORM_EMAIL}?subject=${encodeURIComponent((es ? 'Solicitud web: ' : 'Richiesta dal sito: ') + d.interesse)}&body=${encodeURIComponent(body)}`
      msg.className = 'form-msg ok'; msg.textContent = es ? 'Abrimos tu correo con la solicitud ya escrita.' : 'Abbiamo aperto la tua posta con la richiesta già scritta.'
      return
    }
    try {
      const r = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...d, lingua: document.documentElement.lang, pagina: location.href }) })
      if (!r.ok) throw new Error(r.status)
      form.reset(); msg.className = 'form-msg ok'; msg.textContent = es ? 'Gracias. Te respondemos en un día laborable.' : 'Grazie. Ti rispondiamo entro un giorno lavorativo.'
    } catch {
      msg.className = 'form-msg err'; msg.textContent = es ? `No se pudo enviar. Escríbenos a ${FORM_EMAIL}.` : `Invio non riuscito. Scrivici a ${FORM_EMAIL}.`
    }
  })
}
