"""Boundary tests for the canonical traffic-light thresholds.

These pin the exact contract boundaries (docs/contract.md 0.6):
green < 0.70, yellow 0.70-0.90 (inclusive), red > 0.90.
"""

import pytest

from traffic_light.thresholds import GREEN_MAX, YELLOW_MAX, classify


@pytest.mark.parametrize(
    ("utilisation", "expected"),
    [
        (0.0, "green"),
        (0.5, "green"),
        (0.69, "green"),
        (0.6999, "green"),
        (0.70, "yellow"),   # boundary: 0.70 is yellow, not green
        (0.80, "yellow"),
        (0.90, "yellow"),   # boundary: 0.90 is yellow, not red
        (0.9001, "red"),
        (0.95, "red"),
        (1.0, "red"),
    ],
)
def test_classify_boundaries(utilisation, expected):
    assert classify(utilisation) == expected


def test_classify_matches_named_constants():
    assert classify(GREEN_MAX - 1e-9) == "green"
    assert classify(GREEN_MAX) == "yellow"
    assert classify(YELLOW_MAX) == "yellow"
    assert classify(YELLOW_MAX + 1e-9) == "red"


@pytest.mark.parametrize("bad", [-0.01, 1.01, 2.0, -1.0])
def test_classify_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        classify(bad)
