"""Prove dell'agente vocale, senza rete e senza chiavi.

    cd agente-voce && python -m unittest -v test_agent      (oppure: pytest -q)

Le prove su core.py girano con la sola libreria standard. Quelle su agent.py partono solo se
i pacchetti di requirements.txt sono installati (altrimenti vengono saltate, non falliscono).
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402

try:
    import livekit.agents  # noqa: F401
    HAS_LIVEKIT = True
except Exception:  # noqa: BLE001
    HAS_LIVEKIT = False


class TestPrompt(unittest.TestCase):
    def test_trova_la_cartella_condivisa_del_repository(self):
        d = core.find_agente_dir(here=HERE)
        self.assertIsNotNone(d, "agente/ non trovata accanto ad agente-voce/")
        self.assertEqual(d.resolve(), (HERE.parent / "agente").resolve())

    def test_carica_istruzioni_e_conoscenza_in_ordine(self):
        with tempfile.TemporaryDirectory() as t:
            Path(t, "istruzioni.md").write_text("ISTRUZIONI", encoding="utf-8")
            Path(t, "conoscenza.md").write_text("CONOSCENZA", encoding="utf-8")
            txt, missing = core.load_shared_prompt(Path(t))
        self.assertEqual(missing, [])
        self.assertLess(txt.index("ISTRUZIONI"), txt.index("CONOSCENZA"))

    def test_file_mancanti_segnaposto_e_avviso(self):
        with tempfile.TemporaryDirectory() as t:
            txt, missing = core.load_shared_prompt(Path(t))
            self.assertEqual(txt, core.PROMPT_SEGNAPOSTO)
            self.assertEqual(missing, ["istruzioni.md", "conoscenza.md"])
            Path(t, "istruzioni.md").write_text("SOLO ISTRUZIONI", encoding="utf-8")
            txt, missing = core.load_shared_prompt(Path(t))
            self.assertEqual((txt, missing), ("SOLO ISTRUZIONI", ["conoscenza.md"]))
        self.assertEqual(core.load_shared_prompt(None)[0], core.PROMPT_SEGNAPOSTO)

    def test_variabile_agente_dir(self):
        with tempfile.TemporaryDirectory() as t:
            Path(t, "conoscenza.md").write_text("x", encoding="utf-8")
            with mock.patch.dict(os.environ, {"AGENTE_DIR": t}):
                self.assertEqual(core.find_agente_dir(here=Path("/inesistente")), Path(t))

    def test_prompt_completo_con_regole_voce_e_contesto(self):
        now = datetime(2026, 11, 11, 10, 5, tzinfo=core.TZ_ROME)
        p = core.build_instructions("BASE", "es", now=now)
        self.assertTrue(p.startswith("BASE"))
        self.assertIn("REGOLE PER LA VOCE", p)
        self.assertIn("mostra_pagina", p)
        self.assertIn("a parole", p)
        self.assertIn("mercoledì 11 novembre 2026, ore 10:05", p)
        self.assertIn("canale = voce", p)
        self.assertIn(": es.", p)
        self.assertIn("Non usare tag", p)
        self.assertIn("[happy]", core.build_instructions("BASE", emotion_tags=True))

    def test_regole_voce_senza_nomi_di_terzi(self):
        vietati = ["livekit", "openai", "anthropic", "claude", "gpt", "deepgram", "cartesia", "inworld",
                   "tavus", "supabase", "n8n", "railway", "lovable", "meta "]
        testi = [core.REGOLE_VOCE, core.PROMPT_SEGNAPOSTO, *core.GREETINGS.values(),
                 *core.GOODBYE_SILENCE.values(), *core.GOODBYE_MAX.values()]
        for t in testi:
            for v in vietati:
                self.assertNotIn(v, t.lower(), f"'{v}' in un testo detto al visitatore")


class TestPagine(unittest.TestCase):
    ATTESI = {"home": "/", "prezzi": "/prezzi", "partner": "/partner", "prenota": "/prenota",
              "casi": "/lavori", "boss": "/case/boss-italia", "tecnologie": "/tecnologie",
              "contatti": "/contatti"}

    def test_whitelist_esatta(self):
        self.assertEqual(core.PAGINE, self.ATTESI)

    def test_chiavi_e_sinonimi(self):
        for k, v in self.ATTESI.items():
            self.assertEqual(core.resolve_page(k), v)
            self.assertEqual(core.resolve_page(k.upper() + " "), v)
        self.assertEqual(core.resolve_page("casi studio"), "/lavori")
        self.assertEqual(core.resolve_page("case_boss_italia"), "/case/boss-italia")
        self.assertEqual(core.resolve_page("calendario"), "/prenota")
        self.assertEqual(core.resolve_page("/prezzi"), "/prezzi")

    def test_pagine_non_ammesse(self):
        for bad in ["", None, "eva", "case_sportit", "/case/sportit", "/capabilities", "/eventi",
                    "https://example.com", "javascript:alert(1)", "//evil.example", "../../etc"]:
            self.assertIsNone(core.resolve_page(bad), bad)

    def test_percorsi_per_lingua_da_pagine_json(self):
        with tempfile.TemporaryDirectory() as t:
            Path(t, "pagine.json").write_text(json.dumps({
                "_nota": "x", "partner": {"it": "/partner", "es": "/es/socios"},
                "casi": {"es": "https://evil.example"}, "nuova": {"it": "/segreta"}}), encoding="utf-8")
            pages = core.load_pages(Path(t))
        self.assertNotIn("nuova", pages)  # il file non allarga la whitelist
        self.assertEqual(core.resolve_page("partner", "es", pages), "/es/socios")
        self.assertEqual(core.resolve_page("partner", "it", pages), "/partner")
        self.assertEqual(core.resolve_page("casi", "es", pages), "/lavori")  # percorso esterno scartato
        self.assertEqual(core.resolve_page("prezzi", "en", pages), "/prezzi")

    def test_pagine_json_del_repository_coerente(self):
        p = HERE.parent / "agente" / "pagine.json"
        if not p.is_file():
            self.skipTest("agente/pagine.json non ancora presente")
        data = json.loads(p.read_text(encoding="utf-8"))
        for k, v in self.ATTESI.items():
            self.assertEqual(data[k]["it"], v, k)
        self.assertEqual(set(core.load_pages(p.parent)), set(self.ATTESI))

    def test_messaggio_per_il_sito(self):
        self.assertEqual(json.loads(json.dumps(core.navigate_payload("/prezzi"))),
                         {"action": "navigate", "path": "/prezzi"})


class TestContatto(unittest.TestCase):
    def test_valido_con_telefono(self):
        d, err = core.validate_contact(" Mario  Rossi ", "+39 333 12 34 567", "", "Salone\nX", "beta")
        self.assertIsNone(err)
        self.assertEqual(d["nome"], "Mario Rossi")
        self.assertEqual(d["telefono"], "+393331234567")
        self.assertEqual(d["azienda"], "Salone X")

    def test_email_dettata_a_voce(self):
        d, err = core.validate_contact("Anna", email="anna punto bianchi chiocciola gmail punto com")
        self.assertIsNone(err)
        self.assertEqual(d["email"], "anna.bianchi@gmail.com")
        # "at" dentro una parola non va toccato
        self.assertEqual(core.normalize_email("matteo@studio.it"), "matteo@studio.it")

    def test_errori(self):
        self.assertEqual(core.validate_contact("", "3331234567")[1], "manca_nome")
        self.assertEqual(core.validate_contact("Mario")[1], "manca_recapito")
        self.assertEqual(core.validate_contact("Mario", telefono="123")[1], "telefono_non_valido")
        self.assertEqual(core.validate_contact("Mario", email="mario@")[1], "email_non_valida")
        # uno dei due valido basta
        self.assertIsNone(core.validate_contact("Mario", telefono="12", email="m@x.it")[1])
        for e in ("manca_nome", "manca_recapito", "telefono_non_valido", "email_non_valida"):
            self.assertIn(e, core.ERRORI_CONTATTO)

    def test_telefono(self):
        self.assertEqual(core.normalize_phone("0039 02 1234 5678"), "+390212345678")
        self.assertEqual(core.normalize_phone("333-123.4567"), "3331234567")
        self.assertEqual(core.normalize_phone("1" * 16), "")

    def test_lunghezze_massime(self):
        d, _ = core.validate_contact("N" * 500, "3331234567", interesse="i" * 1000)
        self.assertEqual(len(d["nome"]), 80)
        self.assertEqual(len(d["interesse"]), 300)

    def test_destinazione_del_lead(self):
        self.assertEqual(core.lead_target({}), (None, None))  # senza segreto non si invia
        self.assertEqual(core.lead_target({"SITE_LEAD_URL": "https://s/api"}), (None, None))
        self.assertEqual(core.lead_target({"VOICE_LEAD_SECRET": "k"}), (core.SITE_LEAD_URL_DEFAULT, "k"))
        self.assertEqual(core.SITE_LEAD_URL_DEFAULT, "https://odyrasystemautomation.it/api/voce/lead")
        self.assertEqual(core.lead_target({"VOICE_LEAD_SECRET": "k", "SITE_LEAD_URL": "http://localhost:8090/api/voce/lead"}),
                         ("http://localhost:8090/api/voce/lead", "k"))
        self.assertEqual(core.lead_target({"VOICE_LEAD_SECRET": "k", "SITE_LEAD_URL": "file:///etc/passwd"}), (None, None))

    def test_corpo_per_il_sito(self):
        d, _ = core.validate_contact("Mario", "333 1234567", "", "ACME", "")
        b = core.lead_payload(d, "es", "/prezzi")
        self.assertEqual(set(b), {"name", "email", "phone", "company", "need", "message", "lang", "page"})
        self.assertEqual((b["name"], b["phone"], b["company"], b["lang"], b["page"]),
                         ("Mario", "3331234567", "ACME", "es", "/prezzi"))
        self.assertTrue(b["need"])  # il sito vuole need o message
        self.assertNotIn("page", core.lead_payload(d, "it"))
        self.assertNotIn("privacy", b)


class TestLingua(unittest.TestCase):
    def test_metadati(self):
        self.assertEqual(core.lang_from_metadata('{"lang": "es"}'), "es")
        self.assertEqual(core.lang_from_metadata('{"lang": "EN-gb"}'), "en")
        self.assertEqual(core.lang_from_metadata('{"lang": "fr"}'), "en")  # altre lingue: inglese
        self.assertEqual(core.lang_from_metadata('{"lang": "pl"}', reply=False), "pl")
        self.assertEqual(core.lang_from_metadata('{"lang": "zz"}'), "it")
        self.assertEqual(core.lang_from_metadata("non json"), "it")
        self.assertEqual(core.lang_from_metadata("[1,2]"), "it")
        self.assertEqual(core.lang_from_metadata("", default="en"), "en")

    def test_lingua_di_risposta(self):
        self.assertEqual([core.reply_lang(c) for c in ("it", "es", "en", "de", "ro", "xx", "")],
                         ["it", "es", "en", "en", "en", "", ""])
        self.assertIn("rispondi in inglese", core.build_instructions("B").lower())

    def test_stessa_lista_del_sito(self):
        server = (HERE.parent / "server" / "odyra_server.py")
        if server.is_file():
            self.assertIn("VOICE_LANGS = " + repr(core.SUPPORTED_LANGS), server.read_text(encoding="utf-8"))

    def test_riconoscimento(self):
        self.assertEqual(core.stt_language("it"), "multi")
        self.assertEqual(core.stt_language("pl"), "pl")
        self.assertEqual(core.stt_language("es", override="it"), "it")

    def test_testi_in_ogni_lingua_con_avviso_ai(self):
        parole_ai = {"it": "intelligenza artificiale", "en": "artificial intelligence", "es": "inteligencia artificial"}
        for lang in core.REPLY_LANGS:
            for m in (core.GREETINGS, core.GOODBYE_SILENCE, core.GOODBYE_MAX, core.FILLER_LEAD):
                self.assertIn(lang, m)
            self.assertIn(parole_ai[lang], core.GREETINGS[lang].lower())
        self.assertEqual(core.localized(core.GREETINGS, "de"), core.GREETINGS["en"])
        self.assertEqual(core.localized(core.GREETINGS, "xx"), core.GREETINGS["it"])

    def test_testo_per_la_voce(self):
        self.assertEqual(core.strip_emotion_tags("[happy] Ciao"), " Ciao")
        self.assertEqual(core.fix_pronunciation("Benvenuto in Odyra."), "Benvenuto in Odira.")


@unittest.skipUnless(HAS_LIVEKIT, "pacchetti di requirements.txt non installati")
class TestModuloAgente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import agent
        cls.agent = agent

    def test_nome_e_prompt(self):
        self.assertEqual(self.agent.AGENT_NAME, os.getenv("LIVEKIT_AGENT_NAME", "odyra_web"))
        self.assertTrue(self.agent.SHARED_PROMPT)

    def _agente(self):
        return self.agent.OdyraWebAgent("stanza", "it", [])

    def test_strumenti_registrati(self):
        names = {getattr(t, "id", None) or getattr(t, "name", None) or getattr(getattr(t, "info", None), "name", None)
                 for t in self._agente().tools}
        self.assertTrue({"richiedi_contatto", "mostra_pagina"} <= names, names)

    def test_mostra_pagina_pubblica_sul_topic_ui(self):
        sent = []

        class LP:
            async def publish_data(self, payload, reliable=True, topic=""):
                sent.append((json.loads(payload), topic))

        room = mock.Mock()
        room.local_participant = LP()
        a = self._agente()
        with mock.patch.object(self.agent, "get_job_context", return_value=mock.Mock(room=room)):
            ok = json.loads(asyncio.run(a.mostra_pagina(None, "prezzi")))
            ko = json.loads(asyncio.run(a.mostra_pagina(None, "eva")))
        self.assertTrue(ok["ok"])
        self.assertFalse(ko["ok"])
        self.assertEqual(sent, [({"action": "navigate", "path": "/prezzi"}, "ui")])

    def test_contatto_senza_destinazione_non_invia(self):
        a = self._agente()
        with mock.patch.dict(os.environ, {"VOICE_LEAD_SECRET": ""}), \
                mock.patch.object(self.agent, "post_json") as post:
            r = json.loads(asyncio.run(a.richiedi_contatto(None, "Mario", "3331234567")))
        post.assert_not_called()
        self.assertEqual(r["errore"], "non_registrato")
        self.assertIn("prenota", r["cosa_fare"])

    def test_contatto_non_valido_non_invia(self):
        a = self._agente()
        with mock.patch.object(self.agent, "post_json") as post:
            r = json.loads(asyncio.run(a.richiedi_contatto(None, "Mario")))
        post.assert_not_called()
        self.assertEqual(r["errore"], "manca_recapito")

    def test_contatto_inviato_al_sito(self):
        a = self._agente()
        a.last_page = "/prezzi"
        calls = []

        async def fake_post(url, payload, headers=None):
            calls.append((url, payload, headers))
            return 200

        async def no_filler(ctx, phrase, coro):
            return await coro

        with mock.patch.dict(os.environ, {"VOICE_LEAD_SECRET": "segreto", "SITE_LEAD_URL": ""}), \
                mock.patch.object(self.agent, "post_json", fake_post), \
                mock.patch.object(a, "_with_filler", no_filler):
            r = json.loads(asyncio.run(a.richiedi_contatto(None, "Mario", email="m@x.it", azienda="ACME",
                                                           interesse="beta per 50 centri")))
        self.assertTrue(r["ok"])
        url, payload, headers = calls[0]
        self.assertEqual(url, "https://odyrasystemautomation.it/api/voce/lead")
        self.assertEqual(headers["X-Odyra-Secret"], "segreto")
        self.assertEqual((payload["name"], payload["email"], payload["company"], payload["need"], payload["page"]),
                         ("Mario", "m@x.it", "ACME", "beta per 50 centri", "/prezzi"))

    def test_invio_fallito_porta_a_prenota(self):
        a = self._agente()

        async def fake_post(url, payload, headers=None):
            return 0

        async def no_filler(ctx, phrase, coro):
            return await coro

        with mock.patch.dict(os.environ, {"VOICE_LEAD_SECRET": "s"}), \
                mock.patch.object(self.agent, "post_json", fake_post), mock.patch.object(a, "_with_filler", no_filler):
            r = json.loads(asyncio.run(a.richiedi_contatto(None, "Mario", "3331234567")))
        self.assertFalse(r["ok"])
        self.assertIn("prenota", r["cosa_fare"])

    def test_timeout_http(self):
        self.assertEqual(self.agent.HTTP_TIMEOUT.total, 8)

    def test_nessun_dato_personale_nei_log(self):
        a = self._agente()

        async def fake_post(url, payload, headers=None):
            return 200

        async def no_filler(ctx, phrase, coro):
            return await coro

        with mock.patch.dict(os.environ, {"VOICE_LEAD_SECRET": "segreto-xyz"}), \
                mock.patch.object(self.agent, "post_json", fake_post), mock.patch.object(a, "_with_filler", no_filler), \
                self.assertLogs("odyra_web", level="INFO") as logs:
            asyncio.run(a.richiedi_contatto(None, "Mario Rossi", "3331234567", "mario@x.it", "ACME"))
        testo = "\n".join(logs.output)
        for dato in ("Mario", "3331234567", "mario@x.it", "ACME", "segreto-xyz"):
            self.assertNotIn(dato, testo)

    def test_cambio_lingua_dopo_conferme(self):
        a = self._agente()
        t = mock.Mock()
        a._tts_targets = [t]
        a.consider_language("en")
        self.assertEqual(a.lang, "it")
        a.consider_language("en")
        self.assertEqual(a.lang, "en")
        t.update_options.assert_called_with(language="en")
        a.consider_language("es")
        a.consider_language("es")
        self.assertEqual(a.lang, "es")
        a.consider_language("de")
        a.consider_language("de")
        self.assertEqual(a.lang, "en")  # tedesco: si risponde in inglese


if __name__ == "__main__":
    unittest.main()
