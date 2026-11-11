/* Odyra: consenso cookie, misurazione, modulo contatti, demo dell'agente (voce e chat).
 * Caricato in <head> senza defer (è piccolo): imposta subito la classe "js" e il consenso predefinito,
 * prima che parta qualunque tag di misurazione. Il resto si attiva a DOM pronto.
 * Nessuno script in linea nelle pagine: la Content-Security-Policy non ammette 'unsafe-inline'. */
(function () {
  'use strict'
  var d = document, w = window, root = d.documentElement
  root.classList.add('js')

  var ADS_ID = 'AW-18360673034'
  var CLARITY_ID = 'xzwfgy25hs'
  var CONSENT_KEY = 'odyra-consent'
  var CONSENT_VERSION = 1
  var ATTR_KEY = 'odyra-attribution'
  var TEAM = 'team@odyrasystemautomation.it'
  var me = d.currentScript
  var LANG = root.lang === 'es' ? 'es' : 'it'

  var T = {
    it: {
      cTitle: 'Cookie e misurazione',
      cText: 'Usiamo cookie tecnici necessari al funzionamento del sito. Con il tuo consenso usiamo anche cookie di statistica, per capire come viene usato il sito, e di marketing, per misurare le nostre campagne. Puoi cambiare idea quando vuoi da «Preferenze cookie» in fondo alla pagina.',
      cPolicy: 'Cookie policy', cPolicyHref: '/cookie',
      cAccept: 'Accetta tutti', cReject: 'Solo necessari', cPrefs: 'Preferenze', cSave: 'Salva le preferenze',
      cNec: 'Necessari', cNecD: 'Funzionamento del sito e memoria delle tue scelte. Sempre attivi.',
      cStat: 'Statistica', cStatD: 'Mappe di calore e registrazioni anonime della navigazione, per migliorare le pagine.',
      cMkt: 'Marketing', cMktD: 'Misura delle conversioni delle campagne pubblicitarie.',
      cPrefsLink: 'Preferenze cookie',
      fOk: 'Richiesta inviata. Ti rispondiamo entro un giorno lavorativo.',
      fBad: 'Controlla i campi evidenziati e riprova.',
      fMany: 'Hai inviato troppe richieste. Riprova tra qualche minuto o scrivici a ' + TEAM + '.',
      fMail: 'Si è aperto il tuo programma di posta con la richiesta già scritta: premi Invia.',
      fSending: 'Invio in corso…', fSubject: 'Richiesta dal sito',
      vFab: 'Prova l’agente', vFabAria: 'Parla con l’agente AI di Odyra',
      vTitle: 'Parla con l’agente Odyra',
      vNote: 'Stai parlando con un’intelligenza artificiale. L’audio è elaborato in tempo reale per risponderti.',
      vPrivacy: 'Privacy', vPrivacyHref: '/privacy',
      vIdle: 'Pronto', vLoading: 'Preparazione…', vMicAsk: 'Consenti l’uso del microfono',
      vConnecting: 'Connessione…', vJoining: 'L’agente sta entrando…', vListening: 'Ti ascolto', vSpeaking: 'L’agente parla',
      vReconnecting: 'Riconnessione…', vEnded: 'Conversazione terminata', vError: 'Non riesco a collegarmi. Riprova tra poco.',
      vBusy: 'Troppe prove ravvicinate: riprova tra qualche minuto.', vOff: 'La demo vocale non è disponibile in questo momento.',
      vMicDenied: 'Microfono non disponibile. Consenti l’accesso al microfono dalle impostazioni del browser e riprova.',
      vMute: 'Disattiva il microfono', vUnmute: 'Riattiva il microfono', vMuted: 'Microfono disattivato',
      vEnd: 'Termina', vRetry: 'Riprova', vClose: 'Chiudi e termina la conversazione',
      vAudio: 'Tocca per attivare l’audio', vNav: 'L’agente ti ha portato a: ', vOpen: 'Apri la pagina',
      vNavFail: 'Non sono riuscito ad aprire la pagina qui.',
      aTitle: 'Prova l’agente Odyra', aSub: 'Assistente AI · a voce o per iscritto', aTabVoice: 'Parla', aTabChat: 'Scrivi',
      vStart: 'Inizia a parlare',
      vSoon: 'La demo a voce arriva a breve. Nel frattempo scrivi all’agente: stessa conoscenza, stesse risposte.',
      vSoonGo: 'Scrivi all’agente', vSoonNote: 'La demo a voce arriva a breve: intanto puoi scrivermi qui.',
      chLog: 'Conversazione con l’agente', chSuggLabel: 'Domande suggerite',
      chSugg: ['Quanto costa?', 'Come funziona per una software house?', 'Si integra col mio gestionale?', 'Prenota una call'],
      chPlaceholder: 'Scrivi una domanda…', chSend: 'Invia', chReset: 'Nuova conversazione',
      chOff: 'La chat non è disponibile in questo momento. Prenota una call: ti rispondiamo noi.', chBook: 'Prenota una call',
      chNote: 'Stai scrivendo a un’intelligenza artificiale: può sbagliare. Non inserire dati sensibili.',
      chYou: 'Tu: ', chAgent: 'Agente: ',
      chWelcome: 'Ciao, sono l’assistente AI di Odyra. Ti spiego come funzionano i nostri agenti vocali e WhatsApp, i prezzi e il modello white-label per le software house. Sei una software house o un’azienda?',
      chBusy: 'Troppi messaggi ravvicinati: riprova tra qualche minuto.', chErr: 'Non riesco a rispondere in questo momento.',
      chSee: 'Guarda la pagina'
    },
    es: {
      cTitle: 'Cookies y medición',
      cText: 'Usamos cookies técnicas necesarias para el funcionamiento del sitio. Con tu consentimiento usamos también cookies de estadística, para entender cómo se usa el sitio, y de marketing, para medir nuestras campañas. Puedes cambiar de opinión cuando quieras desde «Preferencias de cookies» al pie de la página.',
      cPolicy: 'Política de cookies', cPolicyHref: '/cookie',
      cAccept: 'Aceptar todas', cReject: 'Solo necesarias', cPrefs: 'Preferencias', cSave: 'Guardar preferencias',
      cNec: 'Necesarias', cNecD: 'Funcionamiento del sitio y memoria de tus elecciones. Siempre activas.',
      cStat: 'Estadística', cStatD: 'Mapas de calor y grabaciones anónimas de la navegación, para mejorar las páginas.',
      cMkt: 'Marketing', cMktD: 'Medición de las conversiones de las campañas publicitarias.',
      cPrefsLink: 'Preferencias de cookies',
      fOk: 'Solicitud enviada. Te respondemos en un día laborable.',
      fBad: 'Revisa los campos marcados y vuelve a intentarlo.',
      fMany: 'Has enviado demasiadas solicitudes. Vuelve a intentarlo en unos minutos o escríbenos a ' + TEAM + '.',
      fMail: 'Se ha abierto tu programa de correo con la solicitud ya escrita: pulsa Enviar.',
      fSending: 'Enviando…', fSubject: 'Solicitud desde la web',
      vFab: 'Prueba el agente', vFabAria: 'Habla con el agente IA de Odyra',
      vTitle: 'Habla con el agente Odyra',
      vNote: 'Estás hablando con una inteligencia artificial. El audio se procesa en tiempo real para responderte.',
      vPrivacy: 'Privacidad', vPrivacyHref: '/es/privacidad',
      vIdle: 'Listo', vLoading: 'Preparando…', vMicAsk: 'Permite el uso del micrófono',
      vConnecting: 'Conectando…', vJoining: 'El agente está entrando…', vListening: 'Te escucho', vSpeaking: 'El agente habla',
      vReconnecting: 'Reconectando…', vEnded: 'Conversación terminada', vError: 'No consigo conectar. Inténtalo de nuevo en un momento.',
      vBusy: 'Demasiados intentos seguidos: inténtalo dentro de unos minutos.', vOff: 'La demo de voz no está disponible en este momento.',
      vMicDenied: 'Micrófono no disponible. Permite el acceso al micrófono en los ajustes del navegador y vuelve a intentarlo.',
      vMute: 'Silenciar el micrófono', vUnmute: 'Activar el micrófono', vMuted: 'Micrófono silenciado',
      vEnd: 'Terminar', vRetry: 'Reintentar', vClose: 'Cerrar y terminar la conversación',
      vAudio: 'Toca para activar el audio', vNav: 'El agente te ha llevado a: ', vOpen: 'Abrir la página',
      vNavFail: 'No he podido abrir la página aquí.',
      aTitle: 'Prueba el agente Odyra', aSub: 'Asistente IA · por voz o por escrito', aTabVoice: 'Hablar', aTabChat: 'Escribir',
      vStart: 'Empezar a hablar',
      vSoon: 'La demo por voz llega muy pronto. Mientras tanto, escribe al agente: mismo conocimiento, mismas respuestas.',
      vSoonGo: 'Escribir al agente', vSoonNote: 'La demo por voz llega muy pronto: mientras tanto puedes escribirme aquí.',
      chLog: 'Conversación con el agente', chSuggLabel: 'Preguntas sugeridas',
      chSugg: ['¿Cuánto cuesta?', '¿Cómo funciona para una empresa de software?', '¿Se integra con mi software de gestión?', 'Reservar una llamada'],
      chPlaceholder: 'Escribe una pregunta…', chSend: 'Enviar', chReset: 'Nueva conversación',
      chOff: 'El chat no está disponible en este momento. Reserva una llamada y te respondemos.', chBook: 'Reservar una llamada',
      chNote: 'Estás escribiendo a una inteligencia artificial: puede equivocarse. No incluyas datos sensibles.',
      chYou: 'Tú: ', chAgent: 'Agente: ',
      chWelcome: 'Hola, soy el asistente IA de Odyra. Te explico cómo funcionan nuestros agentes de voz y WhatsApp, los precios y el modelo white-label para empresas de software. ¿Eres una empresa de software o una empresa con sedes?',
      chBusy: 'Demasiados mensajes seguidos: inténtalo dentro de unos minutos.', chErr: 'No puedo responder en este momento.',
      chSee: 'Ver la página'
    }
  }[LANG]

  function store(kind) { try { return w[kind] } catch (e) { return null } }
  function getJSON(kind, key) { try { return JSON.parse(store(kind).getItem(key) || 'null') } catch (e) { return null } }
  function setJSON(kind, key, v) { try { store(kind).setItem(key, JSON.stringify(v)) } catch (e) { /* navigazione privata */ } }

  // ───────── Google: consenso predefinito negato, poi il tag ─────────
  w.dataLayer = w.dataLayer || []
  function gtag() { w.dataLayer.push(arguments) }
  w.gtag = w.gtag || gtag
  var saved = getJSON('localStorage', CONSENT_KEY)
  if (!saved || saved.v !== CONSENT_VERSION) saved = null
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied',
    functionality_storage: 'granted', security_storage: 'granted', wait_for_update: 500
  })
  gtag('set', 'ads_data_redaction', true)
  gtag('set', 'url_passthrough', true)
  if (saved) gtag('consent', 'update', consentState(saved))
  gtag('js', new Date())
  gtag('config', ADS_ID)
  var gs = d.createElement('script')
  gs.async = true
  gs.src = 'https://www.googletagmanager.com/gtag/js?id=' + ADS_ID
  ;(d.head || root).appendChild(gs)

  function consentState(c) {
    var m = c.marketing ? 'granted' : 'denied'
    return { ad_storage: m, ad_user_data: m, ad_personalization: m, analytics_storage: c.analytics ? 'granted' : 'denied' }
  }
  function track(name, params) { try { w.gtag('event', name, params || {}) } catch (e) { /* mai bloccare la pagina */ } }

  // ───────── Clarity: solo con consenso alla statistica ─────────
  function loadClarity() {
    if (d.getElementById('clarity-tag')) { try { w.clarity('consent') } catch (e) { } return }
    w.clarity = w.clarity || function () { (w.clarity.q = w.clarity.q || []).push(arguments) }
    var s = d.createElement('script')
    s.id = 'clarity-tag'; s.async = true; s.src = 'https://www.clarity.ms/tag/' + CLARITY_ID
    d.head.appendChild(s)
    try { w.clarity('consent') } catch (e) { }
  }
  if (saved && saved.analytics) loadClarity()

  function decide(c) {
    var wasStat = saved && saved.analytics
    saved = { v: CONSENT_VERSION, analytics: !!c.analytics, marketing: !!c.marketing, ts: new Date().toISOString() }
    setJSON('localStorage', CONSENT_KEY, saved)
    gtag('consent', 'update', consentState(saved))
    if (saved.analytics) loadClarity()
    else if (wasStat) {
      try { w.clarity('consent', false) } catch (e) { }
      // Il tag di statistica era già caricato: si ferma davvero solo ricaricando la pagina.
      if (d.getElementById('clarity-tag')) setTimeout(function () { location.reload() }, 300)
    }
  }

  // ───────── Attribuzione campagne (sessionStorage, prima visita della sessione) ─────────
  var ATTR = ['gclid', 'wbraid', 'gbraid', 'msclkid', 'campaignid', 'adgroupid', 'keyword', 'matchtype', 'network', 'device',
    'creative', 'placement', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
  function san(v) { return String(v).replace(/[\r\n]+/g, ' ').trim().slice(0, 120) }
  ;(function captureAttribution() {
    var p = new URLSearchParams(location.search), fresh = {}, n = 0
    ATTR.forEach(function (k) { var v = p.get(k); if (v) { fresh[k] = san(v); n++ } })
    if (!n) return
    fresh.landing_page = san(location.pathname)
    // Solo origine e percorso del sito di provenienza: la query di un altro sito può contenere dati personali.
    if (d.referrer) { try { var ru = new URL(d.referrer); fresh.referrer = san(ru.origin + ru.pathname) } catch (x) { } }
    fresh.first_seen_at = new Date().toISOString()
    setJSON('sessionStorage', ATTR_KEY, fresh)
  })()
  function attribution() {
    var a = getJSON('sessionStorage', ATTR_KEY), out = {}
    if (!a || typeof a !== 'object') return out
    // Solo chiavi note e stringhe corte: lo storage può essere stato scritto da altri script della stessa origine.
    ATTR.concat(['landing_page', 'referrer', 'first_seen_at']).forEach(function (k) { if (typeof a[k] === 'string') out[k] = san(a[k]) })
    return out
  }
  function sameOriginPath(u) {
    // Percorso dello stesso sito o null. Con URL() anche "/\evil.com" e "//evil.com" risultano di un'altra origine.
    try { var x = new URL(u, location.href); return x.origin === location.origin ? x.pathname + x.search + x.hash : null } catch (e) { return null }
  }

  // ───────── utilità DOM ─────────
  function el(tag, attrs, kids) {
    var n = d.createElement(tag)
    for (var k in attrs || {}) {
      if (k === 'text') n.textContent = attrs[k]
      else if (k === 'hidden') n.hidden = !!attrs[k]
      else n.setAttribute(k, attrs[k])
    }
    ;(kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? d.createTextNode(c) : c) })
    return n
  }
  var ICON = {
    mic: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 15a3.5 3.5 0 0 0 3.5-3.5v-5a3.5 3.5 0 1 0-7 0v5A3.5 3.5 0 0 0 12 15Zm6-3.5a1 1 0 1 0-2 0 4 4 0 0 1-8 0 1 1 0 1 0-2 0 6 6 0 0 0 5 5.91V20H8.5a1 1 0 1 0 0 2h7a1 1 0 1 0 0-2H13v-2.59a6 6 0 0 0 5-5.91Z"/></svg>',
    micOff: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M3.7 2.3a1 1 0 0 0-1.4 1.4l18 18a1 1 0 0 0 1.4-1.4l-4.1-4.1A6 6 0 0 0 18 11.5a1 1 0 1 0-2 0c0 .7-.2 1.4-.5 2l-1.2-1.2c.1-.3.2-.5.2-.8v-5a3.5 3.5 0 0 0-6.9-.8L3.7 2.3ZM8.5 11.4v.1a3.5 3.5 0 0 0 4.6 3.3l-4.6-4.6v1.2ZM6 11.5a1 1 0 1 0-2 0 6 6 0 0 0 7 5.91V20H8.5a1 1 0 1 0 0 2h7a1 1 0 1 0 0-2H13v-2.1l-1.9-1.9A4 4 0 0 1 6 11.5Z"/></svg>',
    chat: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false"><path fill="currentColor" d="M5 4h14a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-6.6l-4.2 3.3A1 1 0 0 1 6.6 20.5V18H5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Zm3 6.5a1.25 1.25 0 1 0 0 2.5 1.25 1.25 0 0 0 0-2.5Zm4 0a1.25 1.25 0 1 0 0 2.5 1.25 1.25 0 0 0 0-2.5Zm4 0a1.25 1.25 0 1 0 0 2.5 1.25 1.25 0 0 0 0-2.5Z"/></svg>',
    send: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M3.4 20.4a1 1 0 0 1-1.3-1.2L4.3 12 2.1 4.8a1 1 0 0 1 1.3-1.2l18 7.5a1 1 0 0 1 0 1.8l-18 7.5ZM6 13l-1.4 4.7L17.4 12 4.6 6.3 6 11h6a1 1 0 1 1 0 2H6Z"/></svg>',
    close: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><path fill="currentColor" d="M6.7 5.3a1 1 0 0 0-1.4 1.4L10.6 12l-5.3 5.3a1 1 0 1 0 1.4 1.4l5.3-5.3 5.3 5.3a1 1 0 0 0 1.4-1.4L13.4 12l5.3-5.3a1 1 0 0 0-1.4-1.4L12 10.6 6.7 5.3Z"/></svg>'
  }

  function ready(fn) { if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', fn); else fn() }

  ready(function () {
    var body = d.body
    var live = el('p', { 'class': 'oa-sr', role: 'status', 'aria-live': 'polite' })
    body.appendChild(live)
    function announce(s) { live.textContent = ''; setTimeout(function () { live.textContent = s }, 50) }

    // ───────── banner cookie ─────────
    var banner, prefs, boxStat, boxMkt, bSave, bPrefs
    function buildBanner() {
      boxStat = el('input', { type: 'checkbox', id: 'oc-stat' })
      boxMkt = el('input', { type: 'checkbox', id: 'oc-mkt' })
      var row = function (id, box, title, desc, fixed) {
        var input = box || el('input', { type: 'checkbox', id: id, checked: 'checked', disabled: 'disabled' })
        return el('div', { 'class': 'oc-row' + (fixed ? ' oc-fixed' : '') }, [input,
          el('label', { 'for': input.id }, [el('b', { text: title }), el('span', { text: desc })])])
      }
      prefs = el('fieldset', { 'class': 'oc-prefs', hidden: true }, [
        el('legend', { 'class': 'oa-sr', text: T.cPrefs }),
        row('oc-nec', null, T.cNec, T.cNecD, true), row('oc-stat', boxStat, T.cStat, T.cStatD), row('oc-mkt', boxMkt, T.cMkt, T.cMktD)])
      var bAccept = el('button', { type: 'button', 'class': 'oc-b', text: T.cAccept })
      var bReject = el('button', { type: 'button', 'class': 'oc-b', text: T.cReject })
      bPrefs = el('button', { type: 'button', 'class': 'oc-b oc-b-line', 'aria-expanded': 'false', text: T.cPrefs })
      bSave = el('button', { type: 'button', 'class': 'oc-b oc-b-line', hidden: true, text: T.cSave })
      var title = el('h2', { id: 'oc-title', tabindex: '-1', text: T.cTitle })
      var text = el('p', { id: 'oc-text' }, [T.cText + ' ', el('a', { href: T.cPolicyHref, text: T.cPolicy }), '.'])
      banner = el('section', { 'class': 'oc-banner', role: 'dialog', 'aria-modal': 'false', 'aria-labelledby': 'oc-title', 'aria-describedby': 'oc-text', hidden: true },
        [el('div', { 'class': 'oc-in' }, [title, text, prefs, el('div', { 'class': 'oc-actions' }, [bPrefs, bSave, bReject, bAccept])])])
      bAccept.addEventListener('click', function () { close({ analytics: true, marketing: true }) })
      bReject.addEventListener('click', function () { close({ analytics: false, marketing: false }) })
      bSave.addEventListener('click', function () { close({ analytics: boxStat.checked, marketing: boxMkt.checked }) })
      bPrefs.addEventListener('click', function () { showPrefs(true) })
      banner.addEventListener('keydown', function (e) { if (e.key === 'Escape' && saved) close(null) })
      body.appendChild(banner)
    }
    var opener = null
    function showPrefs(on) {
      prefs.hidden = !on; bSave.hidden = !on; bPrefs.hidden = on
      bPrefs.setAttribute('aria-expanded', String(on))
      if (on) boxStat.focus()
    }
    function openBanner(withPrefs, focus) {
      if (!banner) buildBanner()
      boxStat.checked = !!(saved && saved.analytics); boxMkt.checked = !!(saved && saved.marketing)
      banner.hidden = false
      root.classList.add('oc-open')
      showPrefs(!!withPrefs)
      if (focus && !withPrefs) banner.querySelector('#oc-title').focus()
    }
    function close(choice) {
      if (choice) decide(choice)
      banner.hidden = true
      root.classList.remove('oc-open')
      if (opener && d.contains(opener)) opener.focus()
      opener = null
    }
    d.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('[data-cookie-prefs]')
      if (!t) return
      e.preventDefault(); opener = t; openBanner(true, true)
    })
    if (!saved) openBanner(false, false)
    // Rete di sicurezza: se la pagina non ha il collegamento alle preferenze, lo aggiunge in fondo al piede.
    if (!d.querySelector('[data-cookie-prefs]')) {
      var foot = d.querySelector('footer .foot-legal') || d.querySelector('footer')
      if (foot) foot.appendChild(el('button', { type: 'button', 'class': 'foot-link', 'data-cookie-prefs': '', text: T.cPrefsLink }))
    }

    // ───────── clic verso contatti e demo ─────────
    d.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]')
      if (!a || a.hasAttribute('data-voice-demo') || a.hasAttribute('data-chat-demo')) return  // i pulsanti della demo li conta il loro gestore
      var u
      try { u = new URL(a.href, location.href) } catch (x) { return }
      if (u.origin === location.origin && /^\/(es\/)?(contatti|contacto|demo|prenota)(\/|$)/.test(u.pathname))
        track('click_demo', { link_url: u.pathname, link_text: (a.textContent || '').trim().slice(0, 80) })
    })

    // ───────── modulo contatti ─────────
    function field(f, names) {
      for (var i = 0; i < names.length; i++) {
        var x = f.elements[names[i]]
        if (!x) continue
        if (x instanceof RadioNodeList || (x.length && !x.tagName)) {
          var v = x.value
          if (v) return v
          continue
        }
        if (x.type === 'checkbox') return x.checked
        return (x.value || '').trim()
      }
      return ''
    }
    function statusEl(f) { return f.querySelector('.form-status, .form-msg, [role=status]') }
    d.addEventListener('submit', function (e) {
      var f = e.target
      if (!f.matches || !f.matches('form[data-lead-form], form#form-contatti')) return
      // Il nostro gestore sostituisce eventuali gestori più vecchi sullo stesso modulo.
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation()
      if (f.getAttribute('aria-busy') === 'true') return
      var st = statusEl(f)
      var say = function (s, err) { if (st) { st.textContent = s; st.classList.toggle('err', !!err) } }
      if (!f.checkValidity()) { f.reportValidity(); say(T.fBad, true); return }
      var data = {
        name: field(f, ['name', 'nome']), company: field(f, ['company', 'azienda']), email: field(f, ['email']),
        phone: field(f, ['phone', 'telefono']), need: field(f, ['need', 'interesse', 'esigenza']),
        message: field(f, ['message', 'messaggio']), privacy: field(f, ['privacy']) === true,
        website: field(f, ['website']), source: f.getAttribute('data-source') || f.id || 'modulo',
        page: location.pathname, attribution: attribution()
      }
      var btn = f.querySelector('[type=submit]')
      f.setAttribute('aria-busy', 'true'); if (btn) btn.disabled = true
      say(T.fSending)
      var done = function () { f.removeAttribute('aria-busy'); if (btn) btn.disabled = false }
      var mail = function () {
        var lines = [['Nome', data.name], ['Azienda', data.company], ['E-mail', data.email], ['Telefono', data.phone],
          ['Esigenza', data.need], ['Messaggio', data.message]].filter(function (p) { return p[1] }).map(function (p) { return p[0] + ': ' + p[1] })
        var a = attribution(), ak = Object.keys(a)
        if (ak.length) lines.push('', '--- Provenienza ---')
        ak.forEach(function (k) { lines.push('- ' + k + ': ' + a[k]) })
        location.href = 'mailto:' + TEAM + '?subject=' + encodeURIComponent(T.fSubject + (data.need ? ': ' + data.need : '')) +
          '&body=' + encodeURIComponent(lines.join('\n'))
        say(f.getAttribute('data-mail') || T.fMail)
      }
      fetch('/api/contatto', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), credentials: 'same-origin' })
        .then(function (r) {
          done()
          if (r.ok) {
            track('generate_lead', { form: data.source })
            var to = sameOriginPath(f.getAttribute('data-redirect') || '')
            if (to) { setTimeout(function () { location.href = to }, 250); return }
            f.reset(); say(f.getAttribute('data-ok') || T.fOk)
          } else if (r.status === 400 || r.status === 413 || r.status === 415) say(T.fBad, true)
          else if (r.status === 429) say(T.fMany, true)
          else mail()
        }, function () { done(); mail() })
    }, true)

    // ───────── "Prova l'agente": pannello con due schede, Parla (voce) e Scrivi (chat) ─────────
    // Pagine che l'agente (voce o chat) può aprire: stessa whitelist di agente/pagine.json.
    var PAGES = {
      home: { it: '/', es: '/es/' }, prezzi: { it: '/prezzi' }, partner: { it: '/partner', es: '/es/socios' },
      prenota: { it: '/prenota' }, casi: { it: '/lavori', es: '/es/casos' }, boss: { it: '/case/boss-italia' },
      tecnologie: { it: '/tecnologie', es: '/es/plataforma' }, contatti: { it: '/contatti', es: '/es/contacto' }
    }
    var PATH_KEY = {}
    Object.keys(PAGES).forEach(function (k) { PATH_KEY[PAGES[k].it] = k; if (PAGES[k].es) PATH_KEY[PAGES[k].es] = k })
    PATH_KEY['/#contatti'] = 'contatti'; PATH_KEY['/es'] = 'home'  // compatibilità con l'agente vocale precedente
    function pagePath(k) { var p = PAGES[k]; return (LANG === 'es' && p.es) || p.it }
    // Percorso o chiave → percorso ammesso nella lingua della pagina, oppure null.
    function allowedPath(p) {
      if (typeof p !== 'string') return null
      if (Object.prototype.hasOwnProperty.call(PAGES, p)) return pagePath(p)
      var q = p.length > 1 && p !== '/es/' ? p.replace(/\/+$/, '') : p
      if (Object.prototype.hasOwnProperty.call(PATH_KEY, q)) return pagePath(PATH_KEY[q])
      return null
    }

    var fab = el('button', { type: 'button', 'class': 'ov-fab', 'aria-haspopup': 'dialog', 'aria-label': T.vFabAria })
    fab.innerHTML = ICON.mic
    fab.appendChild(el('span', { 'class': 'ov-fab-t', 'aria-hidden': 'true', text: T.vFab }))
    body.appendChild(fab)

    // Stato dei servizi (voce e chat), chiesto una volta e tenuto 5 minuti nella sessione.
    var HEALTH = null
    function health() {
      if (HEALTH) return Promise.resolve(HEALTH)
      var c = getJSON('sessionStorage', 'odyra-health')
      if (c && typeof c.t === 'number' && Date.now() - c.t < 300000) { HEALTH = c; applyHealth(); return Promise.resolve(c) }
      var timeout = new Promise(function (res) { setTimeout(function () { res(null) }, 2000) })
      var req = fetch('/api/salute', { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.json() : null }, function () { return null })
      return Promise.race([req, timeout]).then(function (h) {
        if (!h || typeof h !== 'object') return { voce: true, chat: true }  // ignoto: si prova, gli errori si gestiscono dopo
        HEALTH = { t: Date.now(), voce: h.voce !== false, chat: h.chat !== false }
        setJSON('sessionStorage', 'odyra-health', HEALTH)
        applyHealth()
        return HEALTH
      })
    }
    function applyHealth() {
      if (!HEALTH) return
      if (!HEALTH.voce && HEALTH.chat) { fab.innerHTML = ICON.chat; fab.appendChild(el('span', { 'class': 'ov-fab-t', 'aria-hidden': 'true', text: T.vFab })) }
      if (panel) refreshAvailability()
    }
    var idle = w.requestIdleCallback || function (fn) { return setTimeout(fn, 1500) }
    setTimeout(function () { idle(function () { health() }) }, 1200)

    var panel, stEl, orb, bMute, bEnd, bRetry, bStart, bAudio, navP, video, offP, tabV, tabC, paneV, paneC
    var room = null, LK = null, state = 'idle', muted = false, lastOpener = null, session = 0, tab = 'voice'
    function buildPanel() {
      var title = el('h2', { id: 'ov-title', text: T.aTitle })
      var bClose = el('button', { type: 'button', 'class': 'ov-x', 'aria-label': T.vClose }); bClose.innerHTML = ICON.close
      var avatar = el('span', { 'class': 'ov-avatar', 'aria-hidden': 'true' }, [el('span')])
      tabV = el('button', { type: 'button', role: 'tab', id: 'ov-tab-voice', 'aria-controls': 'ov-pane-voice', 'class': 'ov-tab' })
      tabV.innerHTML = ICON.mic; tabV.appendChild(el('span', { text: T.aTabVoice }))
      tabC = el('button', { type: 'button', role: 'tab', id: 'ov-tab-chat', 'aria-controls': 'ov-pane-chat', 'class': 'ov-tab' })
      tabC.innerHTML = ICON.chat; tabC.appendChild(el('span', { text: T.aTabChat }))
      var tabs = el('div', { role: 'tablist', 'class': 'ov-tabs', 'aria-label': T.aTitle }, [tabV, tabC])

      // scheda Parla: la demo vocale di sempre
      stEl = el('p', { 'class': 'ov-status', role: 'status', 'aria-live': 'polite', text: T.vIdle })
      orb = el('div', { 'class': 'ov-orb', 'aria-hidden': 'true' }, [el('span'), el('span'), el('span')])
      video = el('video', { 'class': 'ov-video', playsinline: '', muted: '', autoplay: '', hidden: true })
      video.muted = true
      bAudio = el('button', { type: 'button', 'class': 'ov-b ov-b-line', hidden: true, text: T.vAudio })
      navP = el('p', { 'class': 'ov-nav', hidden: true })
      offP = el('div', { 'class': 'ov-off', hidden: true }, [el('p', { text: T.vSoon }),
        el('button', { type: 'button', 'class': 'ov-b', 'data-go-chat': '', text: T.vSoonGo })])
      bStart = el('button', { type: 'button', 'class': 'ov-b ov-start', hidden: true })
      bStart.innerHTML = ICON.mic; bStart.appendChild(d.createTextNode(' ' + T.vStart))
      bMute = el('button', { type: 'button', 'class': 'ov-b ov-b-line ov-mute', 'aria-pressed': 'false', disabled: 'disabled', hidden: true })
      bEnd = el('button', { type: 'button', 'class': 'ov-b ov-end', hidden: true, text: T.vEnd })
      bRetry = el('button', { type: 'button', 'class': 'ov-b', hidden: true, text: T.vRetry })
      paneV = el('div', { role: 'tabpanel', id: 'ov-pane-voice', 'aria-labelledby': 'ov-tab-voice', 'class': 'ov-pane ov-pane-voice', tabindex: '-1' }, [
        el('p', { 'class': 'ov-note' }, [T.vNote + ' ', el('a', { href: T.vPrivacyHref, text: T.vPrivacy })]),
        el('div', { 'class': 'ov-stage' }, [orb, video]), stEl, offP, bAudio, navP,
        el('div', { 'class': 'ov-actions' }, [bStart, bMute, bRetry, bEnd])])
      paneC = el('div', { role: 'tabpanel', id: 'ov-pane-chat', 'aria-labelledby': 'ov-tab-chat', 'class': 'ov-pane ov-pane-chat', hidden: true }, buildChat())

      panel = el('section', { 'class': 'ov-panel', role: 'dialog', 'aria-modal': 'false', 'aria-labelledby': 'ov-title', hidden: true }, [
        el('header', { 'class': 'ov-h' }, [avatar, el('div', { 'class': 'ov-ht' }, [title, el('p', { 'class': 'ov-sub', text: T.aSub })]), bClose]),
        tabs, paneV, paneC])
      setMuteLabel()
      bClose.addEventListener('click', closePanel)
      bEnd.addEventListener('click', function () { hangup(T.vEnded) })
      bRetry.addEventListener('click', start)
      bStart.addEventListener('click', start)
      bMute.addEventListener('click', toggleMute)
      offP.querySelector('[data-go-chat]').addEventListener('click', function () { selectTab('chat', true) })
      bAudio.addEventListener('click', function () { if (room) room.startAudio().then(function () { bAudio.hidden = room.canPlaybackAudio }, function () { }) })
      ;[tabV, tabC].forEach(function (t) {
        t.addEventListener('click', function () { selectTab(t === tabV ? 'voice' : 'chat', true) })
        t.addEventListener('keydown', function (e) {
          if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'Home' || e.key === 'End') {
            e.preventDefault(); var next = (e.key === 'Home') ? 'voice' : (e.key === 'End') ? 'chat' : (tab === 'voice' ? 'chat' : 'voice')
            selectTab(next, false); (next === 'voice' ? tabV : tabC).focus()
          }
        })
      })
      panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); closePanel() } })
      body.appendChild(panel)
      setState('idle')
      refreshAvailability()
    }
    function refreshAvailability() {
      var vOff = !!(HEALTH && !HEALTH.voce), cOff = !!(HEALTH && !HEALTH.chat)
      offP.hidden = !vOff
      offP.querySelector('[data-go-chat]').hidden = cOff
      panel.classList.toggle('ov-voice-off', vOff)
      if (!room && state === 'idle') setState('idle')
      chatOff(cOff)
    }
    function selectTab(t, focus, opts) {
      opts = opts || {}
      tab = t
      setJSON('sessionStorage', 'odyra-agent-tab', t)
      var v = t === 'voice'
      tabV.setAttribute('aria-selected', String(v)); tabC.setAttribute('aria-selected', String(!v))
      tabV.tabIndex = v ? 0 : -1; tabC.tabIndex = v ? -1 : 0
      paneV.hidden = !v; paneC.hidden = v
      panel.setAttribute('data-tab', t)
      root.classList.toggle('ov-chat-open', !v)
      if (!v) {
        if (room || state === 'connecting' || state === 'loading' || state === 'mic') hangup(T.vEnded)
        openChat(focus, opts)
      } else {
        if (opts.autostart && !(HEALTH && !HEALTH.voce) && !room && /^(idle|ended|error|denied)$/.test(state)) start()
        else if (focus) (bStart.hidden ? paneV : bStart).focus()
      }
    }
    function openPanel(t, from, opts) {
      if (!panel) buildPanel()
      lastOpener = from || fab
      panel.hidden = false
      root.classList.add('ov-open')
      fab.setAttribute('aria-expanded', 'true')
      selectTab(t, true, opts)
      if (t === 'voice' && !(opts && opts.autostart)) panel.querySelector('.ov-x').focus()
    }
    function closePanel() {
      if (room || state === 'connecting' || state === 'loading' || state === 'mic') hangup()
      if (!panel) return
      panel.hidden = true
      root.classList.remove('ov-open', 'ov-chat-open')
      fab.setAttribute('aria-expanded', 'false')
      if (lastOpener && d.contains(lastOpener) && lastOpener !== fab) lastOpener.focus(); else fab.focus()
    }
    function setMuteLabel() {
      bMute.innerHTML = muted ? ICON.micOff : ICON.mic
      bMute.setAttribute('aria-label', muted ? T.vUnmute : T.vMute)
      bMute.setAttribute('aria-pressed', String(muted))
    }
    function setState(s, msg) {
      state = s
      var vOff = !!(HEALTH && !HEALTH.voce)
      paneV.setAttribute('data-state', vOff && s === 'idle' ? 'off' : s)
      stEl.textContent = vOff && s === 'idle' ? '' : (msg || {
        idle: T.vIdle, loading: T.vLoading, mic: T.vMicAsk, connecting: T.vConnecting, joining: T.vJoining, listening: muted ? T.vMuted : T.vListening,
        speaking: T.vSpeaking, reconnecting: T.vReconnecting, ended: T.vEnded, error: T.vError, denied: T.vMicDenied
      }[s] || '')
      var active = s === 'joining' || s === 'listening' || s === 'speaking' || s === 'reconnecting'
      var busy = active || s === 'connecting' || s === 'loading' || s === 'mic'
      bMute.disabled = !active; bMute.hidden = !busy
      bStart.hidden = !(s === 'idle') || vOff
      bRetry.hidden = !(s === 'error' || s === 'denied' || s === 'ended') || vOff
      bEnd.hidden = !busy
      root.classList.toggle('ov-live', active)
    }
    function loadLib() {
      if (w.LivekitClient) return Promise.resolve(w.LivekitClient)
      return new Promise(function (res, rej) {
        var s = d.createElement('script')
        s.src = '/assets/vendor/rtc-client.min.js?v=' + ((me && me.getAttribute('data-v')) || '1')
        s.async = true
        s.onload = function () { w.LivekitClient ? res(w.LivekitClient) : rej(new Error('lib')) }
        s.onerror = function () { s.remove(); rej(new Error('lib')) }
        d.head.appendChild(s)
      })
    }
    function hangup(msg) {
      session++
      var r = room; room = null
      if (r) { try { r.disconnect() } catch (x) { } }
      d.querySelectorAll('audio.ov-audio').forEach(function (a) { try { a.pause(); a.srcObject = null; a.remove() } catch (x) { } })
      if (video) { video.hidden = true; try { video.srcObject = null } catch (x) { } }
      if (orb) orb.hidden = false
      if (bAudio) bAudio.hidden = true
      muted = false; if (bMute) setMuteLabel()
      if (panel) setState(msg ? 'ended' : 'idle', msg)
    }
    function fail(kind) { hangup(); setState(kind === 'denied' ? 'denied' : 'error', kind === 'busy' ? T.vBusy : kind === 'off' ? T.vOff : undefined) }
    function start() {
      var my = ++session
      navP.hidden = true
      setState('loading')
      track('voice_demo_start', { page: location.pathname, language: LANG })
      var md = navigator.mediaDevices
      if (!md || !md.getUserMedia) return fail('denied')
      setState('mic')
      // Prima il microfono (richiesta legata al clic), poi libreria e token.
      md.getUserMedia({ audio: true }).then(function (stream) {
        stream.getTracks().forEach(function (t) { t.stop() })
        if (my !== session) return
        setState('connecting')
        return Promise.all([loadLib(), fetch('/api/voce/token', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lang: LANG }), credentials: 'same-origin'
        }).then(function (r) {
          if (r.status === 429) throw new Error('busy')
          if (r.status === 503) throw new Error('off')
          if (!r.ok) throw new Error('token')
          return r.json()
        })]).then(function (res) {
          if (my !== session) return
          return connect(res[0], res[1], my)
        })
      }, function () { if (my === session) fail('denied') }).catch(function (err) {
        if (my !== session) return
        fail(err && (err.message === 'busy' || err.message === 'off') ? err.message : 'error')
      })
    }
    function connect(LKc, data, my) {
      LK = LKc
      if (!data || !data.token || !data.url) throw new Error('token')
      var r = new LK.Room({ adaptiveStream: true, dynacast: true })
      room = r
      var E = LK.RoomEvent
      r.on(E.TrackSubscribed, function (track) {
        if (track.kind === 'audio') {
          var a = track.attach(); a.className = 'ov-audio'; a.hidden = true; a.autoplay = true; a.setAttribute('playsinline', '')
          if (!a.isConnected) body.appendChild(a)
          var p = a.play && a.play(); if (p && p.catch) p.catch(function () { bAudio.hidden = false })
          if (state === 'joining') setState('listening')
        } else if (track.kind === 'video') {
          track.attach(video); video.hidden = false; orb.hidden = true
          if (state === 'joining') setState('listening')
        }
      })
      r.on(E.TrackUnsubscribed, function (track) {
        track.detach().forEach(function (x) { if (x !== video) x.remove() })
        if (track.kind === 'video') { video.hidden = true; orb.hidden = false }
      })
      r.on(E.ActiveSpeakersChanged, function (speakers) {
        if (state !== 'listening' && state !== 'speaking') return
        var agent = speakers.some(function (p) { return p !== r.localParticipant })
        setState(agent ? 'speaking' : 'listening')
      })
      r.on(E.Reconnecting, function () { setState('reconnecting') })
      r.on(E.Reconnected, function () { setState('listening') })
      r.on(E.Disconnected, function () {
        // Se la connessione non è mai partita, l'errore lo mostra il catch di start().
        if (room === r && /^(joining|listening|speaking|reconnecting)$/.test(state)) hangup(T.vEnded)
      })
      r.on(E.AudioPlaybackStatusChanged, function () { bAudio.hidden = r.canPlaybackAudio })
      r.on(E.DataReceived, function (payload, participant, kind, topic) {
        if (topic !== 'ui') return
        try {
          var msg = JSON.parse(new TextDecoder().decode(payload))
          if (msg && msg.action === 'navigate') agentNavigate(typeof msg.path === 'string' ? msg.path : msg.page)
        } catch (x) { /* messaggio non valido: ignorato */ }
      })
      return r.connect(data.url, data.token).then(function () {
        if (my !== session) { r.disconnect(); return }
        setState('joining')
        return r.localParticipant.setMicrophoneEnabled(true).then(function () {
          r.startAudio().then(function () { bAudio.hidden = r.canPlaybackAudio }, function () { bAudio.hidden = false })
          if (r.remoteParticipants && r.remoteParticipants.size && state === 'joining') setState('listening')
        }, function () { if (my === session) fail('denied') })
      })
    }
    function toggleMute() {
      if (!room) return
      var next = !muted
      room.localParticipant.setMicrophoneEnabled(!next).then(function () {
        muted = next; setMuteLabel(); if (state === 'listening') setState('listening')
      }, function () { })
    }

    // Navigazione chiesta dall'agente: si cambia solo il contenuto di <main>, così chiamata e chat restano aperte.
    function agentNavigate(p) {
      var target = allowedPath(p)
      if (target) softNavigate(target, true, showNavLink)
    }
    function showNavLink(ok, title, url) {
      if (!navP) return
      navP.textContent = ''
      if (ok) navP.appendChild(d.createTextNode(T.vNav + title))
      else { navP.appendChild(d.createTextNode(T.vNavFail + ' ')); navP.appendChild(el('a', { href: url, target: '_blank', rel: 'noopener', text: T.vOpen })) }
      navP.hidden = false
    }
    var softDone = false
    function softNavigate(url, push, done) {
      var abs
      done = done || function () { }
      try { abs = new URL(url, location.href) } catch (x) { return }
      if (abs.origin !== location.origin) return
      if (push && abs.pathname === location.pathname) {
        w.scrollTo({ top: 0, behavior: 'smooth' })
        var h = d.querySelector('main h1'); done(true, h ? h.textContent.trim() : d.title, abs.pathname); return
      }
      fetch(abs.pathname, { credentials: 'same-origin', redirect: 'follow', headers: { Accept: 'text/html' } }).then(function (r) {
        if (!r.ok) throw new Error(String(r.status))
        // Dopo eventuali redirect la pagina deve essere ancora del nostro sito ed essere HTML.
        if (r.url && new URL(r.url).origin !== location.origin) throw new Error('origin')
        if (!/^text\/html\b/i.test(r.headers.get('Content-Type') || '')) throw new Error('type')
        return r.text()
      }).then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html')
        var main = doc.querySelector('main'), cur = d.querySelector('main')
        if (!main || !cur) throw new Error('main')
        cur.innerHTML = main.innerHTML
        d.title = doc.title
        var canon = d.querySelector('link[rel=canonical]'), nc = doc.querySelector('link[rel=canonical]')
        if (canon && nc) canon.href = nc.href
        d.querySelectorAll('header [aria-current]').forEach(function (a) { a.removeAttribute('aria-current') })
        d.querySelectorAll('header a[href]').forEach(function (a) { if (a.getAttribute('href') === abs.pathname) a.setAttribute('aria-current', 'page') })
        if (push) history.pushState({ soft: true }, '', abs.pathname)
        softDone = true
        w.scrollTo(0, 0)
        var h1 = cur.querySelector('h1'); var name = h1 ? h1.textContent.trim() : doc.title
        done(true, name, abs.pathname)
        announce(T.vNav + name)
        d.dispatchEvent(new CustomEvent('odyra:navigated', { detail: { path: abs.pathname } }))
        try { gtag('event', 'page_view', { page_location: location.href, page_title: d.title }) } catch (x) { }
      }).catch(function () { done(false, '', abs.pathname) })
    }
    w.addEventListener('popstate', function () {
      if (!softDone) return
      if (room || (panel && !panel.hidden)) softNavigate(location.pathname, false)
      else location.reload()
    })

    // ───────── scheda Scrivi: chat con l'agente ─────────
    var CHAT_KEY = 'odyra-chat', MAX_SEND = 20
    var chatLog, chatForm, chatInput, chatSend, chatSugg, chatOffP, typingEl = null, chatBusy = false
    var chat = { v: 1, msgs: [], started: false }
    ;(function loadChat() {
      var c = getJSON('sessionStorage', CHAT_KEY)
      if (!c || c.v !== 1 || !Array.isArray(c.msgs)) return
      chat.msgs = c.msgs.filter(function (m) {
        return m && typeof m.content === 'string' && (m.role === 'user' || m.role === 'assistant' || m.role === 'note') && m.content.length < 4000
      }).slice(-40)
      chat.started = !!c.started
    })()
    function saveChat() { setJSON('sessionStorage', CHAT_KEY, { v: 1, msgs: chat.msgs.slice(-40), started: chat.started }) }
    function buildChat() {
      chatLog = el('div', { 'class': 'ch-log', role: 'log', 'aria-live': 'polite', 'aria-label': T.chLog, tabindex: '0' })
      chatSugg = el('div', { 'class': 'ch-sugg', role: 'group', 'aria-label': T.chSuggLabel }, T.chSugg.map(function (q) {
        var b = el('button', { type: 'button', 'class': 'ch-chip', text: q })
        b.addEventListener('click', function () { send(q) })
        return b
      }))
      chatInput = el('textarea', { id: 'ch-input', 'class': 'ch-input', rows: '1', maxlength: '800', placeholder: T.chPlaceholder, autocomplete: 'off', enterkeyhint: 'send' })
      chatSend = el('button', { type: 'submit', 'class': 'ch-send', 'aria-label': T.chSend }); chatSend.innerHTML = ICON.send
      chatForm = el('form', { 'class': 'ch-form', novalidate: '' }, [el('label', { 'for': 'ch-input', 'class': 'oa-sr', text: T.chPlaceholder }), chatInput, chatSend])
      var reset = el('button', { type: 'button', 'class': 'ch-reset', text: T.chReset })
      chatOffP = el('div', { 'class': 'ch-off', hidden: true }, [el('p', { text: T.chOff }), el('a', { 'class': 'ov-b', href: pagePath('prenota'), text: T.chBook })])
      chatForm.addEventListener('submit', function (e) { e.preventDefault(); send(chatInput.value) })
      chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(chatInput.value) }
      })
      chatInput.addEventListener('input', grow)
      reset.addEventListener('click', function () {
        chat.msgs = []; chat.started = false; saveChat(); chatLog.textContent = ''; renderAll(); chatInput.focus()
      })
      chatLog.addEventListener('click', function (e) {
        var a = e.target.closest && e.target.closest('a[data-soft]')
        if (!a) return
        e.preventDefault()
        softNavigate(a.getAttribute('href'), true, function (ok) {
          if (!ok) { location.href = a.getAttribute('href'); return }
          if (isFull()) closePanel()
        })
      })
      return [chatLog, chatOffP, chatSugg, chatForm,
        el('p', { 'class': 'ch-note' }, [T.chNote + ' ', el('a', { href: T.vPrivacyHref, text: T.vPrivacy }), ' · ', reset])]
    }
    function isFull() { return w.matchMedia('(max-width: 30rem)').matches }
    function grow() { chatInput.style.height = 'auto'; chatInput.style.height = Math.min(chatInput.scrollHeight, 128) + 'px' }
    function chatOff(off) {
      if (!chatForm) return
      chatOffP.hidden = !off; chatForm.hidden = off
      if (off) chatSugg.hidden = true
      else chatSugg.hidden = chat.msgs.some(function (m) { return m.role === 'user' })
    }
    var chatRendered = false
    function openChat(focus, opts) {
      if (!chatRendered) { renderAll(); chatRendered = true }
      if (opts.notice) addNote(opts.notice)
      if (opts.ask) send(opts.ask)
      scrollEnd(false)
      if (focus && !(HEALTH && !HEALTH.chat)) {
        // su telefono la tastiera coprirebbe i suggerimenti: il fuoco va al registro, non al campo
        if (w.matchMedia('(pointer: coarse)').matches) chatLog.focus({ preventScroll: true }); else chatInput.focus()
      }
    }
    function renderAll() {
      chatLog.textContent = ''
      if (!chat.msgs.length) { chat.msgs.push({ role: 'assistant', content: T.chWelcome }); saveChat() }
      chat.msgs.forEach(renderMsg)
      chatOff(!!(HEALTH && !HEALTH.chat))
    }
    function renderMsg(m) {
      if (m.role === 'note') { chatLog.appendChild(el('p', { 'class': 'ch-sys', text: m.content })); return }
      var b = el('div', { 'class': 'ch-msg ' + (m.role === 'user' ? 'ch-user' : 'ch-agent') })
      b.appendChild(el('span', { 'class': 'oa-sr', text: m.role === 'user' ? T.chYou : T.chAgent }))
      if (m.role === 'user') b.appendChild(el('p', { text: m.content }))
      else richText(b, m.content)
      chatLog.appendChild(b)
    }
    function addNote(text, node) {
      chat.msgs.push({ role: 'note', content: text }); saveChat()
      var p = el('p', { 'class': 'ch-sys', text: text })
      if (node) { p.appendChild(d.createTextNode(' ')); p.appendChild(node) }
      chatLog.appendChild(p); scrollEnd(true)
    }
    function scrollEnd(smooth) {
      var reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches
      try { chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: smooth && !reduce ? 'smooth' : 'auto' }) } catch (x) { chatLog.scrollTop = chatLog.scrollHeight }
    }
    // Testo del modello → DOM, solo con nodi di testo: paragrafi, elenchi "- ", **grassetto** e link ai soli
    // percorsi interni ammessi. Mai innerHTML con contenuti del modello.
    var INLINE = /\*\*([^*\n]{1,200})\*\*|\[([^\]\n]{1,80})\]\(([^)\s]{1,200})\)|(^|[\s(«"“'])(\/[a-z0-9][a-z0-9\-\/]*)/gi
    function inline(parent, text) {
      var last = 0, m
      INLINE.lastIndex = 0
      while ((m = INLINE.exec(text))) {
        var pre = m[4] || ''
        var startText = m.index + pre.length
        var node = null
        if (m[1]) node = el('strong', { text: m[1] })
        else if (m[2]) { var p = allowedPath(m[3]); node = p ? link(p, m[2]) : d.createTextNode(m[2]) }
        else if (m[5]) { var q = allowedPath(m[5]); if (q) node = link(q, m[5]) }
        if (!node) continue
        parent.appendChild(d.createTextNode(text.slice(last, m[1] || m[2] ? m.index : startText)))
        parent.appendChild(node)
        last = m.index + m[0].length
      }
      parent.appendChild(d.createTextNode(text.slice(last)))
    }
    function link(path, label) { return el('a', { href: path, 'data-soft': '', 'class': 'ch-link', text: label }) }
    function richText(box, text) {
      String(text).replace(/\r/g, '').split(/\n{2,}/).forEach(function (block) {
        var lines = block.split('\n').filter(function (l) { return l.trim() })
        if (!lines.length) return
        var items = lines.every(function (l) { return /^\s*([-•*]|\d+[.)])\s+/.test(l) })
        if (items) {
          var ul = el('ul')
          lines.forEach(function (l) { var li = el('li'); inline(li, l.replace(/^\s*([-•*]|\d+[.)])\s+/, '')); ul.appendChild(li) })
          box.appendChild(ul)
        } else {
          var p = el('p')
          lines.forEach(function (l, i) { if (i) p.appendChild(el('br')); inline(p, l.replace(/^#+\s*/, '')) })
          box.appendChild(p)
        }
      })
    }
    function typing(on) {
      if (on && !typingEl) {
        typingEl = el('div', { 'class': 'ch-msg ch-agent ch-typing', 'aria-hidden': 'true' }, [el('span'), el('span'), el('span')])
        chatLog.appendChild(typingEl); scrollEnd(true)
        chatLog.setAttribute('aria-busy', 'true')
      } else if (!on && typingEl) { typingEl.remove(); typingEl = null; chatLog.removeAttribute('aria-busy') }
    }
    function send(raw) {
      var text = String(raw || '').replace(/\s+$/, '').replace(/^\s+/, '').slice(0, 800)
      if (!text || chatBusy) return
      chatInput.value = ''; grow()
      var m = { role: 'user', content: text }
      chat.msgs.push(m); renderMsg(m); chatSugg.hidden = true
      if (!chat.started) { chat.started = true; track('chat_demo_start', { page: location.pathname, language: LANG }) }
      saveChat(); scrollEnd(true)
      ask()
    }
    function ask() {
      chatBusy = true; chatSend.disabled = true; typing(true)
      var hist = chat.msgs.filter(function (m) { return m.role === 'user' || m.role === 'assistant' }).slice(-MAX_SEND)
        .map(function (m) { return { role: m.role, content: m.content.slice(0, m.role === 'user' ? 800 : 1500) } })
      var ctl = 'AbortController' in w ? new AbortController() : null
      var to = setTimeout(function () { if (ctl) ctl.abort() }, 45000)
      fetch('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', signal: ctl ? ctl.signal : undefined,
        body: JSON.stringify({ messages: hist, lang: LANG, page: location.pathname })
      }).then(function (r) {
        return r.json().then(function (j) { return { s: r.status, j: j } }, function () { return { s: r.status, j: null } })
      }).then(function (res) {
        clearTimeout(to); done()
        if (res.s === 200 && res.j && typeof res.j.reply === 'string') {
          var a = { role: 'assistant', content: res.j.reply.slice(0, 3000) }
          chat.msgs.push(a); saveChat(); renderMsg(a); scrollEnd(true)
          ;(Array.isArray(res.j.actions) ? res.j.actions : []).forEach(action)
        } else if (res.s === 429) addNote(T.chBusy)
        else if (res.s === 503 && res.j && res.j.error === 'non_configurato') {
          HEALTH = { t: Date.now(), voce: HEALTH ? HEALTH.voce : true, chat: false }; setJSON('sessionStorage', 'odyra-health', HEALTH); chatOff(true)
        } else if (res.s === 413) { chat.msgs = chat.msgs.slice(-6); saveChat(); failed() }
        else failed()
      }, function () { clearTimeout(to); done(); failed() })
    }
    function done() { chatBusy = false; chatSend.disabled = false; typing(false) }
    function failed() {
      var b = el('button', { type: 'button', 'class': 'ch-retry', text: T.vRetry })
      b.addEventListener('click', function () {
        var n = b.parentNode; if (n) n.remove()
        var i = chat.msgs.lastIndexOf(chat.msgs.filter(function (m) { return m.role === 'note' }).pop()); if (i >= 0) chat.msgs.splice(i, 1)
        if (!chatBusy) ask()
      })
      addNote(T.chErr, b)
    }
    function action(a) {
      if (!a || typeof a !== 'object') return
      if (a.lead === true) track('generate_lead', { form: 'chat' })
      var p = allowedPath(a.navigate)
      if (!p) return
      softNavigate(p, true, function (ok, name, url) {
        if (!ok) { addNote(T.vNavFail, el('a', { href: url, text: T.vOpen })); return }
        var see = null
        if (isFull()) { see = el('button', { type: 'button', 'class': 'ch-retry', text: T.chSee }); see.addEventListener('click', closePanel) }
        addNote(T.vNav + name, see)
      })
    }

    // ───────── aperture ─────────
    d.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('[data-voice-demo], [data-chat-demo]')
      if (!t && e.target.closest && e.target.closest('.ov-fab')) t = fab
      if (!t) return
      e.preventDefault()
      var isChat = t.hasAttribute('data-chat-demo'), isFab = t === fab
      track('click_demo', { link_text: (t.textContent || '').trim().slice(0, 80), kind: isFab ? 'fab' : isChat ? 'chat' : 'voice' })
      var go = function (h) {
        var vOff = h && h.voce === false, cOff = h && h.chat === false
        if (isChat) return openPanel('chat', t, { ask: (t.getAttribute('data-chat-demo') || '').trim().slice(0, 300) })
        if (isFab) {
          var last = getJSON('sessionStorage', 'odyra-agent-tab')
          return openPanel(vOff && !cOff ? 'chat' : (last === 'chat' ? 'chat' : 'voice'), t)
        }
        // pulsanti "Parla con l'agente": se la voce non c'è ancora, si apre la chat con un avviso
        if (vOff && !cOff) return openPanel('chat', t, { notice: T.vSoonNote })
        openPanel('voice', t, { autostart: true })
      }
      if (panel && !panel.hidden && !isChat && !(t.hasAttribute('data-voice-demo') && tab !== 'voice')) { panel.querySelector('.ov-x').focus(); return }
      if (HEALTH) go(HEALTH); else health().then(go)
    })

    // Su schermi piccoli il pulsante si nasconde quando in basso ci sono altri pulsanti, moduli o il piede.
    if ('IntersectionObserver' in w) {
      var io = null, hits = new Set()
      var watch = function () {
        if (io) io.disconnect()
        hits.clear(); fab.classList.remove('ov-fab-away')
        if (!w.matchMedia('(max-width: 47.99rem)').matches) return
        var strip = Math.max(0, w.innerHeight - 110)
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) { if (en.isIntersecting) hits.add(en.target); else hits.delete(en.target) })
          fab.classList.toggle('ov-fab-away', hits.size > 0)
        }, { rootMargin: '-' + strip + 'px 0px 0px 0px' })
        d.querySelectorAll('main .b, main form, main .actions, footer, .top-nav.open').forEach(function (n) { io.observe(n) })
      }
      watch()
      var rt; w.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(watch, 200) })
      d.addEventListener('odyra:navigated', watch)
    }
  })
})()
