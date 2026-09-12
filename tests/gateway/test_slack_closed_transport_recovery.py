"""Closed Slack transports must recover without live Slack or gateway state."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiohttp
import pytest

from gateway.config import PlatformConfig
from plugins.platforms.slack import adapter as slack


@pytest.fixture
def adapter():
    result = slack.SlackAdapter(PlatformConfig(enabled=True, token="xoxb-test"))
    result._running = True
    result._app_token = "xapp-test"
    result._proxy_url = None
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_part", ["client", "session"])
async def test_closed_transport_overrides_stale_connected_flag(adapter, closed_part):
    client = SimpleNamespace(
        closed=closed_part == "client",
        aiohttp_client_session=SimpleNamespace(closed=closed_part == "session"),
        is_connected=AsyncMock(return_value=True),
    )
    adapter._handler = SimpleNamespace(client=client)
    assert await adapter._socket_transport_connected() is False


@pytest.mark.asyncio
async def test_teardown_disables_sdk_reconnect_before_cancelling_tasks(adapter):
    started = asyncio.Event()
    observed = []
    client = SimpleNamespace(closed=False, auto_reconnect_enabled=True)

    async def receiver():
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            observed.append((client.closed, client.auto_reconnect_enabled))

    client.message_receiver = asyncio.create_task(receiver())
    adapter._handler = SimpleNamespace(client=client, close_async=AsyncMock())
    await started.wait()
    await adapter._stop_socket_mode_handler()
    assert observed == [(True, False)]


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["timeout", "exception"])
async def test_stalled_close_does_not_block_recovery(adapter, monkeypatch, failure):
    monkeypatch.setattr(slack, "_SOCKET_TASK_CANCEL_TIMEOUT_S", 0.03)
    closed = asyncio.Event()

    async def stalled_close():
        try:
            if failure == "exception":
                raise RuntimeError("closed websocket")
            await asyncio.Event().wait()
        finally:
            closed.set()

    async with aiohttp.ClientSession() as session:
        client = SimpleNamespace(aiohttp_client_session=session)
        adapter._handler = SimpleNamespace(client=client, close_async=stalled_close)
        await asyncio.wait_for(adapter._stop_socket_mode_handler(), timeout=2)
        assert closed.is_set()
        assert session.closed
