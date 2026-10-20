// Menu su schermi piccoli.
const nav = document.getElementById('nav')
const burger = document.getElementById('burger')
burger?.addEventListener('click', () => {
  const open = nav.classList.toggle('open')
  burger.setAttribute('aria-expanded', String(open))
})
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && nav?.classList.contains('open')) { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); burger.focus() }
})

// Modulo contatti.
// Finché FORM_ENDPOINT è vuoto la richiesta si apre nel programma di posta, già scritta.
// Con un webhook (per esempio n8n) basta incollarne l'indirizzo: i dati partono in POST come JSON.
const FORM_ENDPOINT = ''
const FORM_EMAIL = 'team@odyrasystemautomation.it'
const form = document.getElementById('form-contatti')
if (form) {
  const msg = document.getElementById('form-msg')
  const q = new URLSearchParams(location.search).get('interesse')
  if (q && [...form.interesse.options].some((o) => o.value === q)) form.interesse.value = q
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    msg.classList.remove('err')
    if (!form.checkValidity()) { form.reportValidity(); return }
    const data = Object.fromEntries(new FormData(form))
    if (!FORM_ENDPOINT) {
      const body = Object.entries(data).filter(([k]) => k !== 'privacy').map(([k, v]) => `${k}: ${v}`).join('\n')
      location.href = `mailto:${FORM_EMAIL}?subject=${encodeURIComponent('Richiesta dal sito: ' + data.interesse)}&body=${encodeURIComponent(body)}`
      msg.textContent = form.dataset.mail
      return
    }
    try {
      const r = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...data, lingua: document.documentElement.lang }) })
      if (!r.ok) throw new Error(String(r.status))
      form.reset()
      msg.textContent = form.dataset.ok
    } catch {
      msg.classList.add('err')
      msg.textContent = form.dataset.err
    }
  })
}
