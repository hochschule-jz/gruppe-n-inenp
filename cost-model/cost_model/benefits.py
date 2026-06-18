"""Benefit side — kept conservative and scenario-based.

The headline pathway is the **utilisation uplift** (better findability -> more occupied
space-hours -> revenue), because it is the most quantifiable and is what the break-even KPI
inverts. Dynamic pricing is an additive secondary pathway. The two softer pathways from the
paper (reduced wrong trips / reputation, data monetisation) are intentionally NOT monetised
here — model them qualitatively in the discussion to avoid over-claiming.
"""

from __future__ import annotations

from .config import Benefits

SCENARIOS = ("pessimistic", "base", "optimistic")


def uplift_pp_for(b: Benefits, scenario: str) -> float:
    """Utilisation uplift (percentage points) for a named scenario."""
    table = {
        "pessimistic": b.uplift_pp_pessimistic,
        "base": b.uplift_pp_base,
        "optimistic": b.uplift_pp_optimistic,
    }
    if scenario not in table:
        raise ValueError(f"scenario must be one of {SCENARIOS}, got {scenario!r}")
    return table[scenario]


def utilization_benefit(spots: int, uplift_pp: float, tariff: float, open_hours_per_year: float) -> float:
    """Annual revenue from ``uplift_pp`` percentage points more occupied spaces."""
    extra_occupied_spaces = (uplift_pp / 100.0) * spots
    return extra_occupied_spaces * tariff * open_hours_per_year


def dynamic_pricing_benefit(spots: int, b: Benefits, open_hours_per_year: float) -> float:
    """Annual extra revenue from dynamic pricing, applied to the baseline turnover."""
    baseline_revenue = b.baseline_utilization * spots * b.parking_tariff_eur_per_space_hour * open_hours_per_year
    return (b.dynamic_pricing_uplift_pct / 100.0) * baseline_revenue


def annual_benefit(
    spots: int,
    b: Benefits,
    scenario: str,
    open_hours_per_year: float,
    *,
    include_dynamic_pricing: bool = True,
) -> float:
    """Total annual benefit = utilisation uplift (+ optional dynamic pricing)."""
    total = utilization_benefit(
        spots, uplift_pp_for(b, scenario), b.parking_tariff_eur_per_space_hour, open_hours_per_year
    )
    if include_dynamic_pricing:
        total += dynamic_pricing_benefit(spots, b, open_hours_per_year)
    return total
