// Anteprima home Odyra: filigrana. Tutto il testo è già nell'HTML; qui ci sono disegno, luce e movimento.
const $ = (s, r = document) => r.querySelector(s)
const $$ = (s, r = document) => [...r.querySelectorAll(s)]
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches

// Menu su schermi piccoli.
const nav = $('#nav')
const menu = $('#menu')
menu?.addEventListener('click', () => menu.setAttribute('aria-expanded', String(nav.classList.toggle('open'))))

// Guilloché: rosette e onde a linee sottili, come nella carta di sicurezza.
function guilloche(canvas, { rosette = null, waves = null, color = '92, 203, 240', phase = 0 }) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const w = canvas.clientWidth, h = canvas.clientHeight
  if (!w || !h) return
  if (canvas.width !== Math.round(w * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr) }
  const c = canvas.getContext('2d')
  c.setTransform(dpr, 0, 0, dpr, 0, 0)
  c.clearRect(0, 0, w, h)
  c.lineWidth = 0.7
  if (rosette) {
    const { x, y, r, lobes = 18, rings = 36, depth = 0.16, alpha = 0.16 } = rosette
    const cx = x * w, cy = y * h, R = r * Math.min(w, h)
    for (let k = 0; k < rings; k++) {
      c.strokeStyle = `rgba(${color}, ${alpha * (0.45 + 0.55 * Math.sin((k / rings) * Math.PI))})`
      c.beginPath()
      for (let i = 0; i <= 720; i++) {
        const t = (i / 720) * Math.PI * 2
        const rr = R * (0.55 + 0.45 * (k / rings)) * (1 + depth * Math.sin(lobes * t + phase + k * 0.21))
        const px = cx + rr * Math.cos(t), py = cy + rr * Math.sin(t)
        i ? c.lineTo(px, py) : c.moveTo(px, py)
      }
      c.stroke()
    }
  }
  if (waves) {
    const { lines = 26, amp = 0.05, freq = 3, alpha = 0.12, top = 0, bottom = 1 } = waves
    for (let k = 0; k < lines; k++) {
      const base = (top + (bottom - top) * (k / (lines - 1))) * h
      c.strokeStyle = `rgba(${color}, ${alpha})`
      c.beginPath()
      for (let x = 0; x <= w; x += 4) {
        const y = base + amp * h * Math.sin((x / w) * Math.PI * 2 * freq + phase + k * 0.32) * Math.sin((x / w) * Math.PI + k * 0.05)
        x ? c.lineTo(x, y) : c.moveTo(x, y)
      }
      c.stroke()
    }
  }
}

const art = [
  [$('.hero-guilloche'), (p) => ({ phase: p, rosette: { x: 0.78, y: 0.5, r: 0.62, lobes: 24, rings: 30, depth: 0.12, alpha: 0.09 } })],
  [$('.note-guilloche'), () => ({ phase: 0.6, rosette: { x: 0.24, y: 0.52, r: 0.42, lobes: 16, rings: 34, depth: 0.2, alpha: 0.32 }, waves: { lines: 22, amp: 0.035, freq: 2.5, alpha: 0.13, top: 0.1, bottom: 0.9 } })],
  [$('.close-guilloche'), (p) => ({ phase: p, waves: { lines: 34, amp: 0.06, freq: 2, alpha: 0.08, top: -0.05, bottom: 1.05 } })],
]
let phase = 0
const drawAll = () => art.forEach(([cv, opts]) => cv && guilloche(cv, opts(phase)))
drawAll()
new ResizeObserver(drawAll).observe(document.body)

// Il marchio sulla banconota: lo scrive chi visita.
const brand = $('#brand')
brand?.addEventListener('focus', () => { if (brand.value === 'Il tuo marchio') brand.select() })

// La luce dietro la carta: segue il puntatore e rivela la filigrana Odyra.
const note = $('#note')
const setLight = (x, y, lit) => {
  note.style.setProperty('--lx', x + 'px'); note.style.setProperty('--ly', y + 'px')
  if (lit !== undefined) note.style.setProperty('--lit', lit)
}
if (note) {
  if (reduce) note.style.setProperty('--wm-rest', '.22')
  note.addEventListener('pointermove', (e) => { const r = note.getBoundingClientRect(); setLight(e.clientX - r.left, e.clientY - r.top, 1) })
  note.addEventListener('pointerleave', () => note.style.setProperty('--lit', 0))
  note.addEventListener('pointerdown', (e) => { if (e.target !== brand) { const r = note.getBoundingClientRect(); setLight(e.clientX - r.left, e.clientY - r.top, 1) } })
}

window.addEventListener('load', () => {
  if (!window.gsap || reduce) return
  gsap.registerPlugin(ScrollTrigger, SplitText)

  // Apertura: il titolo si compone riga per riga, la banconota si posa, poi la luce la attraversa una volta.
  const split = SplitText.create('#hero-title', { type: 'lines', mask: 'lines' })
  const light = { x: -0.15, y: 0.55 }
  const sweep = () => { const r = note.getBoundingClientRect(); setLight(light.x * r.width, light.y * r.height) }
  gsap.timeline({ defaults: { ease: 'expo.out' } })
    .from(split.lines, { yPercent: 105, duration: 1.1, stagger: 0.12 })
    .from('.hero-lead', { opacity: 0, y: 16, duration: 0.9 }, '-=0.7')
    .from('.hero .actions > *', { opacity: 0, y: 12, duration: 0.7, stagger: 0.08 }, '-=0.6')
    .from('.note', { opacity: 0, y: 60, rotate: -9, scale: 0.94, duration: 1.4 }, 0.2)
    .add(() => note.style.setProperty('--lit', 1), '-=0.2')
    .to(light, { x: 1.15, y: 0.45, duration: 2.2, ease: 'power2.inOut', onUpdate: sweep }, '<')
    .add(() => note.style.setProperty('--lit', 0))

  // Il fondo guilloché respira piano mentre l'apertura è visibile.
  let running = true
  ScrollTrigger.create({ trigger: '.hero', start: 'top bottom', end: 'bottom top', onToggle: (s) => { running = s.isActive } })
  gsap.ticker.add(() => { if (running) { phase += 0.004; guilloche(art[0][0], art[0][1](phase)) } })

  // Il filo di sicurezza si srotola lungo i passaggi della fabbrica.
  gsap.fromTo('.line-thread i', { scaleY: 0 }, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: '.line', start: 'top 70%', end: 'bottom 60%', scrub: 0.5 } })
  $$('.line li').forEach((li) => {
    ScrollTrigger.create({ trigger: li, start: 'top 68%', onEnter: () => li.classList.add('on'), onLeaveBack: () => li.classList.remove('on') })
  })

  document.fonts?.ready.then(() => ScrollTrigger.refresh())
})

// Il marchio scritto sulla banconota firma anche la demo.
const brandTargets = $$('[data-brand]')
const syncBrand = () => { const v = brand.value.trim().slice(0, 18) || 'Il tuo marchio'; brandTargets.forEach((el) => { el.textContent = v }) }
brand?.addEventListener('input', syncBrand)

// Onda della voce: si muove quando parla l'agente, quasi ferma quando ascolta.
const wave = $('.wave')
const voice = { level: 0.15 }
function drawWave(t) {
  if (!wave) return
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = wave.clientWidth, h = wave.clientHeight
  if (wave.width !== Math.round(w * dpr)) { wave.width = Math.round(w * dpr); wave.height = Math.round(h * dpr) }
  const c = wave.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h)
  const bars = Math.floor(w / 6)
  for (let i = 0; i < bars; i++) {
    const n = Math.sin(i * 0.37 + t * 0.006) * 0.5 + Math.sin(i * 0.11 - t * 0.004) * 0.35 + Math.sin(i * 1.7 + t * 0.013) * 0.15
    const bh = Math.max(2, Math.abs(n) * h * voice.level * (0.6 + 0.4 * Math.sin((i / bars) * Math.PI)))
    c.fillStyle = `rgba(92, 203, 240, ${0.35 + 0.65 * voice.level})`
    c.fillRect(i * 6, (h - bh) / 2, 3, bh)
  }
}
drawWave(0)

window.addEventListener('load', () => {
  if (!window.gsap || reduce) return

  // La banconota si inclina col puntatore, come un foglio tenuto in mano.
  if (note && matchMedia('(hover: hover)').matches) {
    const rx = gsap.quickTo(note, 'rotationX', { duration: 0.6, ease: 'power3.out' })
    const ry = gsap.quickTo(note, 'rotationY', { duration: 0.6, ease: 'power3.out' })
    note.addEventListener('pointermove', (e) => { const r = note.getBoundingClientRect(); ry(((e.clientX - r.left) / r.width - 0.5) * 14); rx(-((e.clientY - r.top) / r.height - 0.5) * 10) })
    note.addEventListener('pointerleave', () => { rx(0); ry(0) })
  }

  // Le cifre salgono quando entrano.
  $$('.count').forEach((el) => {
    const to = +el.dataset.to, o = { v: 0 }
    gsap.to(o, { v: to, duration: 1.6, ease: 'expo.out', scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      onUpdate: () => { el.textContent = Math.round(o.v).toLocaleString('it-IT') } })
  })
  gsap.from('.partners li', { opacity: 0, y: 18, duration: 0.8, ease: 'expo.out', stagger: 0.07, scrollTrigger: { trigger: '.partners', start: 'top 85%', once: true } })

  // La chiamata: le battute arrivano una alla volta, poi l'appuntamento entra in agenda e parte la conferma.
  const lines = $$('.transcript li')
  gsap.ticker.add((time) => drawWave(time * 1000))
  const call = gsap.timeline({ paused: true })
  call.set(lines, { opacity: 0, y: 12 }).set('.slot-new .booked', { opacity: 0, scale: 0.9 }).set('.wa-toast', { opacity: 0, y: 14 })
  lines.forEach((li) => {
    const ai = li.classList.contains('t-ai')
    call.to(li, { opacity: 1, y: 0, duration: 0.5, ease: 'expo.out' })
      .to(voice, { level: ai ? 1 : 0.35, duration: 0.3 }, '<')
      .to({}, { duration: ai ? 1.6 : 1.1 })
  })
  call.to(voice, { level: 0.12, duration: 0.5 })
    .to('.slot-new .booked', { opacity: 1, scale: 1, duration: 0.7, ease: 'back.out(1.6)' }, '-=0.2')
    .to('.wa-toast', { opacity: 1, y: 0, duration: 0.6, ease: 'expo.out' }, '+=0.4')
  ScrollTrigger.create({ trigger: '.demo-in', start: 'top 70%', once: true, onEnter: () => call.play(0) })
  $('.replay')?.addEventListener('click', () => call.play(0))
})
