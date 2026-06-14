"""Profile loading, rate derivation, and validation."""

from pathlib import Path

import pytest

from load_generator.profiles import ProfileError, from_dict, load_profile

_PKG = Path(__file__).resolve().parent.parent


def test_load_bundled_profiles():
    peak = load_profile(_PKG / "peak.json")
    offpeak = load_profile(_PKG / "offpeak.json")
    assert peak.name == "peak" and peak.target_util == 0.88
    assert offpeak.name == "offpeak" and offpeak.target_util == 0.35


def test_rate_derivation_gives_target_util():
    p = from_dict({"spots": 100, "targetUtil": 0.8, "dwellMeanMin": 90})
    # departure = 1/(90*60); arrival = departure * U/(1-U); steady util == U
    assert p.departure_rate == pytest.approx(1.0 / (90 * 60))
    assert p.arrival_rate / (p.arrival_rate + p.departure_rate) == pytest.approx(0.8)


def test_duration_and_send_seconds_with_time_scale():
    p = from_dict({"spots": 10, "targetUtil": 0.5, "dwellMeanMin": 60,
                   "durationMin": 30, "timeScale": 60})
    assert p.duration_seconds == 1800
    assert p.send_seconds == 30  # 1800s simulated, compressed 60x -> 30s real


@pytest.mark.parametrize("bad", [
    {"targetUtil": 0.5, "dwellMeanMin": 90},              # missing spots
    {"spots": 0, "targetUtil": 0.5, "dwellMeanMin": 90},  # spots < 1
    {"spots": 10, "targetUtil": 1.0, "dwellMeanMin": 90}, # util out of range
    {"spots": 10, "targetUtil": -0.1, "dwellMeanMin": 90},
    {"spots": 10, "targetUtil": 0.5, "dwellMeanMin": 0},  # dwell <= 0
    {"spots": 10, "targetUtil": 0.5, "dwellMeanMin": 90, "durationMin": 0},
])
def test_invalid_profiles_rejected(bad):
    with pytest.raises(ProfileError):
        from_dict(bad)


def test_missing_file():
    with pytest.raises(ProfileError):
        load_profile(_PKG / "does-not-exist.json")
