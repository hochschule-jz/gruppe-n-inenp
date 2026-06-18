"""CAPEX: one-time investment, normalised so it scales with garage size.

Sensors/wiring/installation scale per spot; controllers scale **stepwise** (one node per
``sensors_per_controller`` spots — the prototype's 4-sensors-on-one-ESP32 does not scale to
hundreds of spots, so the node count must grow); network and cloud setup are fixed one-time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import Capex


def controllers_for(spots: int, sensors_per_controller: int) -> int:
    """Number of controller nodes needed for ``spots`` (one per N sensors, rounded up)."""
    if sensors_per_controller < 1:
        raise ValueError("sensors_per_controller must be >= 1")
    return math.ceil(spots / sensors_per_controller)


@dataclass(frozen=True)
class CapexBreakdown:
    sensors: float
    wiring: float
    install: float
    controllers: float
    network_fixed: float
    cloud_setup: float
    controller_count: int

    @property
    def total(self) -> float:
        return (
            self.sensors
            + self.wiring
            + self.install
            + self.controllers
            + self.network_fixed
            + self.cloud_setup
        )

    @property
    def per_spot(self) -> float:
        return self.total  # divided by spots at the call site when needed


def capex_for(spots: int, c: Capex) -> CapexBreakdown:
    """Full CAPEX breakdown for a garage of ``spots`` spots."""
    if spots < 1:
        raise ValueError("spots must be >= 1")
    n_controllers = controllers_for(spots, c.sensors_per_controller)
    return CapexBreakdown(
        sensors=c.sensor_eur * spots,
        wiring=c.wiring_eur_per_spot * spots,
        install=c.install_eur_per_spot * spots,
        controllers=c.controller_eur * n_controllers,
        network_fixed=c.network_fixed_eur,
        cloud_setup=c.cloud_setup_eur,
        controller_count=n_controllers,
    )
