"""End-to-end run through run_load with a capturing publisher (no network)."""

import json

from load_generator.cli import run_load
from load_generator.profiles import from_dict


class CapturingPublisher:
    def __init__(self):
        self.messages = []  # (topic, payload, qos)
        self.closed = False

    def publish(self, topic, payload, qos=0):
        self.messages.append((topic, payload, qos))

    def close(self):
        self.closed = True


def _small_profile():
    return from_dict(
        {"name": "test", "spots": 25, "targetUtil": 0.6, "dwellMeanMin": 5,
         "durationMin": 30, "seed": 123},
        name="test",
    )


def test_initial_snapshot_then_transitions():
    pub = CapturingPublisher()
    profile = _small_profile()
    stats = run_load(profile, pub, base_ms=1_000_000, sleep=lambda _: None)

    # One initial message per spot.
    assert stats.initial_messages == profile.spots
    # Total publishes == initial + transitions.
    assert len(pub.messages) == stats.total_messages
    assert stats.total_messages == stats.initial_messages + stats.transition_messages


def test_every_published_message_matches_contract():
    pub = CapturingPublisher()
    run_load(_small_profile(), pub, base_ms=1_000_000, sleep=lambda _: None)
    for topic, payload, qos in pub.messages:
        assert topic.startswith("parking/garage1/spot/")
        msg = json.loads(payload)
        assert list(msg.keys()) == ["sensorId", "garageId", "spotId", "ts", "raw", "status"]
        assert msg["status"] in ("occupied", "free")
        assert msg["raw"] == (1 if msg["status"] == "occupied" else 0)
        assert topic.endswith(f"/spot/{msg['spotId']}")


def test_run_is_reproducible():
    p1, p2 = CapturingPublisher(), CapturingPublisher()
    run_load(_small_profile(), p1, base_ms=1_000_000, sleep=lambda _: None)
    run_load(_small_profile(), p2, base_ms=1_000_000, sleep=lambda _: None)
    assert p1.messages == p2.messages


def test_manifest_usage_estimate():
    pub = CapturingPublisher()
    stats = run_load(_small_profile(), pub, base_ms=1_000_000, sleep=lambda _: None)
    manifest = stats.manifest()
    assert manifest["awsUsageEstimate"]["iotMessages"] == stats.total_messages
    assert manifest["awsUsageEstimate"]["dynamodbWrites"] == stats.total_messages


def test_no_initial_snapshot_option():
    pub = CapturingPublisher()
    stats = run_load(_small_profile(), pub, emit_initial=False,
                     base_ms=1_000_000, sleep=lambda _: None)
    assert stats.initial_messages == 0
    assert len(pub.messages) == stats.transition_messages
