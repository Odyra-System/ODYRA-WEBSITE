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

// Menu su schermi piccoli: pannello a tutto schermo. Esc chiude, il fuoco resta dentro finché è aperto.
const nav = $('#nav')
const menu = $('#menu')
if (nav && menu) {
  const label = $('.top-menu-label', menu)
  const small = matchMedia('(max-width: 1240px)')
  const focusables = () => [menu, ...$$('a, button', nav)]
  const setOpen = (open, focusBack = false) => {
    nav.classList.toggle('open', open)
    menu.setAttribute('aria-expanded', String(open))
    document.documentElement.classList.toggle('menu-open', open)
    if (label) label.textContent = open ? menu.dataset.close : menu.dataset.open
    if (open) $('a', nav)?.focus({ preventScroll: true })
    else if (focusBack) menu.focus()
  }
  menu.addEventListener('click', () => setOpen(!nav.classList.contains('open')))
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false) })
  document.addEventListener('keydown', (e) => {
    if (!nav.classList.contains('open')) return
    if (e.key === 'Escape') { setOpen(false, true); return }
    if (e.key !== 'Tab') return
    const f = focusables(), first = f[0], last = f[f.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  })
  small.addEventListener('change', (m) => { if (!m.matches) setOpen(false) })
}

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

  // Passi numerati: le finestre di filo si accendono una dopo l'altra, una volta sola.
  $$('.steps').forEach((ol) => {
    gsap.fromTo($$(':scope > li', ol), { '--drawn': 0 }, { '--drawn': 1, duration: 0.9, ease: 'expo.out', stagger: 0.14, scrollTrigger: { trigger: ol, start: 'top 82%', once: true } })
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

// Il modulo contatti è gestito da odyra-app.js (invio al server, con ripiego sulla posta).
// Qui solo la preselezione da indirizzo: /contatti?interesse=academy sceglie la voce "academy".
for (const sel of document.querySelectorAll('select[data-param]')) {
  const v = new URLSearchParams(location.search).get(sel.dataset.param)
  if (v && [...sel.options].some(o => o.value === v)) sel.value = v
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

// Video: la copertina disegnata copre il player; al clic parte il video. I comandi stanno
// sotto l'immagine, così non coprono mai i sottotitoli già impressi nel video.
const VTXT = {
  it: { play: 'Riproduci', pause: 'Pausa', mute: 'Disattiva audio', unmute: 'Attiva audio', full: 'Schermo intero', seek: 'Posizione nel video' },
  es: { play: 'Reproducir', pause: 'Pausa', mute: 'Silenciar', unmute: 'Activar sonido', full: 'Pantalla completa', seek: 'Posición en el vídeo' },
}[LANG]
const ICON = {
  play: '<path d="M8 5.5v13l11-6.5z"/>',
  pause: '<path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/>',
  sound: '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15 9a4.2 4.2 0 0 1 0 6M17.5 6.5a7.7 7.7 0 0 1 0 11" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  muted: '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9.5l5 5m0-5l-5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  full: '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
}
const svg = (k) => `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">${ICON[k]}</svg>`
const clock = (s) => { s = Math.max(0, Math.floor(s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}` }
$$('.reel').forEach((reel) => {
  const video = $('video', reel), cover = $('.reel-play', reel)
  if (!video || !cover) return
  video.controls = false
  const total = $('.reel-dur', reel)?.textContent || '0:00'
  const bar = document.createElement('div')
  bar.className = 'reel-bar'
  bar.innerHTML = `<button type="button" class="rb-play" aria-label="${VTXT.play}">${svg('play')}</button>
    <input class="rb-seek" type="range" min="0" max="1000" value="0" step="1" aria-label="${VTXT.seek}">
    <span class="rb-time"><span class="rb-now">0:00</span> / ${total}</span>
    <button type="button" class="rb-mute" aria-label="${VTXT.mute}">${svg('sound')}</button>
    <button type="button" class="rb-full" aria-label="${VTXT.full}">${svg('full')}</button>`
  video.after(bar)
  const bPlay = $('.rb-play', bar), seek = $('.rb-seek', bar), now = $('.rb-now', bar), bMute = $('.rb-mute', bar), bFull = $('.rb-full', bar)
  const start = () => { reel.classList.add('playing'); video.play().catch(() => {}) }
  const toggle = () => (video.paused ? start() : video.pause())
  cover.addEventListener('click', start)
  video.addEventListener('click', toggle)
  bPlay.addEventListener('click', toggle)
  video.addEventListener('play', () => { bPlay.innerHTML = svg('pause'); bPlay.setAttribute('aria-label', VTXT.pause); reel.classList.add('playing') })
  video.addEventListener('pause', () => { bPlay.innerHTML = svg('play'); bPlay.setAttribute('aria-label', VTXT.play) })
  video.addEventListener('timeupdate', () => {
    now.textContent = clock(video.currentTime)
    if (video.duration) { seek.value = String(Math.round((video.currentTime / video.duration) * 1000)); seek.style.setProperty('--p', seek.value / 10 + '%') }
  })
  seek.addEventListener('input', () => {
    reel.classList.add('playing')
    if (video.duration) video.currentTime = (seek.value / 1000) * video.duration
    seek.style.setProperty('--p', seek.value / 10 + '%')
  })
  bMute.addEventListener('click', () => {
    video.muted = !video.muted
    bMute.innerHTML = svg(video.muted ? 'muted' : 'sound')
    bMute.setAttribute('aria-label', video.muted ? VTXT.unmute : VTXT.mute)
  })
  bFull.addEventListener('click', () => {
    if (document.fullscreenElement) return document.exitFullscreen()
    if (reel.requestFullscreen) reel.requestFullscreen().catch(() => {})
    else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen()
  })
})

// ───────── prezzi ─────────
// Listino: interruttore tra i due pubblici, scala degli scaglioni, calcolatore di margine.
// Tutte le cifre sono già nell'HTML (attributi data-w e data-r): qui si ricalcolano soltanto.
{
  const list = $('#listino')
  if (list) {
    const TIER_N = [20, 50, 100, 200]
    const TIER_T = ['20–49', '50–99', '100–199', '200+']
    const ACT = [69, 59, 49, 0]
    const ACT_REC = 99
    const tierOf = (n) => (n < 50 ? 0 : n < 100 ? 1 : n < 200 ? 2 : 3)
    // Euro all'italiana: punto per le migliaia (anche a quattro cifre), virgola per i decimali.
    const num = (v) => {
      const neg = v < 0, a = Math.abs(Math.round(v * 100) / 100)
      const [i, d] = a.toFixed(2).split('.')
      const int = i.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
      return (neg ? '−' : '') + int + (d === '00' ? '' : ',' + d)
    }
    const eur = (v) => num(v) + ' €'
    const ints = (s) => s.split(',').map(Number)
    const set = (el, text) => {
      if (!el || el.textContent === text) return
      el.textContent = text
      if (reduce) return
      el.classList.remove('pz-tick'); void el.offsetWidth; el.classList.add('pz-tick')
    }

    // Interruttore: due schede accessibili; senza JavaScript si vedono entrambi i pannelli.
    const tabs = $$('[role="tab"]', list)
    const partnerOnly = $$('[data-pz-aud="partner"]')
    const choose = (tab, focus = false, push = false) => {
      tabs.forEach((t) => {
        const on = t === tab
        t.setAttribute('aria-selected', String(on))
        t.tabIndex = on ? 0 : -1
        const panel = document.getElementById(t.getAttribute('aria-controls'))
        if (panel) panel.hidden = !on
      })
      const partner = tab.id === 'tab-partner'
      partnerOnly.forEach((s) => { s.hidden = !partner })
      if (focus) tab.focus()
      if (push) history.replaceState(null, '', partner ? '#per-partner' : '#per-aziende')
    }
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => choose(t, false, true))
      t.addEventListener('keydown', (e) => {
        const k = { ArrowRight: 1, ArrowLeft: -1, Home: -i, End: tabs.length - 1 - i }[e.key]
        if (k === undefined) return
        e.preventDefault()
        choose(tabs[(i + k + tabs.length) % tabs.length], true, true)
      })
    })
    if (tabs.length) {
      const fromHash = /aziend/.test(location.hash) ? $('#tab-aziende') : tabs[0]
      choose(fromHash || tabs[0])
      if (fromHash && fromHash !== tabs[0]) list.scrollIntoView()
    }

    // Scala degli scaglioni: aggiorna prezzo wholesale, margine ed esempio annuo di ogni taglia.
    const tierNote = $('[data-pz="tier-text"]', list), tierAct = $('[data-pz="act"]', list)
    const applyTier = (ti) => {
      $$('.pz-row', list).forEach((row) => {
        const w = ints(row.dataset.w)[ti], r = ints(row.dataset.r)[0], m = r - w
        set($('[data-pz="w"]', row), eur(w))
        set($('[data-pz="m"]', row), '+' + eur(m))
        set($('[data-pz="n"]', row), String(TIER_N[ti]))
        set($('[data-pz="y"]', row), eur(m * TIER_N[ti] * 12))
      })
      if (tierNote) tierNote.textContent = `Prezzi per ${TIER_T[ti]} licenze.`
      if (tierAct) set(tierAct, ACT[ti] ? eur(ACT[ti]) : 'gratis')
    }
    $$('input[name="pz-tier"]', list).forEach((r) => r.addEventListener('change', () => applyTier(Number(r.value))))
    const checked = $('input[name="pz-tier"]:checked', list)
    if (checked && checked.value !== '0') applyTier(Number(checked.value))

    // Calcolatore di margine.
    const form = $('#pz-form')
    if (form) {
      const inN = $('#pz-n'), inLic = $('#pz-lic'), inP = $('#pz-p'), hint = $('#pz-hint')
      const out = (k) => $(`[data-pc="${k}"]`)
      const opt = () => inLic.options[inLic.selectedIndex]
      const recText = () => { const [a, b] = ints(opt().dataset.r); return `Prezzo consigliato per questa licenza: ${a}–${b} €.` }
      const calc = () => {
        const o = opt()
        let n = Math.floor(Number(inN.value))
        const fewer = !(n >= 20)
        if (fewer) n = 20
        const ti = tierOf(n)
        const w = ints(o.dataset.w)[ti]
        let p = Number(String(inP.value).replace(',', '.'))
        if (inP.value === '' || !(p >= 0)) p = ints(o.dataset.r)[0]
        const m = p - w
        set(out('w'), eur(w))
        set(out('m'), eur(m))
        set(out('rev'), eur(p * n))
        set(out('mon'), eur(m * n))
        set(out('year'), eur(m * n * 12))
        set(out('act'), eur((ACT_REC - ACT[ti]) * n))
        set(out('actw'), ACT[ti] ? eur(ACT[ti]) : '0 € (gratis)')
        set(out('n'), String(n))
        set(out('lic'), o.textContent)
        set(out('tier'), TIER_T[ti])
        ;['m', 'mon', 'year'].forEach((k) => out(k)?.classList.toggle('neg', m < 0))
        let msg = recText(), warn = false
        if (fewer) { msg = 'L’impegno minimo dopo la beta è di 20 licenze: calcoliamo su 20 centri.'; warn = true }
        else if (m < 0) { msg = `Sotto il prezzo wholesale (${eur(w)}) il margine è negativo. ` + recText(); warn = true }
        hint.textContent = msg
        hint.classList.toggle('warn', warn)
      }
      inLic.addEventListener('change', () => { inP.value = ints(opt().dataset.r)[0]; calc() })
      inN.addEventListener('input', calc)
      inP.addEventListener('input', calc)
      form.addEventListener('submit', (e) => { e.preventDefault(); calc() })
      calc()
    }

    // La banconota del margine: guilloché disegnato come quello della home.
    const cv = $('.pz-note-guilloche')
    if (cv) {
      const draw = () => guilloche(cv, { phase: 0.9, rosette: { x: 0.2, y: 0.55, r: 0.5, lobes: 16, rings: 32, depth: 0.2, alpha: 0.3 }, waves: { lines: 20, amp: 0.035, freq: 2.5, alpha: 0.12, top: 0.1, bottom: 0.9 } })
      draw()
      new ResizeObserver(draw).observe(cv)
    }
  }
}
