"""Chat status remains conversational and stops when the owning run finishes."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from gateway.config import Platform
from gateway.display_config import resolve_display_setting
from gateway.run import GatewayRunner
from gateway.session import SessionSource
from gateway.status_phrases import choose_status_phrase, resolve_status_phrase_catalog


@pytest.mark.asyncio
@pytest.mark.parametrize("platform,finishes_early", [("slack", False), ("slack", True), ("telegram", False)])
async def test_progress_timing_is_scoped_and_never_outlives_run(monkeypatch, platform, finishes_early):
    import gateway.run as facade
    import gateway.run_turn as turn

    config = {"display": {"platforms": {"slack": {
        "long_running_initial_delay": 5,
        "long_running_interval": 60,
        "status_phrases": {"mode": "replace", "generic": ["Jeg er gået i gang."],
                           "status": ["Jeg arbejder stadig på det."]},
    }}}}
    catalog = resolve_status_phrase_catalog(config, platform)
    runner = object.__new__(GatewayRunner)
    adapter = SimpleNamespace(send=AsyncMock(return_value=SimpleNamespace(success=True, message_id="status-1")),
                              edit_message=AsyncMock(return_value=SimpleNamespace(success=True)))
    runner._delivery_adapter_for = lambda source: adapter
    executor = SimpleNamespace(done=lambda: finishes_early or len(delays) >= 3)
    runner._agent_activity_summary = lambda agent: {"current_tool": "terminal SECRET", "api_call_count": 4}
    disp = SimpleNamespace(user_config=config, platform_key=platform,
        resolve_display_setting=resolve_display_setting,
        _display_surface_mode=lambda *a, **kw: "generic",
        _generic_status_phrase=lambda kind: choose_status_phrase(kind, catalog=catalog))
    ctx = SimpleNamespace(source=SessionSource(platform=Platform(platform), chat_id="C_TEST", user_id="U_TEST"),
        session_key=None, agent_holder=[object()], _status_thread_metadata={}, _cleanup_progress=False)
    delays = []

    async def sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(turn.asyncio, "sleep", sleep)
    monkeypatch.setattr(facade, "_float_env", lambda *a: 180)
    await runner._run_agent_notify_long_running(disp, ctx, [executor])
    if finishes_early:
        assert delays == [5]
        adapter.send.assert_not_awaited()
        adapter.edit_message.assert_not_awaited()
    else:
        assert delays == ([5, 60, 60] if platform == "slack" else [180, 180, 180])
        adapter.send.assert_awaited_once()
        adapter.edit_message.assert_awaited_once()
        assert adapter.send.call_args.kwargs["metadata"]["_interim_send"] is True
        if platform == "slack":
            assert adapter.send.call_args.args[1] == "Jeg er gået i gang."
            assert adapter.edit_message.call_args.args[2] == "Jeg arbejder stadig på det."
        assert "SECRET" not in str(adapter.send.call_args) + str(adapter.edit_message.call_args)


@pytest.mark.parametrize("mode", ["steer", "queue", "interrupt"])
def test_configured_busy_ack_hides_internal_details_and_command_hints(monkeypatch, mode):
    import gateway.run as facade

    text = "Tak, jeg har fået din besked og tager den med."
    config = {"display": {"platforms": {"slack": {"busy_ack_text": text}}}}
    monkeypatch.setattr(facade, "_load_gateway_config", lambda: config)
    runner = object.__new__(GatewayRunner)
    event = SimpleNamespace(source=SessionSource(platform=Platform.SLACK, chat_id="C_TEST"))
    agent = Mock()
    result = runner._compose_busy_ack_message(event, 10, None, agent,
        is_steer_mode=mode == "steer", is_queue_mode=mode == "queue", is_redirect_mode=False,
        demoted_for_subagents=False, demoted_for_compression=False)
    assert result == text
    agent.get_activity_summary.assert_not_called()
