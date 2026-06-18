"""Derive monthly AWS usage quantities — the cost drivers.

Two independent drivers, which is the analytically important point:

* **Write side** (occupancy events): 1 event = 1 IoT message = 1 IoT-rule action =
  1 validation-Lambda invocation = 1 DynamoDB write. This is exactly what the load
  generator's ``awsUsageEstimate`` manifest counts.
* **Read side** (consumers polling ``/utilization``): each poll = 1 API Gateway request =
  1 aggregation-Lambda invocation = 1 DynamoDB *query that reads all spots*. The manifest
  does NOT cover this; it is driven by ``dashboard_consumers x poll cadence x spots`` and
  can dominate the bill at scale.

All quantities are returned **per month**.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .capex import controllers_for
from .config import AwsPrices, Capex, LoadParams

DAYS_PER_MONTH = 365.0 / 12.0
SECONDS_PER_DAY = 24 * 3600
MINUTES_PER_MONTH = 60 * 24 * DAYS_PER_MONTH
DDB_PAGE_BYTES = 4096  # DynamoDB capacity-unit page size


@dataclass(frozen=True)
class Usage:
    write_messages: float          # IoT msgs = validation invocations = DDB writes
    iot_connection_minutes: float  # controllers connected 24/7
    read_requests: float           # API Gateway requests = aggregation invocations
    ddb_read_units: float          # RRU consumed by the per-poll "read all spots" query
    lambda_invocations: float      # validation + aggregation
    lambda_gb_seconds: float
    data_transfer_gb: float
    storage_gb: float
    controllers: int


def ddb_read_units_per_query(spots: int, item_bytes: int) -> float:
    """RRU for one eventually-consistent query that returns all ``spots`` items."""
    total_bytes = spots * item_bytes
    pages = math.ceil(total_bytes / DDB_PAGE_BYTES)
    return pages * 0.5  # eventually consistent = half an RRU per 4 KB page


def monthly_usage(spots: int, load: LoadParams, aws: AwsPrices, capex: Capex) -> Usage:
    """Compute all monthly usage quantities for a garage of ``spots`` spots."""
    controllers = controllers_for(spots, capex.sensors_per_controller)

    # Write side.
    write_messages = load.events_per_spot_per_day * spots * DAYS_PER_MONTH
    iot_connection_minutes = controllers * MINUTES_PER_MONTH

    # Read side.
    polls_per_day = load.dashboard_consumers * (load.hours_open_per_day * 3600 / load.poll_interval_s)
    read_requests = polls_per_day * DAYS_PER_MONTH
    ddb_read_units = read_requests * ddb_read_units_per_query(spots, aws.item_bytes)

    # Shared.
    lambda_invocations = write_messages + read_requests
    lambda_gb_seconds = lambda_invocations * aws.lambda_mem_gb * (aws.lambda_ms_per_invoke / 1000.0)
    data_transfer_gb = read_requests * (spots * aws.item_bytes) / 1e9
    storage_gb = (spots * aws.item_bytes) / 1e9  # current-state table: one item per spot

    return Usage(
        write_messages=write_messages,
        iot_connection_minutes=iot_connection_minutes,
        read_requests=read_requests,
        ddb_read_units=ddb_read_units,
        lambda_invocations=lambda_invocations,
        lambda_gb_seconds=lambda_gb_seconds,
        data_transfer_gb=data_transfer_gb,
        storage_gb=storage_gb,
        controllers=controllers,
    )


def events_per_spot_per_day_from_manifest(manifest: dict) -> float:
    """Steady-state event rate from a load-generator run manifest.

    Uses ``transitionMessages`` over the **simulated** ``durationSeconds`` (NOT the
    time-compressed ``sendSeconds``) and the manifest's ``spots``, so a 60x-compressed
    run still yields a real-world per-day rate. This is the bridge that lets a measured
    or dry-run load profile drive the OPEX numbers.
    """
    duration_s = float(manifest["durationSeconds"])
    spots = int(manifest["spots"])
    if duration_s <= 0 or spots <= 0:
        raise ValueError("manifest needs positive durationSeconds and spots")
    per_spot_per_second = (float(manifest["transitionMessages"]) / duration_s) / spots
    return per_spot_per_second * SECONDS_PER_DAY
