"""Tests for the utilisation client using a mocked HTTP response.

No network is touched: ``urllib.request.urlopen`` is monkeypatched to return a
canned payload, so these tests cover the parsing, the trust-but-verify logic,
and the error handling.
"""

import json
import urllib.error
from contextlib import contextmanager

import pytest

from traffic_light import client


@contextmanager
def _fake_urlopen(payload: dict):
    class _Resp:
        def __enter__(self_inner):
            return self_inner

        def __exit__(self_inner, *exc):
            return False

        def read(self_inner):
            return json.dumps(payload).encode("utf-8")

    yield _Resp()


def _patch(monkeypatch, payload):
    monkeypatch.setattr(
        client.urllib.request,
        "urlopen",
        lambda *a, **k: _fake_urlopen(payload).__enter__(),
    )


def test_fetch_utilization_parses(monkeypatch):
    payload = {"garageId": "garage1", "totalSpots": 350, "occupied": 287,
               "free": 63, "utilization": 0.82, "light": "yellow"}
    _patch(monkeypatch, payload)
    result = client.fetch_utilization("https://api.example", "garage1")
    assert result == payload


def test_current_light_uses_backend_value(monkeypatch):
    _patch(monkeypatch, {"utilization": 0.82, "light": "yellow"})
    assert client.current_light("https://api.example") == "yellow"


def test_current_light_derives_when_no_backend_light(monkeypatch):
    _patch(monkeypatch, {"utilization": 0.95})
    assert client.current_light("https://api.example") == "red"


def test_current_light_detects_threshold_drift(monkeypatch):
    # Backend says green but 0.82 should classify as yellow -> drift.
    _patch(monkeypatch, {"utilization": 0.82, "light": "green"})
    with pytest.raises(client.UtilizationError, match="drift"):
        client.current_light("https://api.example", verify=True)


def test_current_light_skips_verify_when_disabled(monkeypatch):
    _patch(monkeypatch, {"utilization": 0.82, "light": "green"})
    assert client.current_light("https://api.example", verify=False) == "green"


def test_fetch_utilization_wraps_network_error(monkeypatch):
    def _boom(*a, **k):
        raise urllib.error.URLError("no route to host")

    monkeypatch.setattr(client.urllib.request, "urlopen", _boom)
    with pytest.raises(client.UtilizationError):
        client.fetch_utilization("https://api.example")
