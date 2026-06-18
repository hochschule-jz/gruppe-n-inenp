from cost_model.benefits import utilization_benefit
from cost_model.kpis import annuity_factor, breakeven_uplift_pp, npv, payback_months, roi, tco


def test_annuity_factor_zero_rate_is_horizon():
    assert annuity_factor(5, 0.0) == 5.0


def test_annuity_factor_positive_rate_less_than_horizon():
    assert annuity_factor(5, 0.07) < 5.0


def test_tco_undiscounted():
    assert tco(1000.0, 200.0, 5, 0.0) == 1000.0 + 200.0 * 5


def test_breakeven_uplift_gives_zero_roi():
    spots, capex, opex, horizon, tariff, open_h = 200, 10000.0, 500.0, 5, 3.0, 5000.0
    be = breakeven_uplift_pp(spots, capex, opex, horizon, 0.0, tariff, open_h)
    benefit = utilization_benefit(spots, be, tariff, open_h)
    assert abs(roi(capex, opex, benefit, horizon, 0.0)) < 1e-9


def test_payback_decreases_with_benefit():
    assert payback_months(10000.0, 500.0, 2000.0) > payback_months(10000.0, 500.0, 4000.0)


def test_payback_infinite_when_opex_exceeds_benefit():
    import math

    assert math.isinf(payback_months(10000.0, 5000.0, 1000.0))


def test_npv_sign_matches_roi_sign():
    capex, opex, benefit, horizon = 10000.0, 500.0, 3000.0, 5
    assert (npv(capex, opex, benefit, horizon, 0.0) > 0) == (roi(capex, opex, benefit, horizon, 0.0) > 0)
