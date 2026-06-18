"""Scale sweep + one-way (tornado) sensitivity analysis.

The scale sweep evaluates the mandated 200/350/500 garage sizes; the tornado varies each key
lever +/- ``delta`` and ranks them by impact on ROI, so the dominant drivers fall out.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import Assumptions
from .model import evaluate


@dataclass(frozen=True)
class ScaleRow:
    spots: int
    capex_total: float
    opex_annual: float
    tco: float
    roi: float
    payback_months: float
    breakeven_uplift_pp: float


def scale_sweep(a: Assumptions, scenario: str = "base") -> list[ScaleRow]:
    """Evaluate every garage size in ``a.scale_spot_counts``."""
    rows: list[ScaleRow] = []
    for n in a.scale_spot_counts:
        r = evaluate(a, n, scenario)
        rows.append(
            ScaleRow(
                spots=n,
                capex_total=r.capex.total,
                opex_annual=r.opex.total_annual,
                tco=r.tco,
                roi=r.roi,
                payback_months=r.payback_months,
                breakeven_uplift_pp=r.breakeven_uplift_pp,
            )
        )
    return rows


# Levers the tornado varies: name -> (getter, setter-returning-new-Assumptions).
_LEVERS = {
    "sensor_eur": (
        lambda a: a.capex.sensor_eur,
        lambda a, v: replace(a, capex=replace(a.capex, sensor_eur=v)),
    ),
    "tariff": (
        lambda a: a.benefits.parking_tariff_eur_per_space_hour,
        lambda a, v: replace(a, benefits=replace(a.benefits, parking_tariff_eur_per_space_hour=v)),
    ),
    "uplift_base_pp": (
        lambda a: a.benefits.uplift_pp_base,
        lambda a, v: replace(a, benefits=replace(a.benefits, uplift_pp_base=v)),
    ),
    "events_per_spot_per_day": (
        lambda a: a.load.events_per_spot_per_day,
        lambda a, v: replace(a, load=replace(a.load, events_per_spot_per_day=v)),
    ),
}


@dataclass(frozen=True)
class TornadoRow:
    lever: str
    low_value: float
    high_value: float
    low_roi: float
    high_roi: float

    @property
    def swing(self) -> float:
        return abs(self.high_roi - self.low_roi)


def one_way_sensitivity(
    a: Assumptions, spots: int, scenario: str = "base", delta: float = 0.30
) -> list[TornadoRow]:
    """Vary each lever +/- ``delta`` and rank by ROI swing (largest first)."""
    rows: list[TornadoRow] = []
    for name, (get, set_) in _LEVERS.items():
        base = get(a)
        low_roi = evaluate(set_(a, base * (1 - delta)), spots, scenario).roi
        high_roi = evaluate(set_(a, base * (1 + delta)), spots, scenario).roi
        rows.append(TornadoRow(name, base * (1 - delta), base * (1 + delta), low_roi, high_roi))
    rows.sort(key=lambda r: r.swing, reverse=True)
    return rows
