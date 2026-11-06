"""KPA: Flemse ignorerer en besked, når en anden allerede har sat :eyes: på den."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import plugins.platforms.slack.adapter as _m
from plugins.platforms.slack.adapter import SlackAdapter


def _adapter(reactions=None, error=None, extra=None):
    a = object.__new__(SlackAdapter)
    a._app = MagicMock()
    a._bot_user_id = "UBOT"
    a.config = SimpleNamespace(extra=extra or {})
    client = MagicMock()
    if error:
        client.reactions_get = AsyncMock(side_effect=error)
    else:
        client.reactions_get = AsyncMock(return_value={"message": {"reactions": reactions or []}})
    a._get_client = lambda *args, **kw: client
    return a


def _run(a):
    return asyncio.run(a._claimed_by_foreign_eyes("C1", "1.1", "T1", "UBOT"))


def test_human_eyes_means_ignore():
    assert _run(_adapter([{"name": "eyes", "users": ["U123"]}])) is True


def test_own_eyes_only_does_not_block():
    assert _run(_adapter([{"name": "eyes", "users": ["UBOT"]}])) is False


def test_other_emoji_and_no_reactions_do_not_block():
    assert _run(_adapter([{"name": "thumbsup", "users": ["U123"]}])) is False
    assert _run(_adapter([])) is False


def test_missing_scope_fails_open():
    assert _run(_adapter(error=RuntimeError("missing_scope"))) is False


def test_can_be_switched_off():
    a = _adapter([{"name": "eyes", "users": ["U123"]}], extra={"ignore_if_eyes": False})
    assert _run(a) is False
