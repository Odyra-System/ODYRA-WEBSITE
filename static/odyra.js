// Sito Odyra: filigrana. Tutto il testo è già nell'HTML; qui ci sono disegno, luce e movimento.
const $ = (s, r = document) => r.querySelector(s)
const $$ = (s, r = document) => [...r.querySelectorAll(s)]
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
// Lingua della pagina: i pochi testi scritti da qui seguono l'HTML.
const LANG = document.documentElement.lang === 'es' ? 'es' : 'it'
const LOCALE = LANG === 'es' ? 'es-ES' : 'it-IT'
const TXT = {
  it: { sede: ' sede', sedi: ' sedi', subject: 'Richiesta dal sito: ' },
  es: { sede: ' sede', sedi: ' sedes', subject: 'Solicitud desde la web: ' },
}[LANG]

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
  // L'attestato dell'Academy: carta chiara, inchiostro blu.
  ...$$('.cert-guilloche').map((cv) => [cv, () => ({ color: '15, 110, 153', phase: 1.2, rosette: { x: 0.5, y: 0.5, r: 0.62, lobes: 20, rings: 28, depth: 0.14, alpha: 0.13 }, waves: { lines: 16, amp: 0.025, freq: 3, alpha: 0.07, top: 0.06, bottom: 0.94 } })]),
]
let phase = 0
const drawAll = () => art.forEach(([cv, opts]) => cv && guilloche(cv, opts(phase)))
drawAll()
new ResizeObserver(drawAll).observe(document.body)

// Il marchio sulla banconota: lo scrive chi visita.
const brand = $('#brand')
brand?.addEventListener('focus', () => { if (brand.value === brand.defaultValue) brand.select() })

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
  if (note) {
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
  } else {
    // Pagine interne: il titolo si compone riga per riga.
    const h1 = $('.phead h1')
    if (h1) {
      const s = SplitText.create(h1, { type: 'lines', mask: 'lines' })
      gsap.timeline({ defaults: { ease: 'expo.out' } }).from(s.lines, { yPercent: 105, duration: 1, stagger: 0.1 }).from('.phead .hero-lead, .phead .actions, .phead .jump', { opacity: 0, y: 14, duration: 0.8, stagger: 0.08 }, '-=0.6')
    }
  }

  // Il fondo guilloché respira piano mentre l'apertura è visibile.
  let running = !!$('.hero-guilloche')
  if ($('.hero, .phead')) ScrollTrigger.create({ trigger: '.hero, .phead', start: 'top bottom', end: 'bottom top', onToggle: (s) => { running = s.isActive } })
  gsap.ticker.add(() => { if (running) { phase += 0.004; guilloche(art[0][0], art[0][1](phase)) } })

  // Il filo di sicurezza si srotola lungo i passaggi della fabbrica.
  if ($('.line')) gsap.fromTo('.line-thread i', { scaleY: 0 }, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: '.line', start: 'top 70%', end: 'bottom 60%', scrub: 0.5 } })
  $$('.line li').forEach((li) => {
    ScrollTrigger.create({ trigger: li, start: 'top 68%', onEnter: () => li.classList.add('on'), onLeaveBack: () => li.classList.remove('on') })
  })

  document.fonts?.ready.then(() => ScrollTrigger.refresh())
})

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
      onUpdate: () => { el.textContent = Math.round(o.v).toLocaleString(LOCALE) } })
  })
  if ($('.partners')) gsap.from('.partners li', { opacity: 0, y: 18, duration: 0.8, ease: 'expo.out', stagger: 0.07, scrollTrigger: { trigger: '.partners', start: 'top 85%', once: true } })
})

window.addEventListener('load', () => {
  if (!window.gsap) return
  gsap.registerPlugin(ScrollTrigger)

  // La pila: su schermi larghi la sezione si ferma, gli strati si separano e si accendono uno alla volta.
  const depth = $('.depth')
  if (depth && $('.stack')) {
    const plates = $$('.plate'), labels = $$('.layer-labels li')
    const mark = (k) => { plates.forEach((p, i) => p.classList.toggle('on', i === k)); labels.forEach((l, i) => l.classList.toggle('on', i === k)) }
    gsap.matchMedia().add('(min-width: 901px) and (prefers-reduced-motion: no-preference)', () => {
      depth.classList.add('live')
      const st = { gap: 0.9 }
      const stack = $('.stack')
      const tl = gsap.timeline({ scrollTrigger: { trigger: depth, pin: true, start: 'top top', end: '+=1800', scrub: 0.8,
        onUpdate: (s) => mark(s.progress < 0.28 ? -1 : Math.min(plates.length - 1, Math.floor((s.progress - 0.28) / 0.72 * plates.length))) } })
      tl.fromTo(st, { gap: 0.9 }, { gap: 4.4, duration: 1, ease: 'power2.inOut', onUpdate: () => stack.style.setProperty('--gap', st.gap + 'rem') })
        .fromTo('.stack', { rotateZ: 0, y: 30 }, { rotateZ: 6, y: 0, duration: 1, ease: 'power1.inOut' }, 0)
        .to({}, { duration: 2.6 })
      return () => { depth.classList.remove('live'); stack.style.removeProperty('--gap'); mark(-1) }
    })
  }

  // Casi di successo: quando un caso è al centro, la sezione prende il colore di quel cliente.
  const cases = $('.cases')
  const active = new Set()
  const paint = () => {
    const last = [...active].pop()
    cases.classList.toggle('tinted', !!last)
    cases.style.setProperty('--tint', last ? last.dataset.tint : '')
    if (!last) cases.style.removeProperty('--tint')
  }
  $$('.cases .case').forEach((c) => ScrollTrigger.create({ trigger: c, start: 'top 55%', end: 'bottom 45%',
    onToggle: (s) => { s.isActive ? active.add(c) : active.delete(c); paint() } }))

  ScrollTrigger.refresh()
})

// Catalogo degli agenti: frecce, filtri, trascinamento col mouse, avanzamento.
const vp = $('.agents-viewport')
if (vp) {
  const all = $$('.agent', vp)
  const visible = () => all.filter((a) => !a.hidden)
  const now = $('#ax-now'), tot = $('#ax-tot'), bar = $('#ax-bar'), prev = $('#ax-prev'), next = $('#ax-next')
  const step = () => (visible()[1]?.offsetLeft ?? 0) - (visible()[0]?.offsetLeft ?? 0) || 340
  const update = () => {
    const v = visible(), max = vp.scrollWidth - vp.clientWidth
    const left = vp.getBoundingClientRect().left
    let first = v.findIndex((a) => a.getBoundingClientRect().right > left + 40)
    if (first < 0) first = 0
    const shown = v.filter((a) => { const r = a.getBoundingClientRect(); return r.left < innerWidth - 40 && r.right > 40 }).length || 1
    now.textContent = Math.min(first + 1, v.length)
    tot.textContent = v.length
    bar.style.width = Math.min(100, (shown / v.length) * 100) + '%'
    bar.style.transform = `translateX(${max > 0 ? (vp.scrollLeft / max) * (100 / Math.min(1, shown / v.length) - 100) : 0}%)`
    prev.disabled = vp.scrollLeft < 8
    next.disabled = vp.scrollLeft > max - 8
    v.forEach((a) => { const r = a.getBoundingClientRect(); a.classList.toggle('out', r.right > innerWidth + 20 || r.left < -20) })
  }
  prev.addEventListener('click', () => vp.scrollBy({ left: -step() }))
  next.addEventListener('click', () => vp.scrollBy({ left: step() }))
  vp.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); vp.scrollBy({ left: step() }) }
    if (e.key === 'ArrowLeft') { e.preventDefault(); vp.scrollBy({ left: -step() }) }
  })
  vp.addEventListener('scroll', () => requestAnimationFrame(update), { passive: true })
  window.addEventListener('resize', update)
  $$('.filters button').forEach((btn) => btn.addEventListener('click', () => {
    $$('.filters button').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)))
    const f = btn.dataset.f
    all.forEach((a) => { a.hidden = f !== 'all' && a.dataset.cat !== f })
    vp.scrollTo({ left: 0, behavior: 'instant' })
    if (window.gsap && !reduce) gsap.from(visible().map((a) => a.querySelector('.screen')), { opacity: 0, y: 24, duration: 0.6, ease: 'expo.out', stagger: 0.05 })
    update()
  }))
  // Trascinamento col mouse (su touch scorre già col dito).
  let down = false, sx = 0, sl = 0, moved = 0
  vp.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') return; down = true; moved = 0; sx = e.clientX; sl = vp.scrollLeft })
  window.addEventListener('pointermove', (e) => { if (!down) return; const dx = e.clientX - sx; moved = Math.abs(dx); if (moved > 4) vp.classList.add('dragging'); vp.scrollLeft = sl - dx })
  window.addEventListener('pointerup', () => { if (!down) return; down = false; vp.classList.remove('dragging') })
  update()
}

// Modulo contatti: finché FORM_ENDPOINT è vuoto apre la posta con la richiesta già scritta.
const FORM_ENDPOINT = ''
const form = $('#form-contatti')
if (form) {
  const msg = $('#form-msg')
  const q = new URLSearchParams(location.search).get('interesse')
  const pre = q && form.querySelector(`input[name=interesse][value="${CSS.escape(q)}"]`)
  if (pre) pre.checked = true
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    msg.classList.remove('err')
    if (!form.checkValidity()) { form.reportValidity(); return }
    const data = Object.fromEntries(new FormData(form))
    if (!FORM_ENDPOINT) {
      const body = Object.entries(data).filter(([k]) => k !== 'privacy').map(([k, v]) => `${k}: ${v}`).join('\n')
      location.href = `mailto:team@odyrasystemautomation.it?subject=${encodeURIComponent(TXT.subject + data.interesse)}&body=${encodeURIComponent(body)}`
      msg.textContent = form.dataset.mail
      return
    }
    try {
      const r = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      if (!r.ok) throw new Error(String(r.status))
      form.reset(); msg.textContent = form.dataset.ok
    } catch { msg.classList.add('err'); msg.textContent = form.dataset.err }
  })
}

// Da una sede a mille: il cursore accende le sedi, le voci "resta uguale" non cambiano.
const range = $('#sedi')
if (range) {
  const STEPS = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 1500]
  const cv = $('#grow-grid'), out = $('#sedi-out b'), steady = $('.steady')
  const COLS = 50, ROWS = 30
  let shown = 1500, target = 1500, flashT
  const draw = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight
    if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr) }
    const c = cv.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h)
    const cw = w / COLS, ch = h / ROWS, s = Math.min(cw, ch) * 0.62
    const n = Math.round(shown)
    for (let i = 0; i < COLS * ROWS; i++) {
      const x = (i % COLS) * cw + (cw - s) / 2, y = Math.floor(i / COLS) * ch + (ch - s) / 2
      const on = i < n, fresh = on && i > n - 25 && shown < target
      c.fillStyle = fresh ? '#C8F1FD' : on ? 'rgba(92, 203, 240, .9)' : 'rgba(168, 230, 249, .1)'
      c.beginPath(); c.roundRect ? c.roundRect(x, y, s, s, s * 0.25) : c.rect(x, y, s, s); c.fill()
    }
  }
  const tick = () => {
    shown += (target - shown) * 0.12
    if (Math.abs(target - shown) < 0.5) shown = target
    out.textContent = Math.round(shown).toLocaleString(LOCALE)
    draw()
    if (shown !== target) requestAnimationFrame(tick)
  }
  const set = (i) => {
    target = STEPS[i]
    range.value = i
    range.style.setProperty('--fill', (i / (STEPS.length - 1)) * 100 + '%')
    range.setAttribute('aria-valuetext', target.toLocaleString(LOCALE) + (target === 1 ? TXT.sede : TXT.sedi))
    $('#sedi-out').lastChild.textContent = target === 1 ? TXT.sede : TXT.sedi
    steady.classList.add('flash'); clearTimeout(flashT); flashT = setTimeout(() => steady.classList.remove('flash'), 450)
    if (reduce) { shown = target; out.textContent = target.toLocaleString(LOCALE); draw() } else requestAnimationFrame(tick)
  }
  range.addEventListener('input', () => set(+range.value))
  new ResizeObserver(draw).observe(cv)
  draw()
  // La prima volta il cursore va da 1 a 1.500 da solo, per mostrare il gioco.
  new IntersectionObserver((e, o) => {
    if (!e[0].isIntersecting) return
    o.disconnect()
    if (reduce) return
    shown = 1; set(0)
    STEPS.forEach((_, i) => setTimeout(() => set(i), 500 + i * 320))
  }, { threshold: 0.45 }).observe(cv)
}

// Luce che segue il puntatore sulle sezioni scure.
$$('.spot').forEach((s) => {
  s.addEventListener('pointermove', (e) => { const r = s.getBoundingClientRect(); s.style.setProperty('--mx', e.clientX - r.left + 'px'); s.style.setProperty('--my', e.clientY - r.top + 'px'); s.style.setProperty('--spot', 1) })
  s.addEventListener('pointerleave', () => s.style.setProperty('--spot', 0))
})

window.addEventListener('load', () => {
  if (!window.gsap || reduce) return
  // Titoli delle sezioni: salgono dalla riga quando entrano.
  $$('main section:not(.hero):not(.phead) h2').forEach((h) => {
    const s = SplitText.create(h, { type: 'lines', mask: 'lines', linesClass: 'rise-line' })
    gsap.from(s.lines, { yPercent: 100, duration: 1, ease: 'expo.out', stagger: 0.08, scrollTrigger: { trigger: h, start: 'top 88%', once: true } })
  })
  // Bottoni principali magnetici.
  if (matchMedia('(hover: hover)').matches) $$('.b-cyan').forEach((b) => {
    const x = gsap.quickTo(b, 'x', { duration: 0.4, ease: 'power3.out' }), y = gsap.quickTo(b, 'y', { duration: 0.4, ease: 'power3.out' })
    b.addEventListener('pointermove', (e) => { const r = b.getBoundingClientRect(); x((e.clientX - r.left - r.width / 2) * 0.25); y((e.clientY - r.top - r.height / 2) * 0.3) })
    b.addEventListener('pointerleave', () => { x(0); y(0) })
  })
  ScrollTrigger.refresh()
})

// Sotto-menu: nelle pagine con i salti rapidi, compare in alto e segna la sezione in cui ti trovi.
const jump = $('.phead .jump')
if (jump) {
  const bar = document.createElement('nav'); bar.className = 'subnav'; bar.setAttribute('aria-label', 'In questa pagina')
  bar.innerHTML = '<ul>' + jump.innerHTML + '</ul>'; document.body.appendChild(bar)
  const links = $$('a', bar), targets = links.map((a) => $(a.getAttribute('href'))).filter(Boolean)
  new IntersectionObserver((e) => bar.classList.toggle('show', !e[0].isIntersecting), { rootMargin: '-80px 0px 0px 0px' }).observe($('.phead'))
  const io = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) links.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id)) }), { rootMargin: '-45% 0px -50% 0px' })
  targets.forEach((t) => io.observe(t))
}

// Schermate degli agenti e card dei formati: si inclinano leggermente seguendo il puntatore.
if (!reduce && matchMedia('(hover: hover)').matches) $$('.agent .screen, .format').forEach((el) => {
  el.classList.add('tilt')
  el.addEventListener('pointermove', (e) => { const r = el.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5; el.style.transform = `perspective(900px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-4px)` })
  el.addEventListener('pointerleave', () => { el.style.transform = '' })
})

window.addEventListener('load', () => {
  if (!window.gsap || reduce) return
  // Academy: la linea del percorso si disegna e accende le settimane.
  if ($('.journey-line')) {
    gsap.fromTo('.journey-line i', { scaleX: 0 }, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: '.journey-track', start: 'top 75%', end: 'bottom 55%', scrub: 0.5,
      onUpdate: (s) => $$('.journey-steps li').forEach((li, i) => li.classList.toggle('on', s.progress >= i / 3 - 0.02)) } })
  }
})

// Sigilli: ogni anello si disegna quando la sua voce entra nello schermo, uno dopo l'altro.
const seals = $$('.seals div')
if (seals.length) {
  if (reduce || !('IntersectionObserver' in window)) seals.forEach((s) => s.classList.add('on'))
  else {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return
      en.target.style.transitionDelay = `${seals.indexOf(en.target) % 2 * 0.15}s`
      en.target.classList.add('on')
      io.unobserve(en.target)
    }), { rootMargin: '0px 0px -12% 0px' })
    seals.forEach((s) => io.observe(s))
  }
}

// Academy: il nome dell'azienda sull'attestato lo scrive chi visita.
const certName = $('#cert-name')
certName?.addEventListener('focus', () => { if (certName.value === certName.dataset.default) certName.select() })

// Il sigillo si imprime sull'attestato come un timbro, una volta, quando l'attestato entra nello schermo.
$$('.cert-seal').forEach((seal) => {
  if (reduce || !('IntersectionObserver' in window)) return
  seal.classList.add('stamp-ready')
  const io = new IntersectionObserver(([en]) => { if (en.isIntersecting) { seal.classList.add('stamped'); io.disconnect() } }, { threshold: 0.6 })
  io.observe(seal)
})

// Programma dell'Academy: scelto il pubblico, restano accesi i formati e i temi che lo riguardano.
const audButtons = $$('.aud button')
audButtons.forEach((btn) => btn.addEventListener('click', () => {
  const aud = btn.dataset.aud
  audButtons.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)))
  $$('.prog-list li').forEach((li) => {
    const match = aud === 'tutti' || li.dataset.aud.split(' ').includes(aud)
    li.classList.toggle('off', !match)
    li.classList.toggle('hit', match && aud !== 'tutti')
  })
}))
