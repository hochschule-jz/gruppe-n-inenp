"""Build the locked MQTT topic and JSON payload.

Single source of truth for the wire format, kept byte-compatible with
``docs/contract.md`` section 0.3 and the firmware's ``publishSpot()``:

    topic:   parking/<garageId>/spot/<spotId>
    payload: {"sensorId","garageId","spotId","ts","raw","status"}
"""

from __future__ import annotations

import json
from typing import Any

DEFAULT_GARAGE_ID = "garage1"
#: Free during dev (contract 0.5); a distinct id marks virtually-generated load.
DEFAULT_SENSOR_ID = "virtual-loadgen"


def build_topic(garage_id: str, spot_id: int) -> str:
    return f"parking/{garage_id}/spot/{spot_id}"


def build_payload(
    *,
    spot_id: int,
    occupied: bool,
    ts_ms: int,
    garage_id: str = DEFAULT_GARAGE_ID,
    sensor_id: str = DEFAULT_SENSOR_ID,
) -> dict[str, Any]:
    """Construct one contract-compliant message.

    ``raw`` mirrors a TCRT5000 ``digitalRead`` with ``occupiedWhenHigh`` true
    (occupied -> 1, free -> 0); ``status`` is the derived label.
    """
    return {
        "sensorId": sensor_id,
        "garageId": garage_id,
        "spotId": spot_id,
        "ts": ts_ms,
        "raw": 1 if occupied else 0,
        "status": "occupied" if occupied else "free",
    }


def to_json(payload: dict[str, Any]) -> str:
    """Compact JSON, matching the embedded device's minimal payload."""
    return json.dumps(payload, separators=(",", ":"))
