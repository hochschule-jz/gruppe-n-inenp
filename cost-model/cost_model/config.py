"""Load and type the cost-model assumptions — the single source of truth.

Every input lives in ``assumptions.toml`` so the model stays reproducible and each figure
in the paper traces back to exactly one documented value. Parsed read-only with the stdlib
``tomllib`` (Python 3.11+), so the core model has no third-party dependencies.

All monetary values are in the currency given by ``[meta].currency`` (EUR). AWS unit prices
are **placeholders** until verified against the AWS Pricing Calculator — see the README.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ASSUMPTIONS = Path(__file__).with_name("assumptions.toml")


@dataclass(frozen=True)
class Capex:
    """One-time investment inputs (per-spot, per-controller, and fixed)."""

    sensor_eur: float
    wiring_eur_per_spot: float
    install_eur_per_spot: float
    sensors_per_controller: int
    controller_eur: float
    network_fixed_eur: float
    cloud_setup_eur: float


@dataclass(frozen=True)
class AwsPrices:
    """AWS unit prices + a few technical model constants used to size usage.

    Prices are per the unit named in each field. ``item_bytes``, ``lambda_mem_gb`` and
    ``lambda_ms_per_invoke`` are not prices but technical constants the usage model needs.
    """

    iot_messaging_eur_per_million: float
    iot_connection_eur_per_million_min: float
    lambda_eur_per_million_req: float
    lambda_eur_per_gb_second: float
    lambda_mem_gb: float
    lambda_ms_per_invoke: float
    ddb_write_eur_per_million: float
    ddb_read_eur_per_million: float
    ddb_storage_eur_per_gb_month: float
    apigw_eur_per_million_req: float
    data_transfer_eur_per_gb: float
    item_bytes: int


@dataclass(frozen=True)
class NonCloudOpex:
    """Recurring non-cloud operating costs."""

    maintenance_pct_of_capex: float
    sensor_replacement_pct: float
    power_eur_per_controller_year: float


@dataclass(frozen=True)
class LoadParams:
    """Drivers of cloud usage: the write side (occupancy events) and the read side (polling)."""

    events_per_spot_per_day: float
    dashboard_consumers: float
    poll_interval_s: float
    hours_open_per_day: float


@dataclass(frozen=True)
class Benefits:
    """Benefit-side parameters. Utilisation uplift is given in percentage points."""

    parking_tariff_eur_per_space_hour: float
    baseline_utilization: float
    uplift_pp_pessimistic: float
    uplift_pp_base: float
    uplift_pp_optimistic: float
    dynamic_pricing_uplift_pct: float


@dataclass(frozen=True)
class Assumptions:
    horizon_years: int
    currency: str
    discount_rate: float
    capex: Capex
    aws: AwsPrices
    non_cloud: NonCloudOpex
    load: LoadParams
    benefits: Benefits
    scale_spot_counts: tuple[int, ...]


def load_assumptions(path: str | Path = DEFAULT_ASSUMPTIONS) -> Assumptions:
    """Parse ``assumptions.toml`` into a typed :class:`Assumptions`."""
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    meta = raw["meta"]
    return Assumptions(
        horizon_years=int(meta["horizon_years"]),
        currency=str(meta.get("currency", "EUR")),
        discount_rate=float(meta.get("discount_rate", 0.0)),
        capex=Capex(**raw["capex"]),
        aws=AwsPrices(**raw["aws"]),
        non_cloud=NonCloudOpex(**raw["non_cloud"]),
        load=LoadParams(**raw["load"]),
        benefits=Benefits(**raw["benefits"]),
        scale_spot_counts=tuple(int(n) for n in raw["scale"]["spot_counts"]),
    )
