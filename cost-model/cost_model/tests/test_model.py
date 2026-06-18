from cost_model import evaluate, load_assumptions
from cost_model.benefits import utilization_benefit
from cost_model.kpis import roi


def test_evaluate_runs_with_default_assumptions():
    a = load_assumptions()
    r = evaluate(a, 200, "base")
    assert r.capex.total > 0
    assert r.opex.total_annual > 0
    assert r.tco > r.capex.total  # TCO adds OPEX on top of CAPEX


def test_breakeven_is_self_consistent_end_to_end():
    a = load_assumptions()
    r = evaluate(a, 350, "base")
    open_h = a.load.hours_open_per_day * 365
    benefit = utilization_benefit(
        350, r.breakeven_uplift_pp, a.benefits.parking_tariff_eur_per_space_hour, open_h
    )
    assert abs(roi(r.capex.total, r.opex.total_annual, benefit, a.horizon_years, a.discount_rate)) < 1e-9


def test_manifest_override_changes_write_volume():
    a = load_assumptions()
    low = evaluate(a, 200, "base", events_per_spot_per_day=5.0)
    high = evaluate(a, 200, "base", events_per_spot_per_day=50.0)
    assert high.opex.iot > low.opex.iot
