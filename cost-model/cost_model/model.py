"""Tie the pieces together: assumptions + spot count + scenario -> one :class:`Result`.

This is the function the report, the sensitivity sweep and the tests all call.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .benefits import annual_benefit
from .capex import CapexBreakdown, capex_for
from .config import Assumptions
from .kpis import breakeven_uplift_pp, npv, payback_months, roi, tco
from .opex import OpexBreakdown, opex_annual
from .usage import Usage, monthly_usage

DAYS_PER_YEAR = 365.0


@dataclass(frozen=True)
class Result:
    spots: int
    scenario: str
    capex: CapexBreakdown
    opex: OpexBreakdown
    usage: Usage
    annual_benefit: float
    tco: float
    roi: float
    payback_months: float
    breakeven_uplift_pp: float
    npv: float


def evaluate(
    a: Assumptions,
    spots: int,
    scenario: str = "base",
    *,
    events_per_spot_per_day: float | None = None,
) -> Result:
    """Evaluate the full model for one garage size and benefit scenario.

    Pass ``events_per_spot_per_day`` (e.g. from
    :func:`cost_model.usage.events_per_spot_per_day_from_manifest`) to drive the write-side
    volume from a real/dry-run load profile instead of the assumptions default.
    """
    load = a.load
    if events_per_spot_per_day is not None:
        load = replace(load, events_per_spot_per_day=events_per_spot_per_day)

    cap = capex_for(spots, a.capex)
    use = monthly_usage(spots, load, a.aws, a.capex)
    op = opex_annual(spots, use, a.aws, a.non_cloud, cap.total, a.capex.sensor_eur)

    open_hours_per_year = load.hours_open_per_day * DAYS_PER_YEAR
    benefit = annual_benefit(spots, a.benefits, scenario, open_hours_per_year)

    h, r = a.horizon_years, a.discount_rate
    return Result(
        spots=spots,
        scenario=scenario,
        capex=cap,
        opex=op,
        usage=use,
        annual_benefit=benefit,
        tco=tco(cap.total, op.total_annual, h, r),
        roi=roi(cap.total, op.total_annual, benefit, h, r),
        payback_months=payback_months(cap.total, op.total_annual, benefit),
        breakeven_uplift_pp=breakeven_uplift_pp(
            spots, cap.total, op.total_annual, h, r, a.benefits.parking_tariff_eur_per_space_hour, open_hours_per_year
        ),
        npv=npv(cap.total, op.total_annual, benefit, h, r),
    )
