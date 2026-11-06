"""KPA: thread_reply_channels lægger svar i tråden i udvalgte kanaler; DM og øvrige kanaler forbliver flade."""

from types import SimpleNamespace

from plugins.platforms.slack.adapter import SlackAdapter

KANAL = "C0CAWPLKXNW"


def _a(extra=None):
    a = object.__new__(SlackAdapter)
    a.config = SimpleNamespace(extra={"reply_in_thread": False, "thread_reply_channels": KANAL, **(extra or {})})
    a._thread_reply_ts = set()
    a._REACTING_MESSAGE_IDS_MAX = 5000
    a._extra_or_env_channel_set = lambda key, env, coerce_scalar=False: (
        set(str(a.config.extra.get(key) or "").split(",")) - {""})
    return a


def test_session_ts_i_trad_kanal_registrerer_besked():
    a = _a()
    assert a._session_thread_ts({"channel": KANAL}, "1.1", False, {}) == "1.1"
    assert "1.1" in a._thread_reply_ts


def test_andre_kanaler_forbliver_flade():
    a = _a()
    assert a._session_thread_ts({"channel": "C999"}, "2.2", False, {}) is None
    assert "2.2" not in a._thread_reply_ts


def test_svar_gaar_i_traaden_kun_for_registreret_besked():
    a = _a()
    a._session_thread_ts({"channel": KANAL}, "1.1", False, {})
    assert a._resolve_thread_ts("1.1", {"thread_id": "1.1"}) == "1.1"        # i tråden
    assert a._resolve_thread_ts("3.3", {"thread_id": "3.3"}) is None         # DM/andre: flat


def test_ægte_traad_under_standardindstilling_er_uaendret():
    a = _a({"reply_in_thread": True, "thread_reply_channels": ""})
    assert a._resolve_thread_ts("5.5", {}) == "5.5"
