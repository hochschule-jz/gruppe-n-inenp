"""Named load profiles and rate derivation.

A profile is a small JSON file describing one load scenario (e.g. peak vs
off-peak). It is specified in human-meaningful terms — target utilisation and
mean parking duration — from which the simulator's per-second arrival and
departure rates are derived:

    departure_rate = 1 / (dwellMeanMin * 60)          # leaving an occupied spot
    arrival_rate   = departure_rate * U / (1 - U)     # so steady-state util == U
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .message import DEFAULT_GARAGE_ID, DEFAULT_SENSOR_ID


class ProfileError(ValueError):
    """Raised when a profile file is missing required fields or out of range."""


@dataclass(frozen=True)
class Profile:
    name: str
    spots: int
    target_util: float
    dwell_mean_min: float
    seed: int
    duration_min: float
    time_scale: float = 1.0
    warm_start: bool = True
    garage_id: str = DEFAULT_GARAGE_ID
    sensor_id: str = DEFAULT_SENSOR_ID

    @property
    def departure_rate(self) -> float:
        """Per-second rate of an occupied spot becoming free."""
        return 1.0 / (self.dwell_mean_min * 60.0)

    @property
    def arrival_rate(self) -> float:
        """Per-second rate of a free spot becoming occupied (gives util == target)."""
        return self.departure_rate * self.target_util / (1.0 - self.target_util)

    @property
    def duration_seconds(self) -> float:
        """Simulated time span of the run."""
        return self.duration_min * 60.0

    @property
    def send_seconds(self) -> float:
        """Real wall-clock span of the run after time compression."""
        return self.duration_seconds / self.time_scale


def from_dict(data: dict[str, Any], *, name: str = "profile") -> Profile:
    """Validate a raw mapping and build a :class:`Profile`."""
    if not isinstance(data, dict):
        raise ProfileError("profile must be a JSON object")

    def _req(key: str) -> Any:
        if key not in data:
            raise ProfileError(f"profile {name!r} is missing required field {key!r}")
        return data[key]

    spots = _req("spots")
    target_util = _req("targetUtil")
    dwell_mean_min = _req("dwellMeanMin")

    if not isinstance(spots, int) or spots < 1:
        raise ProfileError("'spots' must be an integer >= 1")
    if not (0.0 <= float(target_util) < 1.0):
        raise ProfileError("'targetUtil' must be in [0, 1)")
    if float(dwell_mean_min) <= 0.0:
        raise ProfileError("'dwellMeanMin' must be > 0")

    duration_min = float(data.get("durationMin", 60.0))
    time_scale = float(data.get("timeScale", 1.0))
    if duration_min <= 0.0:
        raise ProfileError("'durationMin' must be > 0")
    if time_scale <= 0.0:
        raise ProfileError("'timeScale' must be > 0")

    return Profile(
        name=str(data.get("name", name)),
        spots=spots,
        target_util=float(target_util),
        dwell_mean_min=float(dwell_mean_min),
        seed=int(data.get("seed", 42)),
        duration_min=duration_min,
        time_scale=time_scale,
        warm_start=bool(data.get("warmStart", True)),
        garage_id=str(data.get("garageId", DEFAULT_GARAGE_ID)),
        sensor_id=str(data.get("sensorId", DEFAULT_SENSOR_ID)),
    )


def load_profile(path: str | Path) -> Profile:
    """Load and validate a profile JSON file."""
    p = Path(path)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProfileError(f"profile file not found: {p}") from exc
    except json.JSONDecodeError as exc:
        raise ProfileError(f"invalid JSON in {p}: {exc}") from exc
    return from_dict(raw, name=p.stem)
