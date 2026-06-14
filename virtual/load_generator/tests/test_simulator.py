"""Simulator behaviour: determinism, state-change-only, and steady-state util."""

import pytest

from load_generator.simulator import Simulator


def _time_weighted_util(sim: Simulator, duration: float) -> float:
    """Integrate occupied-count over time -> average utilisation."""
    state = sim.initial_states
    occupied = sum(1 for v in state.values() if v)
    area = 0.0
    prev_t = 0.0
    for ev in sim.events(duration):
        area += occupied * (ev.t - prev_t)
        occupied += 1 if ev.occupied else -1
        prev_t = ev.t
    area += occupied * (duration - prev_t)
    return area / (sim.n_spots * duration)


def test_deterministic_for_same_seed():
    a = Simulator(50, arrival_rate=0.02, departure_rate=0.02, seed=7)
    b = Simulator(50, arrival_rate=0.02, departure_rate=0.02, seed=7)
    assert list(a.events(2000)) == list(b.events(2000))


def test_different_seed_differs():
    a = list(Simulator(50, 0.02, 0.02, seed=1).events(2000))
    b = list(Simulator(50, 0.02, 0.02, seed=2).events(2000))
    assert a != b


def test_events_are_time_ordered():
    sim = Simulator(100, 0.03, 0.02, seed=3)
    times = [ev.t for ev in sim.events(5000)]
    assert times == sorted(times)


def test_only_state_changes_alternate_per_spot():
    sim = Simulator(20, 0.05, 0.05, seed=11)
    initial = sim.initial_states
    last = dict(initial)
    for ev in sim.events(3000):
        assert ev.occupied != last[ev.spot_id]  # every event is a real change
        last[ev.spot_id] = ev.occupied


def test_warm_start_off_is_all_free():
    sim = Simulator(30, 0.1, 0.1, seed=5, warm_start=False)
    assert set(sim.initial_states.values()) == {False}


@pytest.mark.parametrize(
    ("arrival", "departure", "target"),
    [(0.02, 0.02, 0.5), (0.04, 0.01, 0.8), (0.01, 0.04, 0.2)],
)
def test_steady_state_matches_target(arrival, departure, target):
    sim = Simulator(200, arrival, departure, seed=99)
    util = _time_weighted_util(sim, duration=40000)
    assert sim.steady_state_util == pytest.approx(target, abs=1e-9)
    assert util == pytest.approx(target, abs=0.03)
