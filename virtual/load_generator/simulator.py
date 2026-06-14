"""Per-spot occupancy simulator (pure, deterministic, no I/O).

Each parking spot is an independent two-state continuous-time process:

    free --arrival(arrival_rate)--> occupied --departure(departure_rate)--> free

with rates expressed per second. The steady-state occupancy probability is
``arrival_rate / (arrival_rate + departure_rate)``, so choosing the rates from a
target utilisation and a mean dwell time (see ``profiles.py``) makes the
realised occupancy land on that target.

The simulator emits **only state-change events** (plus optional warm-start
initial states), mirroring real event-driven devices. It is fully reproducible
for a given seed and touches neither MQTT nor the wall clock — that is what
makes it unit-testable.
"""

from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Event:
    """A single occupancy change."""

    t: float        # seconds of simulated time since start
    spot_id: int    # 1..n_spots
    occupied: bool  # the new state after this transition


def _next_interval(rng: random.Random, rate: float) -> float:
    """Exponential inter-event time for a Poisson process of ``rate`` per second.

    A non-positive rate means the process never fires (returns +inf).
    """
    if rate <= 0.0:
        return math.inf
    return rng.expovariate(rate)


class Simulator:
    def __init__(
        self,
        n_spots: int,
        arrival_rate: float,
        departure_rate: float,
        seed: int,
        *,
        warm_start: bool = True,
    ) -> None:
        if n_spots < 1:
            raise ValueError("n_spots must be >= 1")
        if departure_rate <= 0.0:
            raise ValueError("departure_rate must be > 0")
        if arrival_rate < 0.0:
            raise ValueError("arrival_rate must be >= 0")
        self.n_spots = n_spots
        self.arrival_rate = arrival_rate
        self.departure_rate = departure_rate
        self.seed = seed
        self.warm_start = warm_start

    @property
    def steady_state_util(self) -> float:
        total = self.arrival_rate + self.departure_rate
        return self.arrival_rate / total if total > 0 else 0.0

    def _build_initial(self, rng: random.Random) -> dict[int, bool]:
        """Initial state per spot, consuming ``rng`` deterministically.

        With ``warm_start`` each spot is occupied with the steady-state
        probability, so utilisation starts at target instead of all-free.
        """
        util = self.steady_state_util
        if not self.warm_start:
            return {spot: False for spot in range(1, self.n_spots + 1)}
        return {spot: rng.random() < util for spot in range(1, self.n_spots + 1)}

    @property
    def initial_states(self) -> dict[int, bool]:
        """The warm-start states (spot_id -> occupied), reproducible per seed."""
        return self._build_initial(random.Random(self.seed))

    def _leave_rate(self, occupied: bool) -> float:
        return self.departure_rate if occupied else self.arrival_rate

    def events(self, duration_seconds: float) -> Iterator[Event]:
        """Yield state-change events in ``(0, duration_seconds]``, time-ordered.

        Reproducible: every call rebuilds the same RNG sequence from the seed.
        """
        if duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")
        rng = random.Random(self.seed)
        state = self._build_initial(rng)

        # (transition_time, spot_id); spot_id breaks ties deterministically.
        heap: list[tuple[float, int]] = []
        for spot in range(1, self.n_spots + 1):
            dt = _next_interval(rng, self._leave_rate(state[spot]))
            if dt != math.inf:
                heapq.heappush(heap, (dt, spot))

        while heap:
            t, spot = heapq.heappop(heap)
            if t > duration_seconds:
                break
            new_state = not state[spot]
            state[spot] = new_state
            yield Event(t=t, spot_id=spot, occupied=new_state)
            dt = _next_interval(rng, self._leave_rate(new_state))
            if dt != math.inf:
                heapq.heappush(heap, (t + dt, spot))
