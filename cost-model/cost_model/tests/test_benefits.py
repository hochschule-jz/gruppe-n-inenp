import pytest

from cost_model.benefits import annual_benefit, uplift_pp_for, utilization_benefit
from cost_model.config import Benefits

B = Benefits(
    parking_tariff_eur_per_space_hour=3.0,
    baseline_utilization=0.7,
    uplift_pp_pessimistic=1.0,
    uplift_pp_base=3.0,
    uplift_pp_optimistic=6.0,
    dynamic_pricing_uplift_pct=0.0,
)


def test_utilization_benefit_linear_in_uplift():
    b1 = utilization_benefit(200, 1.0, 3.0, 5000.0)
    b3 = utilization_benefit(200, 3.0, 3.0, 5000.0)
    assert abs(b3 - 3 * b1) < 1e-9


def test_scenario_lookup():
    assert uplift_pp_for(B, "base") == 3.0
    with pytest.raises(ValueError):
        uplift_pp_for(B, "nope")


def test_annual_benefit_equals_utilization_when_no_dynamic_pricing():
    ab = annual_benefit(200, B, "base", 5000.0)
    assert abs(ab - utilization_benefit(200, 3.0, 3.0, 5000.0)) < 1e-9
