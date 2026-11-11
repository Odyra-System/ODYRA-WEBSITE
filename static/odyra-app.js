/* Odyra: consenso cookie, misurazione, modulo contatti, demo vocale.
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
      vNavFail: 'Non sono riuscito ad aprire la pagina qui.'
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
      vNavFail: 'No he podido abrir la página aquí.'
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
    if (d.referrer) fresh.referrer = san(d.referrer)
    fresh.first_seen_at = new Date().toISOString()
    setJSON('sessionStorage', ATTR_KEY, fresh)
  })()
  function attribution() { return getJSON('sessionStorage', ATTR_KEY) || {} }

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
      var a = e.target.closest && e.target.closest('a[href], [data-voice-demo]')
      if (!a) return
      if (a.hasAttribute('data-voice-demo')) return track('click_demo', { link_text: (a.textContent || '').trim().slice(0, 80), kind: 'voice' })
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
            var to = f.getAttribute('data-redirect')
            if (to && /^\/(?!\/)/.test(to)) { setTimeout(function () { location.href = to }, 250); return }
            f.reset(); say(f.getAttribute('data-ok') || T.fOk)
          } else if (r.status === 400 || r.status === 413 || r.status === 415) say(T.fBad, true)
          else if (r.status === 429) say(T.fMany, true)
          else mail()
        }, function () { done(); mail() })
    }, true)

    // ───────── demo vocale ─────────
    var NAV = {}
    try { NAV = JSON.parse((me && me.getAttribute('data-voice-nav')) || '{}') } catch (x) { NAV = {} }
    var fab = el('button', { type: 'button', 'class': 'ov-fab', 'data-voice-demo': '', 'aria-haspopup': 'dialog', 'aria-label': T.vFabAria })
    fab.innerHTML = ICON.mic
    fab.appendChild(el('span', { 'class': 'ov-fab-t', 'aria-hidden': 'true', text: T.vFab }))
    body.appendChild(fab)

    var panel, stEl, orb, bMute, bEnd, bRetry, bAudio, navP, video
    var room = null, LK = null, state = 'idle', muted = false, lastOpener = null, session = 0
    function buildPanel() {
      var title = el('h2', { id: 'ov-title', text: T.vTitle })
      var bClose = el('button', { type: 'button', 'class': 'ov-x', 'aria-label': T.vClose }); bClose.innerHTML = ICON.close
      stEl = el('p', { 'class': 'ov-status', role: 'status', 'aria-live': 'polite', text: T.vIdle })
      orb = el('div', { 'class': 'ov-orb', 'aria-hidden': 'true' }, [el('span'), el('span'), el('span')])
      video = el('video', { 'class': 'ov-video', playsinline: '', muted: '', autoplay: '', hidden: true })
      video.muted = true
      bAudio = el('button', { type: 'button', 'class': 'ov-b ov-b-line', hidden: true, text: T.vAudio })
      navP = el('p', { 'class': 'ov-nav', hidden: true })
      bMute = el('button', { type: 'button', 'class': 'ov-b ov-b-line ov-mute', 'aria-pressed': 'false', disabled: 'disabled' })
      bEnd = el('button', { type: 'button', 'class': 'ov-b ov-end', text: T.vEnd })
      bRetry = el('button', { type: 'button', 'class': 'ov-b', hidden: true, text: T.vRetry })
      panel = el('section', { 'class': 'ov-panel', role: 'dialog', 'aria-modal': 'false', 'aria-labelledby': 'ov-title', hidden: true }, [
        el('header', { 'class': 'ov-h' }, [title, bClose]),
        el('p', { 'class': 'ov-note' }, [T.vNote + ' ', el('a', { href: T.vPrivacyHref, text: T.vPrivacy })]),
        el('div', { 'class': 'ov-stage' }, [orb, video]), stEl, bAudio, navP,
        el('div', { 'class': 'ov-actions' }, [bMute, bRetry, bEnd])])
      setMuteLabel()
      bClose.addEventListener('click', closePanel)
      bEnd.addEventListener('click', function () { if (room || state === 'connecting' || state === 'loading') hangup(T.vEnded); else closePanel() })
      bRetry.addEventListener('click', start)
      bMute.addEventListener('click', toggleMute)
      bAudio.addEventListener('click', function () { if (room) room.startAudio().then(function () { bAudio.hidden = room.canPlaybackAudio }, function () { }) })
      panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); closePanel() } })
      body.appendChild(panel)
    }
    function setMuteLabel() {
      bMute.innerHTML = muted ? ICON.micOff : ICON.mic
      bMute.setAttribute('aria-label', muted ? T.vUnmute : T.vMute)
      bMute.setAttribute('aria-pressed', String(muted))
    }
    function setState(s, msg) {
      state = s
      panel.setAttribute('data-state', s)
      stEl.textContent = msg || {
        idle: T.vIdle, loading: T.vLoading, mic: T.vMicAsk, connecting: T.vConnecting, joining: T.vJoining, listening: muted ? T.vMuted : T.vListening,
        speaking: T.vSpeaking, reconnecting: T.vReconnecting, ended: T.vEnded, error: T.vError, denied: T.vMicDenied
      }[s] || ''
      var active = s === 'joining' || s === 'listening' || s === 'speaking' || s === 'reconnecting'
      bMute.disabled = !active
      bRetry.hidden = !(s === 'error' || s === 'denied' || s === 'ended')
      bEnd.textContent = (active || s === 'connecting' || s === 'loading' || s === 'mic') ? T.vEnd : T.vClose.split(' ')[0]
      root.classList.toggle('ov-live', active)
    }
    function openPanel(from) {
      if (!panel) buildPanel()
      lastOpener = from || fab
      panel.hidden = false
      root.classList.add('ov-open')
      fab.setAttribute('aria-expanded', 'true')
      panel.querySelector('.ov-x').focus()
      if (!room && state !== 'connecting' && state !== 'loading' && state !== 'mic') start()
    }
    function closePanel() {
      if (room || state === 'connecting' || state === 'loading' || state === 'mic') hangup()
      if (!panel) return
      panel.hidden = true
      root.classList.remove('ov-open')
      fab.setAttribute('aria-expanded', 'false')
      if (lastOpener && d.contains(lastOpener)) lastOpener.focus(); else fab.focus()
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
          if (msg && msg.action === 'navigate' && typeof msg.path === 'string') agentNavigate(msg.path)
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

    // Navigazione chiesta dall'agente: si cambia solo il contenuto di <main>, così la chiamata non cade.
    var MAP = { '/': 'home', '/#contatti': 'contatti', '/case/boss-italia': 'case' }
    function agentNavigate(p) {
      if (!Object.prototype.hasOwnProperty.call(MAP, p) && !/^\/case\/[a-z0-9-]+$/.test(p)) return
      var target = NAV[MAP[p] || 'lavori'] || ({ home: '/', contatti: '/contatti', case: '/case/boss-italia' }[MAP[p]] || '/lavori')
      softNavigate(target, true)
    }
    function showNavLink(url, title, ok) {
      if (!navP) return
      navP.textContent = ''
      if (ok) navP.appendChild(d.createTextNode(T.vNav + title))
      else { navP.appendChild(d.createTextNode(T.vNavFail + ' ')); navP.appendChild(el('a', { href: url, target: '_blank', rel: 'noopener', text: T.vOpen })) }
      navP.hidden = false
    }
    var softDone = false
    function softNavigate(url, push) {
      var abs
      try { abs = new URL(url, location.href) } catch (x) { return }
      if (abs.origin !== location.origin) return
      if (push && abs.pathname === location.pathname) { w.scrollTo({ top: 0, behavior: 'smooth' }); return }
      fetch(abs.pathname, { credentials: 'same-origin', headers: { Accept: 'text/html' } }).then(function (r) {
        if (!r.ok) throw new Error(String(r.status))
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
        showNavLink(abs.pathname, name, true)
        announce(T.vNav + name)
        d.dispatchEvent(new CustomEvent('odyra:navigated', { detail: { path: abs.pathname } }))
        try { gtag('event', 'page_view', { page_location: location.href, page_title: d.title }) } catch (x) { }
      }).catch(function () { showNavLink(abs.pathname, '', false) })
    }
    w.addEventListener('popstate', function () {
      if (!softDone) return
      if (room) softNavigate(location.pathname, false)
      else location.reload()
    })

    d.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('[data-voice-demo]')
      if (!t) return
      e.preventDefault()
      if (panel && !panel.hidden) { panel.querySelector('.ov-x').focus(); return }
      openPanel(t)
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
