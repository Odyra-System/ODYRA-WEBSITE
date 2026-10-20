// Anteprima home Odyra. Tutto il testo è già nell'HTML: qui c'è solo movimento e interazione.
const $ = (s, r = document) => r.querySelector(s)
const $$ = (s, r = document) => [...r.querySelectorAll(s)]

// Menu su schermi piccoli.
const nav = $('#nav')
const menu = $('#menu')
menu?.addEventListener('click', () => menu.setAttribute('aria-expanded', String(nav.classList.toggle('open'))))

// Indice a linguette: ogni mestiere ha il suo volume.
const SECTORS = {
  salone: ['Codice del salone', 'Art. 3', 'Ordine tecnico', 'Colore, taglio, piega. Schiaritura, tonalizzante, piega. L’ordine lo impone il sistema, non la memoria di chi risponde.', 'In produzione con GoAgent, per oltre 1.500 saloni.'],
  dentale: ['Codice dello studio dentistico', 'Art. 1', 'Le regole dello studio', 'Ogni studio ha le sue regole su visite, sedute e spostamenti. Le scriviamo nel codice insieme a voi, prima di attivare l’agente.', 'Settore di competenza. Parliamone.'],
  officina: ['Codice dell’officina', 'Art. 1', 'Le regole dell’officina', 'Tagliandi, revisioni, tempi di lavorazione: ogni officina lavora a modo suo. Le sue regole entrano nel codice, non in un prompt.', 'Settore di competenza. Parliamone.'],
  hotel: ['Codice dell’hotel', 'Art. 1', 'Le regole della struttura', 'Richieste, disponibilità, politiche di cancellazione: l’agente le segue come le scrive la struttura.', 'Settore di competenza. Parliamone.'],
  veterinario: ['Codice della clinica veterinaria', 'Art. 1', 'Le regole della clinica', 'Visite, urgenze, richiami: le priorità della clinica diventano codice, e l’agente le rispetta sempre.', 'Settore di competenza. Parliamone.'],
}
const vol = ['#vol-title', '#vol-num', '#vol-head', '#vol-text', '#vol-note'].map((s) => $(s))
const tabs = $$('.tabs [role=tab]')
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches

function showSector(key) {
  tabs.forEach((t) => t.setAttribute('aria-selected', String(t.dataset.sector === key)))
  SECTORS[key].forEach((text, i) => {
    const el = vol[i]
    if (window.gsap && !reduce) {
      gsap.to(el, { duration: i === 3 ? 0.9 : 0.6, scrambleText: { text, chars: 'abcdefghilmnoprstuvz', speed: 0.6 }, ease: 'none' })
    } else el.textContent = text
  })
}
tabs.forEach((t, i) => {
  t.addEventListener('click', () => showSector(t.dataset.sector))
  t.addEventListener('keydown', (e) => {
    const d = e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : e.key === 'ArrowUp' || e.key === 'ArrowLeft' ? -1 : 0
    if (!d) return
    e.preventDefault()
    const n = tabs[(i + d + tabs.length) % tabs.length]
    n.focus(); showSector(n.dataset.sector)
  })
})

// Il marchio del partner: chi visita scrive il nome del suo software.
const brandInput = $('#brand-name')
const brandTargets = $$('[data-brand]')
brandInput?.addEventListener('input', () => {
  const name = brandInput.value.trim().slice(0, 24) || 'Il tuo gestionale'
  brandTargets.forEach((el) => { el.textContent = name })
})

// Cinque libri: si apre un dorso alla volta.
$$('.book-spine').forEach((spine) => spine.addEventListener('click', () => {
  $$('.book').forEach((b) => {
    const open = b === spine.parentElement
    b.classList.toggle('open', open)
    b.querySelector('.book-spine').setAttribute('aria-expanded', String(open))
  })
}))

// Movimento: una stampa a caldo all'apertura, il segnalibro, la pressa delle regole.
window.addEventListener('load', () => {
  if (!window.gsap) return
  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin)
  const mm = gsap.matchMedia()

  mm.add('(prefers-reduced-motion: no-preference)', () => {
    // Stampa a caldo: le lettere arrivano con un colpo di pressa, dal grande e sfocato al nitido.
    const split = SplitText.create('#cover-title', { type: 'words,chars', wordsClass: 'w' })
    const tl = gsap.timeline({ defaults: { ease: 'expo.out' } })
    tl.from(split.chars, { duration: 1.1, opacity: 0, scale: 1.35, filter: 'blur(10px)', stagger: { each: 0.028, from: 'start' } })
      .from('.cover-lead', { duration: 0.9, opacity: 0, y: 18 }, '-=0.7')
      .from('.cover .actions > *', { duration: 0.7, opacity: 0, y: 14, stagger: 0.08 }, '-=0.6')
      .from('.volume', { duration: 1, clipPath: 'inset(0 0 100% 0)' }, '-=0.9')
      .from('.tabs button', { duration: 0.7, x: 40, opacity: 0, stagger: 0.06 }, '-=0.8')

    // Il segnalibro scende con la lettura.
    gsap.to('.ribbon i', { scaleY: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.4 } })

    // I titoli impressi delle altre sezioni si imprimono quando arrivano.
    $$('main section:not(.cover) h2.stamp').forEach((h) => {
      gsap.from(h, { scrollTrigger: { trigger: h, start: 'top 85%', once: true }, duration: 1.2, ease: 'expo.out', opacity: 0, scale: 1.08, filter: 'blur(6px)', transformOrigin: 'left center' })
    })
    return () => split.revert()
  })

  // La pressa: su schermi larghi la sezione si ferma e ogni regola diventa codice, poi risposta.
  mm.add('(prefers-reduced-motion: no-preference) and (min-width: 901px)', () => {
    const press = $('.press')
    const rules = $$('.rule', press)
    const steps = $$('.press-steps li', press)
    const hdr = () => $('.spine').offsetHeight
    press.style.setProperty('--hdr', hdr() + 'px')
    press.classList.add('pinned')
    // Ogni riga di codice in un suo elemento, così l'effetto non perde gli a capo.
    const codes = rules.map((r) => $('code', r).textContent)
    rules.forEach((r, i) => { $('code', r).innerHTML = codes[i].split('\n').map((l) => `<span class="ln" style="padding-left:${l.length - l.trimStart().length}ch">${l.trim().replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`).join('') })
    const mark = (i) => steps.forEach((s, k) => s.classList.toggle('on', k === i))
    mark(0)
    gsap.set(rules.slice(1), { autoAlpha: 0 })
    const tl = gsap.timeline({ scrollTrigger: { trigger: press, pin: true, start: () => `top ${hdr()}px`, end: () => '+=' + rules.length * window.innerHeight * 0.9, scrub: 0.8, invalidateOnRefresh: true } })
    rules.forEach((r, i) => {
      const art = $('.r-art', r), lines = $$('.ln', r), bubbles = $$('.bubble', r)
      if (i > 0) {
        tl.to(rules[i - 1], { autoAlpha: 0, y: -40, duration: 0.6 })
          .set(r, { autoAlpha: 1 })
          .call(mark, [i - 1]).call(mark, [i])
      }
      tl.fromTo(art, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.6 })
      lines.forEach((ln, k) => {
        const text = ln.textContent
        tl.fromTo(ln, { scrambleText: { text: text.replace(/\S/g, '·') } }, { scrambleText: { text, chars: '{}[]<>=_01', revealDelay: 0 }, duration: 0.35, ease: 'none' }, k === 0 ? '<0.2' : '<0.12')
      })
      tl.fromTo(bubbles[0], { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.4 })
        .fromTo(bubbles[1], { autoAlpha: 0, y: 20, scale: 0.96 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.5 })
        .to({}, { duration: 0.6 })
    })
    return () => { press.classList.remove('pinned'); rules.forEach((r, i) => { $('code', r).textContent = codes[i] }) }
  })

  document.fonts?.ready.then(() => ScrollTrigger.refresh())
})
