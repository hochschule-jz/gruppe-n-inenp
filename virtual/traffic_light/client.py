"""Consume the backend utilisation API and derive the entrance traffic light.

Reads ``GET {api_base}/garages/{garageId}/utilization`` (defined in
``backend/api/``), which already returns an aggregated payload including both
``utilization`` and a server-computed ``light``. This component trusts that
``light`` but can re-derive it locally via :func:`thresholds.classify` to catch
threshold drift between the backend and the virtual prototype.

Uses only the standard library (``urllib``) so the traffic light stays a
dependency-free, importable library.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .thresholds import Light, classify


class UtilizationError(RuntimeError):
    """Raised when the utilisation endpoint cannot be reached or parsed."""


def fetch_utilization(
    api_base: str,
    garage_id: str = "garage1",
    *,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Fetch the aggregated utilisation payload for ``garage_id``.

    Returns the parsed JSON, e.g.::

        {"garageId": "garage1", "totalSpots": 350, "occupied": 287,
         "free": 63, "utilization": 0.82, "light": "yellow", "spots": [...]}
    """
    url = f"{api_base.rstrip('/')}/garages/{garage_id}/utilization"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except (urllib.error.URLError, OSError) as exc:  # network / DNS / timeout
        raise UtilizationError(f"could not fetch {url}: {exc}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise UtilizationError(f"invalid JSON from {url}: {exc}") from exc


def current_light(
    api_base: str,
    garage_id: str = "garage1",
    *,
    timeout: float = 5.0,
    verify: bool = True,
) -> Light:
    """Return the current entrance-light state for ``garage_id``.

    Uses the backend's ``light`` field. When ``verify`` is true (default), the
    locally re-derived light from ``utilization`` must agree with the backend's,
    otherwise :class:`UtilizationError` is raised — a guard against the backend
    and the virtual prototype drifting apart on the thresholds.
    """
    payload = fetch_utilization(api_base, garage_id, timeout=timeout)
    backend_light = payload.get("light")
    utilisation = payload.get("utilization")

    if utilisation is None:
        if backend_light is None:
            raise UtilizationError("payload has neither 'light' nor 'utilization'")
        return backend_light

    derived = classify(float(utilisation))
    if verify and backend_light is not None and backend_light != derived:
        raise UtilizationError(
            f"threshold drift: backend light={backend_light!r} but "
            f"utilization={utilisation!r} classifies as {derived!r}"
        )
    return backend_light or derived
