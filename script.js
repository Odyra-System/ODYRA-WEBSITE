// Intestazione: bordo e ombra appena si scorre; menu mobile.
const hdr = document.getElementById('top')
const onScroll = () => hdr.classList.toggle('scrolled', window.scrollY > 8)
onScroll(); window.addEventListener('scroll', onScroll, { passive: true })

const burger = document.getElementById('burger')
const nav = document.getElementById('nav')
burger?.addEventListener('click', () => {
  const open = nav.classList.toggle('open')
  burger.setAttribute('aria-expanded', String(open))
  document.body.style.overflow = open ? 'hidden' : ''
})
nav?.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => {
  nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''
}))
document.querySelectorAll('.dd > button').forEach((b) => b.addEventListener('click', () => {
  const dd = b.parentElement, o = dd.classList.toggle('open'); b.setAttribute('aria-expanded', String(o))
}))

// Comparsa al scroll.
const io = new IntersectionObserver((es) => es.forEach((e) => {
  if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target) }
}), { threshold: 0.12 })
document.querySelectorAll('.rv').forEach((el) => io.observe(el))

// Contatori dei numeri chiave.
const cio = new IntersectionObserver((es) => es.forEach((e) => {
  if (!e.isIntersecting) return
  const el = e.target, to = +el.dataset.count, dur = 1400, t0 = performance.now()
  const f = (t) => {
    const p = Math.min(1, (t - t0) / dur), v = Math.round(to * (1 - Math.pow(1 - p, 3)))
    el.textContent = v.toLocaleString(document.documentElement.lang === 'es' ? 'es-ES' : 'it-IT')
    if (p < 1) requestAnimationFrame(f)
  }
  requestAnimationFrame(f); cio.unobserve(el)
}), { threshold: 0.6 })
document.querySelectorAll('[data-count]').forEach((el) => cio.observe(el))

// Simulazione della conversazione WhatsApp (pagina prodotto).
document.querySelectorAll('.wa').forEach((wa) => {
  const bs = [...wa.querySelectorAll('.b')]
  let i = 0
  const run = () => {
    if (i < bs.length) { bs[i++].classList.add('on'); setTimeout(run, 1500) }
    else setTimeout(() => { bs.forEach((b) => b.classList.remove('on')); i = 0; setTimeout(run, 800) }, 6000)
  }
  new IntersectionObserver((es, o) => { if (es[0].isIntersecting) { run(); o.disconnect() } }, { threshold: 0.4 }).observe(wa)
})

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
    if (form.company_site.value) return // campo trappola per lo spam
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
      form.reset(); msg.className = 'form-msg ok'; msg.textContent = es ? 'Gracias. Te respondemos en 24 horas laborables.' : 'Grazie. Ti rispondiamo entro un giorno lavorativo.'
    } catch {
      msg.className = 'form-msg err'; msg.textContent = es ? `No se pudo enviar. Escríbenos a ${FORM_EMAIL}.` : `Invio non riuscito. Scrivici a ${FORM_EMAIL}.`
    }
  })
}
