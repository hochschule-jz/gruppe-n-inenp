from cost_model.config import AwsPrices, Capex, LoadParams
from cost_model.usage import (
    DAYS_PER_MONTH,
    ddb_read_units_per_query,
    events_per_spot_per_day_from_manifest,
    monthly_usage,
)

AWS = AwsPrices(
    iot_messaging_eur_per_million=1.0,
    iot_connection_eur_per_million_min=0.08,
    lambda_eur_per_million_req=0.2,
    lambda_eur_per_gb_second=1.66667e-5,
    lambda_mem_gb=0.128,
    lambda_ms_per_invoke=30.0,
    ddb_write_eur_per_million=1.25,
    ddb_read_eur_per_million=0.25,
    ddb_storage_eur_per_gb_month=0.25,
    apigw_eur_per_million_req=1.0,
    data_transfer_eur_per_gb=0.09,
    item_bytes=150,
)
CAP = Capex(2.0, 3.0, 10.0, 16, 15.0, 1000.0, 2000.0)
LOAD = LoadParams(events_per_spot_per_day=20.0, dashboard_consumers=1.0, poll_interval_s=2.5, hours_open_per_day=16.0)


def test_write_messages_linear_in_spots():
    u1 = monthly_usage(200, LOAD, AWS, CAP)
    u2 = monthly_usage(400, LOAD, AWS, CAP)
    assert abs(u2.write_messages - 2 * u1.write_messages) < 1e-6


def test_write_messages_value():
    u = monthly_usage(200, LOAD, AWS, CAP)
    assert abs(u.write_messages - 20.0 * 200 * DAYS_PER_MONTH) < 1e-6


def test_read_requests_independent_of_spots_but_reads_grow():
    u1 = monthly_usage(200, LOAD, AWS, CAP)
    u2 = monthly_usage(400, LOAD, AWS, CAP)
    assert abs(u1.read_requests - u2.read_requests) < 1e-6   # cadence-driven, not spot-driven
    assert u2.ddb_read_units > u1.ddb_read_units             # bigger query reads more bytes


def test_ddb_read_units_per_query():
    # 200 spots x 150 B = 30000 B -> ceil(30000/4096)=8 pages -> 8 * 0.5 = 4 RRU
    assert ddb_read_units_per_query(200, 150) == 4.0


def test_events_from_manifest_uses_simulated_duration():
    manifest = {"transitionMessages": 3600, "durationSeconds": 3600, "spots": 100, "sendSeconds": 60}
    # 3600 msgs / 3600 s / 100 spots = 0.01 /spot/s * 86400 = 864 /spot/day (ignores sendSeconds)
    assert abs(events_per_spot_per_day_from_manifest(manifest) - 864.0) < 1e-6
