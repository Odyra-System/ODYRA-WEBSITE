"""odyra_web — agente vocale del sito Odyra (worker LiveKit Agents).

Flusso: il sito (server/odyra_server.py, /api/voce) crea un token con
roomConfig.agents=[{agentName: odyra_web, metadata: {"lang": "it"}}] → LiveKit manda questo
worker nella stanza → conversazione a voce dal browser.

Prompt = agente/istruzioni.md + agente/conoscenza.md (gli stessi della chat del sito)
         + regole per la voce (core.REGOLE_VOCE).
Strumenti: richiedi_contatto (lead) e mostra_pagina (porta il visitatore su una pagina del sito).

Regole: nessun dato personale nei log (niente trascrizioni, nomi, numeri, email, metadati grezzi).
Avvio: `python agent.py start` (produzione), `python agent.py dev` o `console` (prove).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Optional

import aiohttp
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    JobContext,
    JobProcess,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context,
    inference,
)
from livekit.plugins import deepgram, silero

import core

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("odyra_web")


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def _envf(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _envb(name: str, default: bool) -> bool:
    return _env(name, str(default)).lower() in ("1", "true", "yes", "on")


# ───────────────────────── Configurazione ─────────────────────────

AGENT_NAME = _env("LIVEKIT_AGENT_NAME", "odyra_web")  # = VOICE_AGENT_NAME del sito
DEFAULT_LANG = core.reply_lang(_env("DEFAULT_LANG", "it")) or "it"

# LLM: openai (predefinito, primo token più rapido) o anthropic; l'altro fa da riserva se ha la chiave.
LLM_PROVIDER = _env("LLM_PROVIDER", "openai").lower()
OPENAI_MODEL = _env("OPENAI_MODEL", _env("LLM_MODEL", "gpt-4.1-mini"))
ANTHROPIC_MODEL = _env("ANTHROPIC_MODEL", _env("LLM_FALLBACK_MODEL", "claude-sonnet-4-6"))
LLM_TEMPERATURE = _envf("LLM_TEMPERATURE", 0.4)
LLM_FALLBACK_ENABLED = _envb("LLM_FALLBACK_ENABLED", True)
LLM_ATTEMPT_TIMEOUT_S = _envf("LLM_ATTEMPT_TIMEOUT_S", 3.0)

# TTS: inworld (predefinito, come oggi) o cartesia. Riserva Cartesia spenta di default: con il
# FallbackAdapter Inworld passava alla sintesi non in streaming e restava muto.
TTS_PROVIDER = _env("TTS_PROVIDER", "inworld").lower()
TTS_FALLBACK_ENABLED = _envb("TTS_FALLBACK_ENABLED", False)
INWORLD_MODEL = _env("INWORLD_MODEL", "inworld-tts-2")
INWORLD_VOICE = _env("INWORLD_VOICE")
INWORLD_SPEAKING_RATE = _envf("INWORLD_SPEAKING_RATE", 1.1)
INWORLD_DELIVERY_MODE = _env("INWORLD_DELIVERY_MODE", "CREATIVE")
CARTESIA_MODEL = _env("CARTESIA_MODEL", "sonic-3")
CARTESIA_VOICE = _env("CARTESIA_VOICE")

# STT: Deepgram.
DEEPGRAM_MODEL = _env("DEEPGRAM_MODEL", "nova-3-general")
DEEPGRAM_LANGUAGE = _env("DEEPGRAM_LANGUAGE")  # vuoto = automatico (multi o monolingua)
KEYTERMS = ["Odyra", "WhatsApp", "gestionale", "software house", "centralino", "agenda",
            "chiocciola", "punto", "gmail", "prefisso", "cellulare"]

# Turni e tempi (tarati per il web, come il worker attuale).
TURN_DETECTION = _env("TURN_DETECTION", "model").lower()  # model | vad
VAD_ACTIVATION_THRESHOLD = _envf("VAD_ACTIVATION_THRESHOLD", 0.5)
MIN_ENDPOINTING_DELAY = _envf("MIN_ENDPOINTING_DELAY", 0.3)
MAX_ENDPOINTING_DELAY = _envf("MAX_ENDPOINTING_DELAY", 1.5)
MIN_INTERRUPTION_DURATION = _envf("MIN_INTERRUPTION_DURATION", 0.6)
MIN_INTERRUPTION_WORDS = int(_envf("MIN_INTERRUPTION_WORDS", 2))
PREEMPTIVE_GENERATION = _envb("PREEMPTIVE_GENERATION", True)
FALSE_INTERRUPTION_TIMEOUT_S = _envf("FALSE_INTERRUPTION_TIMEOUT_S", 2.0)
SILENCE_TIMEOUT_S = _envf("SILENCE_TIMEOUT_S", 60.0)
MAX_DURATION_S = _envf("MAX_DURATION_S", 480.0)
STUCK_TIMEOUT_S = _envf("STUCK_TIMEOUT_S", 18.0)
FILLER_DELAY_S = _envf("FILLER_DELAY_S", 0.7)
LANG_SWITCH_CONFIRMATIONS = max(1, int(_envf("LANG_SWITCH_CONFIRMATIONS", 2)))

# Avatar video: solo se richiesto esplicitamente e configurato (aggiunge latenza).
AVATAR_ENABLED = _envb("AVATAR_ENABLED", False) and all(
    _env(k) for k in ("TAVUS_API_KEY", "TAVUS_REPLICA_ID", "TAVUS_PERSONA_ID"))

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=8)
THINKING_SOUND = AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.3, fade_in=0.3, fade_out=0.5)

# Prompt condiviso: si legge una volta all'avvio del processo.
AGENTE_DIR = core.find_agente_dir()
SHARED_PROMPT, PROMPT_MISSING = core.load_shared_prompt(AGENTE_DIR)
PAGES = core.load_pages(AGENTE_DIR)

# ───────────────────────── Sentry (facoltativo, senza dati personali) ─────────────────────────

_SENTRY = None
if _env("SENTRY_DSN"):
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        def _scrub(event: dict, hint: Any = None) -> Optional[dict]:
            # Togliamo tutto ciò che potrebbe contenere testo della conversazione o recapiti.
            for key in ("request", "user", "extra", "contexts"):
                event.pop(key, None)
            for bc in (event.get("breadcrumbs") or {}).get("values", []) or []:
                bc.pop("data", None)
            return event

        sentry_sdk.init(
            dsn=_env("SENTRY_DSN"),
            environment=_env("SENTRY_ENVIRONMENT", _env("RAILWAY_ENVIRONMENT_NAME", "production")),
            release=_env("SENTRY_RELEASE", _env("RAILWAY_GIT_COMMIT_SHA")) or None,
            traces_sample_rate=_envf("SENTRY_TRACES_SAMPLE_RATE", 0.0),
            send_default_pii=False,
            include_local_variables=False,
            max_breadcrumbs=30,
            before_send=_scrub,
            auto_enabling_integrations=False,
            integrations=[LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR)],
        )
        sentry_sdk.set_tag("agent_name", AGENT_NAME)
        _SENTRY = sentry_sdk
    except Exception as e:  # noqa: BLE001
        logger.warning("Sentry non attivo: %s", type(e).__name__)


def _report(exc: BaseException) -> None:
    if _SENTRY is not None:
        try:
            _SENTRY.capture_exception(exc)
        except Exception:  # noqa: BLE001
            pass


# ───────────────────────── Motori ─────────────────────────

def build_llm():
    from livekit.plugins import anthropic, openai

    def _openai():
        return openai.LLM(model=OPENAI_MODEL, temperature=LLM_TEMPERATURE, parallel_tool_calls=False)

    def _anthropic():
        return anthropic.LLM(model=ANTHROPIC_MODEL, temperature=LLM_TEMPERATURE)

    order = [("anthropic", _anthropic, "ANTHROPIC_API_KEY"), ("openai", _openai, "OPENAI_API_KEY")]
    if LLM_PROVIDER != "anthropic":
        order.reverse()
    engines = []
    for name, make, key in order:
        if not engines or (LLM_FALLBACK_ENABLED and _env(key)):
            try:
                engines.append(make())
            except Exception as e:  # noqa: BLE001
                logger.warning("LLM %s non disponibile: %s", name, type(e).__name__)
    if len(engines) == 1:
        return engines[0]
    from livekit.agents.llm import FallbackAdapter
    return FallbackAdapter(engines, attempt_timeout=LLM_ATTEMPT_TIMEOUT_S)


def _make_tts(provider: str, lang: str):
    if provider == "cartesia":
        from livekit.plugins import cartesia
        kw: dict[str, Any] = dict(model=CARTESIA_MODEL, language=lang)
        if CARTESIA_VOICE:
            kw["voice"] = CARTESIA_VOICE
        return cartesia.TTS(**kw)
    from livekit.plugins import inworld
    kw = dict(model=INWORLD_MODEL, language=lang, speaking_rate=INWORLD_SPEAKING_RATE)
    if INWORLD_VOICE:
        kw["voice"] = INWORLD_VOICE
    if INWORLD_DELIVERY_MODE:
        kw["delivery_mode"] = INWORLD_DELIVERY_MODE
    return inworld.TTS(**kw)


def build_tts(lang: str):
    """Ritorna (motore per la sessione, motori reali su cui cambiare lingua)."""
    primary = _make_tts(TTS_PROVIDER, lang)
    other = "cartesia" if TTS_PROVIDER != "cartesia" else "inworld"
    other_key = "CARTESIA_API_KEY" if other == "cartesia" else "INWORLD_API_KEY"
    if not (TTS_FALLBACK_ENABLED and _env(other_key)):
        return primary, [primary]
    try:
        from livekit.agents import tts as _tts
        fallback = _make_tts(other, lang)
        return _tts.FallbackAdapter([primary, fallback]), [primary, fallback]
    except Exception as e:  # noqa: BLE001
        logger.warning("Riserva TTS non disponibile: %s", type(e).__name__)
        return primary, [primary]


def build_stt(lang: str):
    language = core.stt_language(lang, DEEPGRAM_LANGUAGE)
    kw: dict[str, Any] = dict(model=DEEPGRAM_MODEL, language=language, numerals=True, mip_opt_out=True)
    if language == "it":
        kw["keyterm"] = KEYTERMS  # i termini chiave valgono solo in monolingua italiano
    return deepgram.STT(**kw), language


def _load_vad():
    try:
        return silero.VAD.load(activation_threshold=VAD_ACTIVATION_THRESHOLD)
    except TypeError:
        return silero.VAD.load()


# ───────────────────────── HTTP ─────────────────────────

async def post_json(url: str, payload: dict, headers: Optional[dict] = None) -> int:
    """POST JSON; ritorna lo stato HTTP (0 se la richiesta non parte). Nessun contenuto nei log."""
    try:
        async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT) as s:
            async with s.post(url, json=payload, headers=headers or {}) as resp:
                await resp.read()
                return resp.status
    except Exception as e:  # noqa: BLE001
        logger.warning("POST lead non riuscito: %s", type(e).__name__)
        _report(e)
        return 0


# ───────────────────────── Agente ─────────────────────────

class OdyraWebAgent(Agent):
    def __init__(self, room_name: str, lang: str, tts_targets: list) -> None:
        super().__init__(instructions=core.build_instructions(
            SHARED_PROMPT, lang, emotion_tags=(TTS_PROVIDER == "inworld" and not TTS_FALLBACK_ENABLED)))
        self.room_name = room_name
        self.lang = lang
        self._tts_targets = tts_targets
        self._lang_pending: Optional[str] = None
        self._lang_count = 0
        self._filler_handle = None
        self.lead_sent = False
        self.last_page = ""  # ultima pagina aperta con mostra_pagina (va nel lead come "page")

    # ── lingua: il riconoscimento "multi" rileva, la voce si riallinea dopo N conferme ──

    def apply_language(self, lang: str) -> None:
        self.lang = lang
        for t in self._tts_targets:
            try:
                t.update_options(language=lang)
            except Exception as e:  # noqa: BLE001
                logger.warning("cambio lingua TTS non riuscito: %s", type(e).__name__)
        logger.info("lingua attiva: %s", lang)

    def consider_language(self, detected: str) -> None:
        detected = core.reply_lang(detected)  # fr/de/pl/ro → inglese
        if not detected or detected == self.lang:
            self._lang_pending, self._lang_count = None, 0
            return
        if detected == self._lang_pending:
            self._lang_count += 1
        else:
            self._lang_pending, self._lang_count = detected, 1
        if self._lang_count >= LANG_SWITCH_CONFIRMATIONS:
            self.apply_language(detected)
            self._lang_pending, self._lang_count = None, 0

    async def stt_node(self, audio, model_settings):
        async for ev in Agent.default.stt_node(self, audio, model_settings):
            try:
                if "FINAL_TRANSCRIPT" in str(getattr(ev, "type", "")):
                    alts = getattr(ev, "alternatives", None)
                    if alts:
                        self.consider_language(getattr(alts[0], "language", "") or "")
            except Exception:  # noqa: BLE001
                pass
            yield ev

    async def tts_node(self, text, model_settings):
        """Corregge la pronuncia, toglie i tag se il motore non li capisce e non manda mai
        alla voce un turno fatto solo di tag (evita silenzi e glitch)."""
        keep_tags = TTS_PROVIDER == "inworld" and not TTS_FALLBACK_ENABLED

        async def _gated():
            buf: list[str] = []
            released = False
            async for chunk in text:
                chunk = core.fix_pronunciation(chunk if keep_tags else core.strip_emotion_tags(chunk))
                if released:
                    yield chunk
                    continue
                buf.append(chunk)
                if core.strip_emotion_tags("".join(buf)).strip():
                    released = True
                    for held in buf:
                        yield held
                    buf.clear()

        async for frame in Agent.default.tts_node(self, _gated(), model_settings):
            yield frame

    # ── frase di attesa se uno strumento ci mette più di FILLER_DELAY_S ──

    async def _with_filler(self, context: RunContext, phrase: str, coro):
        async def _later():
            await asyncio.sleep(FILLER_DELAY_S)
            if self._filler_handle is None or self._filler_handle.done():
                self._filler_handle = context.session.say(phrase, allow_interruptions=True, add_to_chat_ctx=False)
        task = asyncio.create_task(_later())
        try:
            return await coro
        finally:
            task.cancel()

    # ── strumenti ──

    @function_tool()
    async def richiedi_contatto(self, context: RunContext, nome: str, telefono: str = "", email: str = "",
                                azienda: str = "", interesse: str = "") -> str:
        """Registra la richiesta di essere ricontattati dal team Odyra. Usalo solo quando il visitatore
        vero lo vuole e dopo aver confermato i dati ad alta voce. Servono il nome e almeno un recapito
        (telefono o email). `azienda`: nome dell'azienda o software house. `interesse`: sintesi in
        massimo venti parole di cosa cerca (es. "software house gestionale saloni, licenze white-label")."""
        data, err = core.validate_contact(nome, telefono, email, azienda, interesse)
        if err:
            return json.dumps({"ok": False, "errore": err, "cosa_fare": core.ERRORI_CONTATTO[err]})
        url, secret = core.lead_target()
        if url is None:
            # Segreto non configurato: non si salva nulla, si invita a prenotare la call.
            logger.info("lead ricevuto (nessuna destinazione configurata)")
            return json.dumps({"ok": False, "errore": "non_registrato",
                               "cosa_fare": "Spiega che per non perdere la richiesta è meglio prenotare subito "
                                            "una call: usa mostra_pagina con pagina 'prenota'."})
        payload = core.lead_payload(data, self.lang, self.last_page)
        headers = {"User-Agent": "odyra-voice/1", "X-Odyra-Secret": secret}
        status = await self._with_filler(context, core.localized(core.FILLER_LEAD, self.lang),
                                         post_json(url, payload, headers))
        ok = 200 <= status < 300
        logger.info("lead inviato: esito=%s", status or "errore")
        if ok:
            self.lead_sent = True
            return json.dumps({"ok": True, "cosa_fare": "Conferma che il team lo ricontatta entro un giorno lavorativo. "
                                                        "Se vuole, può anche prenotare subito una call."})
        return json.dumps({"ok": False, "errore": "invio_non_riuscito",
                           "cosa_fare": "Scusati in una frase e proponi di prenotare la call: "
                                        "mostra_pagina con pagina 'prenota'."})

    @function_tool()
    async def mostra_pagina(self, context: RunContext, pagina: str) -> str:
        """Apre una pagina del sito sullo schermo del visitatore, senza interrompere la conversazione.
        Dillo a voce mentre lo fai. Valori ammessi per `pagina`: home, prezzi, partner, prenota (per
        prenotare una call con il team), casi (casi di successo), boss (il caso BOSS), tecnologie, contatti."""
        path = core.resolve_page(pagina, self.lang, PAGES)
        if not path:
            return json.dumps({"ok": False, "errore": "pagina_non_ammessa", "valide": list(core.PAGINE)})
        try:
            room = get_job_context().room
            await room.local_participant.publish_data(
                json.dumps(core.navigate_payload(path)).encode("utf-8"), reliable=True, topic="ui")
            self.last_page = path
            return json.dumps({"ok": True, "pagina": pagina})
        except Exception as e:  # noqa: BLE001
            logger.warning("mostra_pagina non riuscita: %s", type(e).__name__)
            return json.dumps({"ok": False, "errore": "navigazione_non_riuscita"})


# ───────────────────────── Ciclo di vita ─────────────────────────

def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = _load_vad()
    if PROMPT_MISSING:
        logger.warning("prompt condiviso incompleto: mancano %s (cartella %s)", PROMPT_MISSING, AGENTE_DIR)
    logger.info("pronto: agent=%s llm=%s tts=%s avatar=%s", AGENT_NAME, LLM_PROVIDER, TTS_PROVIDER, AVATAR_ENABLED)


def _is_agent(participant) -> bool:
    try:
        from livekit import rtc
        return participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_AGENT
    except Exception:  # noqa: BLE001
        return False


async def entrypoint(ctx: JobContext) -> None:
    lang = core.lang_from_metadata(ctx.job.metadata, DEFAULT_LANG)  # it/es/en, le altre → en
    heard = core.lang_from_metadata(ctx.job.metadata, lang, reply=False)  # per capire anche pl/ro
    logger.info("nuova sessione lang=%s", lang)
    await ctx.connect()

    loop = asyncio.get_running_loop()
    state: dict[str, Any] = {"start": loop.time(), "last": loop.time(), "closing": False,
                             "reason": "completed", "awaiting_reply_since": None}

    stt, stt_lang = build_stt(heard)
    tts_engine, tts_targets = build_tts(lang)
    session_kw: dict[str, Any] = dict(
        stt=stt,
        llm=build_llm(),
        tts=tts_engine,
        vad=ctx.proc.userdata.get("vad") or _load_vad(),
        turn_detection=("vad" if TURN_DETECTION == "vad" else inference.TurnDetector()),
        min_endpointing_delay=MIN_ENDPOINTING_DELAY,
        max_endpointing_delay=MAX_ENDPOINTING_DELAY,
        min_interruption_duration=MIN_INTERRUPTION_DURATION,
        min_interruption_words=MIN_INTERRUPTION_WORDS,
        preemptive_generation=PREEMPTIVE_GENERATION,
        resume_false_interruption=True,
        false_interruption_timeout=FALSE_INTERRUPTION_TIMEOUT_S,
    )
    session = AgentSession(**session_kw)
    agent = OdyraWebAgent(ctx.room.name, lang, tts_targets)
    logger.info("stt=%s", stt_lang)

    def close(reason: str) -> None:
        if state["closing"]:
            return
        state["closing"], state["reason"] = True, reason
        logger.info("chiusura: %s dopo %.0fs", reason, loop.time() - state["start"])
        ctx.shutdown(reason=reason)

    def touch(*_: Any) -> None:
        state["last"] = loop.time()

    def on_transcript(ev: Any) -> None:
        # Frase finale vera del visitatore: da qui l'agente deve rispondere (serve al controllo "bloccato").
        if getattr(ev, "is_final", False) and (getattr(ev, "transcript", "") or "").strip():
            touch()
            state["awaiting_reply_since"] = loop.time()

    def on_agent_state(ev: Any) -> None:
        touch()
        if getattr(ev, "new_state", "") in ("thinking", "speaking"):
            state["awaiting_reply_since"] = None

    session.on("user_input_transcribed", on_transcript)
    session.on("agent_state_changed", on_agent_state)
    session.on("user_state_changed", touch)
    ctx.room.on("participant_disconnected", lambda p: None if _is_agent(p) else close("visitor_left"))

    async def _delete_room(*_: Any) -> None:
        # Chiude davvero la stanza (libera anche l'eventuale avatar).
        try:
            from livekit import api
            await ctx.api.room.delete_room(api.DeleteRoomRequest(room=ctx.room.name))
        except Exception as e:  # noqa: BLE001
            logger.warning("chiusura stanza non riuscita: %s", type(e).__name__)

    ctx.add_shutdown_callback(_delete_room)

    avatar = None
    if AVATAR_ENABLED:
        try:
            from livekit.plugins import tavus
            avatar = tavus.AvatarSession(replica_id=_env("TAVUS_REPLICA_ID"), persona_id=_env("TAVUS_PERSONA_ID"))
            await avatar.start(session, room=ctx.room)
        except Exception as e:  # noqa: BLE001
            logger.warning("avatar non avviato, proseguo solo voce: %s", type(e).__name__)
            avatar = None

    if avatar is not None:
        await session.start(agent=agent, room=ctx.room, room_output_options=RoomOutputOptions(audio_enabled=False))
    else:
        await session.start(agent=agent, room=ctx.room)
        try:  # suono "sto pensando" solo senza avatar (altrimenti due canali audio)
            await BackgroundAudioPlayer(thinking_sound=THINKING_SOUND).start(room=ctx.room, agent_session=session)
        except Exception as e:  # noqa: BLE001
            logger.warning("suono di attesa non avviato: %s", type(e).__name__)

    try:
        await asyncio.wait_for(ctx.wait_for_participant(), timeout=30.0)
    except asyncio.TimeoutError:
        close("no_visitor")
        return

    # Saluto fisso (niente giro di LLM: parte subito) con l'avviso che è un'AI.
    try:
        await session.say(core.localized(core.GREETINGS, lang), allow_interruptions=True)
    except Exception as e:  # noqa: BLE001
        logger.warning("saluto non riuscito: %s", type(e).__name__)
        _report(e)
    touch()

    async def watchdog() -> None:
        """Un solo controllo al secondo: durata massima, silenzio, agente bloccato."""
        while not state["closing"]:
            await asyncio.sleep(1)
            now = loop.time()
            if session.agent_state in ("thinking", "speaking"):
                state["last"] = now
            waiting = state["awaiting_reply_since"]
            if waiting is not None and session.user_state != "speaking" and now - waiting >= STUCK_TIMEOUT_S:
                logger.warning("nessuna risposta da %.0fs", now - waiting)
                close("stuck")
                return
            if now - state["start"] >= MAX_DURATION_S:
                msg, reason = core.GOODBYE_MAX, "max_duration"
            elif now - state["last"] > SILENCE_TIMEOUT_S:
                msg, reason = core.GOODBYE_SILENCE, "silence_timeout"
            else:
                continue
            try:
                await session.say(core.localized(msg, agent.lang), allow_interruptions=False)
            except Exception:  # noqa: BLE001
                pass
            close(reason)
            return

    wd = asyncio.create_task(watchdog(), name="watchdog")

    async def _stop_watchdog(*_: Any) -> None:
        wd.cancel()
        if _SENTRY is not None:
            try:
                _SENTRY.flush(timeout=2)
            except Exception:  # noqa: BLE001
                pass

    ctx.add_shutdown_callback(_stop_watchdog)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name=AGENT_NAME))
