"""Local parsing and SDK compatibility; no HTTP or provider requests."""
import pytest
import logging
import time

from opentelemetry.trace import TraceState


def test_invalid_tracestate_does_not_block_worker(caplog):
    caplog.set_level(logging.CRITICAL, logger="opentelemetry.trace.span")
    started = time.monotonic()
    result = TraceState.from_header(["a=b" + " " * 80000 + "x"])
    elapsed = time.monotonic() - started
    assert list(result.items()) == []
    assert elapsed < 2, f"tracestate parsing blocked for {elapsed:.3f}s"


def test_valid_tracestate_preserves_values():
    assert list(TraceState.from_header(["alpha=one \t, beta=two"]).items()) == [
        ("alpha", "one"), ("beta", "two")]


def test_compatible_mistral_keeps_audio_methods_without_network():
    # mistral er en lazy PM-extra og findes ikke i alle runtimes.
    Mistral = pytest.importorskip("mistralai.client").Mistral

    with Mistral(api_key="test-only-not-a-real-key") as client:
        assert callable(client.audio.speech.complete)
        assert callable(client.audio.transcriptions.complete)
