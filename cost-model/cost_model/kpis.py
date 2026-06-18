"""The four KPIs from the paper: TCO, ROI, amortisation (payback), break-even.

All four accept a ``discount_rate``; with ``r = 0`` they reduce to the undiscounted
definitions the paper uses, while ``r > 0`` gives a discounted (NPV) cross-check. Costs and
benefits are modelled as constant annual amounts; CAPEX falls at t0.
"""

from __future__ import annotations

import math


def annuity_factor(horizon_years: int, discount_rate: float) -> float:
    """Present-value factor for 1 unit/year over the horizon. ``r = 0`` -> ``horizon``."""
    if horizon_years < 1:
        raise ValueError("horizon_years must be >= 1")
    if discount_rate == 0:
        return float(horizon_years)
    r = discount_rate
    return (1 - (1 + r) ** (-horizon_years)) / r


def tco(capex_total: float, opex_annual_total: float, horizon_years: int, discount_rate: float = 0.0) -> float:
    """Total cost of ownership = CAPEX + (present value of) annual OPEX."""
    return capex_total + opex_annual_total * annuity_factor(horizon_years, discount_rate)


def npv(
    capex_total: float,
    opex_annual_total: float,
    annual_benefit: float,
    horizon_years: int,
    discount_rate: float = 0.0,
) -> float:
    """Net present value of (benefit - OPEX) over the horizon, minus CAPEX at t0."""
    a = annuity_factor(horizon_years, discount_rate)
    return (annual_benefit - opex_annual_total) * a - capex_total


def roi(
    capex_total: float,
    opex_annual_total: float,
    annual_benefit: float,
    horizon_years: int,
    discount_rate: float = 0.0,
) -> float:
    """ROI over the horizon = (PV benefits - PV costs) / PV costs."""
    a = annuity_factor(horizon_years, discount_rate)
    pv_benefits = annual_benefit * a
    pv_costs = capex_total + opex_annual_total * a
    return (pv_benefits - pv_costs) / pv_costs if pv_costs else math.inf


def payback_months(capex_total: float, opex_annual_total: float, annual_benefit: float) -> float:
    """Simple (undiscounted) payback in months; ``inf`` if it never pays back."""
    net_annual = annual_benefit - opex_annual_total
    if net_annual <= 0:
        return math.inf
    return capex_total / net_annual * 12.0


def breakeven_uplift_pp(
    spots: int,
    capex_total: float,
    opex_annual_total: float,
    horizon_years: int,
    discount_rate: float,
    tariff: float,
    open_hours_per_year: float,
) -> float:
    """Utilisation uplift (percentage points) at which the system exactly pays for itself.

    Inverts the **utilisation pathway only** (the conservative, defensible framing): how many
    extra pp of utilisation are needed so benefits == costs, ignoring dynamic pricing and the
    softer pathways. Compare the result against literature uplift ranges.
    """
    a = annuity_factor(horizon_years, discount_rate)
    breakeven_annual_benefit = capex_total / a + opex_annual_total
    benefit_per_pp = spots * tariff * open_hours_per_year / 100.0
    if benefit_per_pp <= 0:
        return math.inf
    return breakeven_annual_benefit / benefit_per_pp
