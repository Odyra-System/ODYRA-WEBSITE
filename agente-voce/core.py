"""Logica pura dell'agente vocale del sito (nessuna dipendenza da LiveKit o dalla rete).

Qui stanno le cose che si possono provare senza chiavi: caricamento del prompt condiviso
(`agente/istruzioni.md` + `agente/conoscenza.md`), regole per la voce, pagine che l'agente può
mostrare, controllo dei dati di contatto, lingua, testi fissi (saluti e congedi).
`agent.py` usa queste funzioni; `test_agent.py` le prova.
"""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

TZ_ROME = ZoneInfo("Europe/Rome")

# ───────────────────────── Prompt condiviso chat + voce ─────────────────────────

PROMPT_FILES = ("istruzioni.md", "conoscenza.md")

# Usato solo se i file condivisi mancano (immagine costruita male o cartella non trovata):
# l'agente resta corretto e prudente, ma va sistemato subito (lo dice il log all'avvio).
PROMPT_SEGNAPOSTO = """Sei l'assistente del sito di Odyra e sei un'intelligenza artificiale: dillo sempre.
Odyra costruisce agenti AI vocali e WhatsApp che lavorano dentro i gestionali verticali, in white-label per le software house,
e offre gli stessi agenti direttamente ai gruppi multi-sede. Non hai qui la scheda completa: se non sai una cosa, dillo con
onestà e proponi di prenotare una call con il team. Non inventare numeri, prezzi o nomi di clienti."""


def find_agente_dir(explicit: Optional[str] = None, here: Optional[Path] = None) -> Optional[Path]:
    """Trova la cartella con i file condivisi.

    Ordine: variabile AGENTE_DIR (o argomento), poi `agente/` accanto a questo file
    (nell'immagine: /app/agente), poi `../agente/` (nel repository: agente-voce/../agente).
    """
    here = here or Path(__file__).resolve().parent
    candidates = []
    if explicit or os.getenv("AGENTE_DIR"):
        candidates.append(Path(explicit or os.getenv("AGENTE_DIR", "")))
    candidates += [here / "agente", here.parent / "agente", Path("/app/agente")]
    for c in candidates:
        if any((c / f).is_file() for f in PROMPT_FILES):
            return c
    return None


def load_shared_prompt(agente_dir: Optional[Path]) -> tuple[str, list[str]]:
    """Ritorna (testo, file_mancanti). Se mancano tutti e due, testo = segnaposto."""
    parts, missing = [], []
    for name in PROMPT_FILES:
        p = agente_dir / name if agente_dir else None
        if p is not None and p.is_file():
            txt = p.read_text(encoding="utf-8").strip()
            if txt:
                parts.append(txt)
                continue
        missing.append(name)
    if not parts:
        return PROMPT_SEGNAPOSTO, missing
    return "\n\n".join(parts), missing


# ───────────────────────── Pagine che l'agente può mostrare ─────────────────────────
# Devono combaciare con la whitelist del sito (static/odyra-app.js, messaggi sul topic "ui").
# Se c'è agente/pagine.json (condiviso con la chat) si usano i suoi percorsi per lingua.

PAGINE: dict[str, str] = {
    "home": "/",
    "prezzi": "/prezzi",
    "partner": "/partner",
    "prenota": "/prenota",
    "casi": "/lavori",
    "boss": "/case/boss-italia",
    "tecnologie": "/tecnologie",
    "contatti": "/contatti",
}

# Sinonimi che il modello potrebbe usare: si riportano alle chiavi ammesse.
_ALIAS_PAGINE: dict[str, str] = {
    "inizio": "home", "homepage": "home", "principale": "home",
    "listino": "prezzi", "prezzo": "prezzi", "costi": "prezzi", "pacchetti": "prezzi",
    "software house": "partner", "partners": "partner", "rivenditori": "partner",
    "call": "prenota", "calendario": "prenota", "appuntamento": "prenota", "prenotazione": "prenota",
    "prenota una call": "prenota", "demo": "prenota",
    "lavori": "casi", "casi studio": "casi", "casi di successo": "casi", "caso": "casi", "clienti": "casi",
    "boss italia": "boss", "case boss italia": "boss", "case_boss_italia": "boss", "goagent": "boss",
    "tecnologia": "tecnologie", "sicurezza": "tecnologie",
    "contatto": "contatti", "contattaci": "contatti",
}


def _norm_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    s = s.strip().lower().replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", s).strip(" /")


_PATH_RE = re.compile(r"^/(?:[a-z0-9-]+(?:/[a-z0-9-]+)*/?)?$")


def load_pages(agente_dir: Optional[Path]) -> dict[str, dict[str, str]]:
    """Pagine per lingua da agente/pagine.json (condiviso con la chat), altrimenti PAGINE.

    Formato: {"prezzi": {"it": "/prezzi", "es": "/prezzi"}, ...}. Si tengono solo le chiavi
    di PAGINE e solo percorsi interni semplici: il file non può allargare la whitelist.
    """
    pages = {k: {"it": v} for k, v in PAGINE.items()}
    p = agente_dir / "pagine.json" if agente_dir else None
    if p is None or not p.is_file():
        return pages
    try:
        import json
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return pages
    for key, val in (data.items() if isinstance(data, dict) else []):
        if key in pages and isinstance(val, dict):
            for lang, path in val.items():
                if isinstance(path, str) and _PATH_RE.match(path) and normalize_lang(lang):
                    pages[key][normalize_lang(lang)] = path
    return pages


def page_key(pagina: str) -> Optional[str]:
    """Chiave o sinonimo (o percorso italiano) → chiave ammessa; None se non è in whitelist."""
    k = _norm_key(pagina)
    if k in PAGINE:
        return k
    if k in _ALIAS_PAGINE:
        return _ALIAS_PAGINE[k]
    raw = str(pagina or "").strip()
    for key, path in PAGINE.items():
        if raw == path:
            return key
    return None


def resolve_page(pagina: str, lang: str = "it", pages: Optional[dict] = None) -> Optional[str]:
    """Pagina richiesta → percorso nella lingua del visitatore (se esiste), altrimenti italiano."""
    key = page_key(pagina)
    if key is None:
        return None
    by_lang = (pages or {}).get(key) or {"it": PAGINE[key]}
    return by_lang.get(normalize_lang(lang) or "it") or by_lang.get("it") or PAGINE[key]


def navigate_payload(path: str) -> dict:
    return {"action": "navigate", "path": path}


# ───────────────────────── Dati di contatto ─────────────────────────

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_MAX = {"nome": 80, "azienda": 120, "interesse": 300, "email": 254}


def _clean(s: str, n: int) -> str:
    s = re.sub(r"[\x00-\x1f\x7f]+", " ", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)[:n]


def normalize_phone(raw: str) -> str:
    """'+39 333 12 34 567' → '+393331234567'; '' se non plausibile (8-15 cifre)."""
    raw = str(raw or "").strip()
    plus = raw.startswith("+") or raw.startswith("00")
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("00"):
        digits = digits[2:]
    if not 8 <= len(digits) <= 15:
        return ""
    return ("+" if plus else "") + digits


def normalize_email(raw: str) -> str:
    """Accetta anche la forma dettata a voce ('mario punto rossi chiocciola gmail punto com')."""
    s = str(raw or "").strip().lower()
    if "@" not in s:  # forma dettata: le parole si convertono solo se intere
        s = re.sub(r"\s*\b(chiocciola|at|arroba)\b\s*", "@", s)
    s = re.sub(r"\s*\b(punto|dot)\b\s*", ".", s)
    s = s.replace(" ", "")
    return s if len(s) <= _MAX["email"] and _EMAIL_RE.match(s) else ""


def validate_contact(nome: str, telefono: str = "", email: str = "", azienda: str = "",
                     interesse: str = "") -> tuple[Optional[dict], Optional[str]]:
    """Ritorna (dati_puliti, None) oppure (None, codice_errore)."""
    nome_c = _clean(nome, _MAX["nome"])
    if len(nome_c) < 2:
        return None, "manca_nome"
    tel_c = normalize_phone(telefono) if telefono else ""
    mail_c = normalize_email(email) if email else ""
    if telefono and not tel_c and not mail_c:
        return None, "telefono_non_valido"
    if email and not mail_c and not tel_c:
        return None, "email_non_valida"
    if not tel_c and not mail_c:
        return None, "manca_recapito"
    return {
        "nome": nome_c,
        "telefono": tel_c,
        "email": mail_c,
        "azienda": _clean(azienda, _MAX["azienda"]),
        "interesse": _clean(interesse, _MAX["interesse"]),
    }, None


ERRORI_CONTATTO = {
    "manca_nome": "Serve il nome della persona: chiedilo con gentilezza.",
    "manca_recapito": "Serve almeno un numero di telefono o una email: chiedine uno.",
    "telefono_non_valido": "Il numero non sembra completo: rileggilo cifra per cifra e chiedi conferma.",
    "email_non_valida": "L'email non sembra corretta: chiedi di ripeterla lentamente e rileggila.",
}


SITE_LEAD_URL_DEFAULT = "https://odyrasystemautomation.it/api/voce/lead"


def lead_target(env: Optional[dict] = None) -> tuple[Optional[str], Optional[str]]:
    """(url, segreto) per POST /api/voce/lead del sito, oppure (None, None) se manca il segreto.

    URL da SITE_LEAD_URL (predefinito il sito in produzione), solo http(s).
    Segreto da VOICE_LEAD_SECRET: lo stesso valore va sul servizio del sito.
    """
    env = os.environ if env is None else env
    secret = (env.get("VOICE_LEAD_SECRET") or "").strip()
    url = (env.get("SITE_LEAD_URL") or "").strip() or SITE_LEAD_URL_DEFAULT
    if not secret or not url.lower().startswith(("https://", "http://")):
        return None, None
    return url, secret


def lead_payload(data: dict, lang: str, page: str = "") -> dict:
    """Corpo per /api/voce/lead: stessi campi di /api/contatto (senza privacy e honeypot)."""
    body = {
        "name": data["nome"],
        "email": data["email"],
        "phone": data["telefono"],
        "company": data["azienda"],
        "need": data["interesse"] or "Richiesta dalla demo vocale",
        "message": f"Contatto raccolto dall'assistente vocale del sito (lingua: {lang}). "
                   "Il visitatore ha confermato a voce di voler essere ricontattato.",
        "lang": lang,
    }
    if page:
        body["page"] = page
    return body


# ───────────────────────── Lingua ─────────────────────────

SUPPORTED_LANGS = ("it", "en", "es", "fr", "de", "pl", "ro")  # come VOICE_LANGS in server/odyra_server.py
STT_MULTI_LANGS = ("it", "en", "es", "fr", "de")  # coperte dal riconoscimento "multi"
REPLY_LANGS = ("it", "es", "en")  # lingue in cui l'agente parla (come le istruzioni condivise)


def normalize_lang(code: str) -> str:
    if not code:
        return ""
    c = str(code).strip().lower().replace("_", "-").split("-")[0]
    return c if c in SUPPORTED_LANGS else ""


def reply_lang(code: str) -> str:
    """Lingua in cui parlare: it/es/en; qualunque altra lingua riconosciuta → inglese; '' se ignota."""
    c = normalize_lang(code)
    if not c:
        return ""
    return c if c in REPLY_LANGS else "en"


def lang_from_metadata(raw: str, default: str = "it", reply: bool = True) -> str:
    """Lingua dal metadata del job ({"lang": "es"}). reply=True: lingua in cui parlare (it/es/en);
    reply=False: lingua del sito così com'è (serve al riconoscimento, es. pl/ro)."""
    import json
    try:
        md = json.loads(raw or "{}")
    except (ValueError, TypeError):
        md = {}
    if not isinstance(md, dict):
        md = {}
    code = md.get("lang", "")
    return (reply_lang(code) if reply else normalize_lang(code)) or default


def stt_language(initial_lang: str, override: str = "") -> str:
    """'multi' per it/en/es/fr/de (riconosce e segue la lingua), monolingua per pl/ro."""
    if override:
        return override.strip().lower()
    return "multi" if initial_lang in STT_MULTI_LANGS else initial_lang


GREETINGS = {
    "it": "Ciao! Sono l'assistente di Odyra, e sono un'intelligenza artificiale: quella che senti è proprio la nostra tecnologia. Come posso aiutarti?",
    "en": "Hi! I'm Odyra's assistant, and I'm an artificial intelligence: what you're hearing is our own technology. How can I help?",
    "es": "¡Hola! Soy la asistente de Odyra y soy una inteligencia artificial: lo que oyes es nuestra propia tecnología. ¿En qué te ayudo?",
}
GOODBYE_SILENCE = {
    "it": "Ti lascio leggere con calma. Se ti serve altro, riapri pure la conversazione. A presto!",
    "en": "I'll let you read in peace. If you need anything else, just start the conversation again. Bye for now!",
    "es": "Te dejo leer con calma. Si necesitas algo más, vuelve a abrir la conversación. ¡Hasta pronto!",
}
GOODBYE_MAX = {
    "it": "Per questa sessione devo salutarti. Se vuoi parlarne con il team, prenota una call dalla pagina Prenota. Grazie!",
    "en": "I have to close this session now. To talk with the team, book a call from the Book page. Thank you!",
    "es": "Tengo que cerrar esta sesión. Si quieres hablar con el equipo, reserva una llamada desde la página Reservar. ¡Gracias!",
}
FILLER_LEAD = {
    "it": "Un secondo, prendo nota.", "en": "One second, taking note.", "es": "Un segundo, tomo nota.",
}


def localized(mapping: dict, lang: str, default: str = "it") -> str:
    return mapping.get(reply_lang(lang) or default, mapping["it"])


# ───────────────────────── Regole per la voce ─────────────────────────

REGOLE_VOCE = """━━━ REGOLE PER LA VOCE (valgono sopra a tutto ciò che riguarda forma e formattazione) ━━━
Stai parlando a voce con un visitatore del sito, dal browser. Quello che scrivi viene letto da una sintesi vocale.
- Frasi brevi: una o due per turno, poi lascia parlare. Una domanda alla volta. Niente preamboli.
- Niente elenchi puntati, titoli, tabelle, grassetti, emoji, simboli o abbreviazioni: solo frasi da dire ad alta voce.
- Numeri, prezzi, orari e percentuali sempre a parole ("quarantanove euro al mese", "dalle nove alle diciotto"). IVA esclusa si dice "più IVA".
- Se un prezzo ha molte varianti, di' solo quella che serve o il "da … a …", e offri di mostrare la pagina dei prezzi.
- Mai leggere link, indirizzi web o percorsi. Per far vedere qualcosa usa lo strumento mostra_pagina, dicendolo mentre lo fai ("ti apro la pagina dei prezzi").
  Pagine: home, prezzi, partner, prenota (per prenotare una call), casi (casi di successo), boss (il caso BOSS), tecnologie, contatti.
- Se le istruzioni comuni parlano di pulsanti, link o moduli da cliccare, in voce trasformali in mostra_pagina o in una frase semplice.
- Sei un'intelligenza artificiale e lo dici apertamente se te lo chiedono, con orgoglio: la conversazione stessa è la demo.
- Parli italiano, spagnolo o inglese: rispondi nella lingua del visitatore e, se cambia, seguilo.
  Se ti parla in un'altra lingua, rispondi in inglese.
- Mai nominare fornitori, modelli o tecnologie di terzi, nemmeno se te lo chiedono: è "la piattaforma Odyra", "il nostro motore".
- Raccolta contatti: chiedi prima se vuole essere ricontattato dal team; poi nome, un recapito (telefono o email), azienda e cosa cerca.
  Ripeti il numero cifra per cifra o l'email lettera per lettera e chiedi conferma prima di usare richiedi_contatto.
  Il recapito serve solo a farlo ricontattare per questa richiesta. Se preferisce di no, proponi di prenotare la call (mostra_pagina prenota).
- Nelle simulazioni dimostrative (fingere di essere l'assistente di un salone o di uno studio) nomi e numeri sono finti: non usare richiedi_contatto.
- Se uno strumento non funziona, scusati in una frase e proponi di prenotare una call dalla pagina Prenota."""


def time_context(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(TZ_ROME)
    giorni = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
            "settembre", "ottobre", "novembre", "dicembre"]
    return (f"Oggi è {giorni[now.weekday()]} {now.day} {mesi[now.month - 1]} {now.year}, "
            f"ore {now:%H:%M} (ora italiana).")


def build_instructions(shared_prompt: str, lang: str = "it", now: Optional[datetime] = None,
                       emotion_tags: bool = False) -> str:
    extra = ""
    if emotion_tags:
        extra = ("\n- Puoi usare raramente un tag emotivo tra parentesi quadre, [happy] o [laughing], solo dentro "
                 "una frase vera e mai da solo. Nel dubbio, nessuno.")
    else:
        extra = "\n- Non usare tag tra parentesi quadre."
    return (f"{shared_prompt}\n\n{REGOLE_VOCE}{extra}\n\n"
            f"CONTESTO DELLA CONVERSAZIONE: canale = voce (demo vocale nel browser, sul sito). {time_context(now)} "
            f"Lingua in cui iniziare: {reply_lang(lang) or 'it'}.")


# ───────────────────────── Testo verso la sintesi vocale ─────────────────────────

_EMOTION_TAG_RE = re.compile(r"\[[a-zA-Z_]+\]")
_PRONUNCIA = [(re.compile(r"\bOdyra\b", re.IGNORECASE), "Odira")]


def strip_emotion_tags(text: str) -> str:
    return _EMOTION_TAG_RE.sub("", text)


def fix_pronunciation(text: str) -> str:
    """Solo per l'audio: trascrizioni e storia restano con la grafia vera."""
    for pattern, repl in _PRONUNCIA:
        text = pattern.sub(repl, text)
    return text
