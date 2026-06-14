"""The wire format must match docs/contract.md section 0.3 exactly."""

import json

from load_generator.message import build_payload, build_topic, to_json


def test_topic_format():
    assert build_topic("garage1", 3) == "parking/garage1/spot/3"


def test_payload_keys_order_and_types():
    payload = build_payload(spot_id=3, occupied=True, ts_ms=1735680000000)
    # Exact key set and order from the contract.
    assert list(payload.keys()) == ["sensorId", "garageId", "spotId", "ts", "raw", "status"]
    assert isinstance(payload["sensorId"], str)
    assert isinstance(payload["garageId"], str)
    assert isinstance(payload["spotId"], int)
    assert isinstance(payload["ts"], int)
    assert payload["raw"] in (0, 1)
    assert payload["status"] in ("occupied", "free")


def test_occupied_mapping():
    occ = build_payload(spot_id=1, occupied=True, ts_ms=1)
    free = build_payload(spot_id=1, occupied=False, ts_ms=1)
    assert (occ["raw"], occ["status"]) == (1, "occupied")
    assert (free["raw"], free["status"]) == (0, "free")


def test_defaults_match_contract():
    payload = build_payload(spot_id=7, occupied=False, ts_ms=42)
    assert payload["garageId"] == "garage1"
    assert payload["sensorId"] == "virtual-loadgen"


def test_json_is_compact_and_roundtrips():
    payload = build_payload(spot_id=3, occupied=True, ts_ms=1735680000000)
    text = to_json(payload)
    assert " " not in text  # compact, like the embedded device
    assert json.loads(text) == payload
