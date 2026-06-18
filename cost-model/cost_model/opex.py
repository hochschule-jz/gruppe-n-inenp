"""OPEX: annual recurring cost = usage-based AWS line items + non-cloud costs.

AWS line items are derived from the monthly :class:`~cost_model.usage.Usage` quantities and
the unit prices, then annualised. Non-cloud costs are maintenance (a share of CAPEX), sensor
replacement, and controller power.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import AwsPrices, NonCloudOpex
from .usage import Usage

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class OpexBreakdown:
    iot: float
    lambda_: float
    dynamodb: float
    api_gateway: float
    data_transfer: float
    maintenance: float
    sensor_replacement: float
    power: float

    @property
    def aws_annual(self) -> float:
        return self.iot + self.lambda_ + self.dynamodb + self.api_gateway + self.data_transfer

    @property
    def non_cloud_annual(self) -> float:
        return self.maintenance + self.sensor_replacement + self.power

    @property
    def total_annual(self) -> float:
        return self.aws_annual + self.non_cloud_annual


def opex_annual(
    spots: int,
    usage: Usage,
    aws: AwsPrices,
    nc: NonCloudOpex,
    capex_total: float,
    sensor_eur: float,
) -> OpexBreakdown:
    """Annual OPEX breakdown. ``usage`` quantities are monthly and annualised here."""
    iot = (
        usage.write_messages / 1e6 * aws.iot_messaging_eur_per_million
        + usage.iot_connection_minutes / 1e6 * aws.iot_connection_eur_per_million_min
    ) * MONTHS_PER_YEAR

    lambda_ = (
        usage.lambda_invocations / 1e6 * aws.lambda_eur_per_million_req
        + usage.lambda_gb_seconds * aws.lambda_eur_per_gb_second
    ) * MONTHS_PER_YEAR

    dynamodb = (
        usage.write_messages / 1e6 * aws.ddb_write_eur_per_million
        + usage.ddb_read_units / 1e6 * aws.ddb_read_eur_per_million
        + usage.storage_gb * aws.ddb_storage_eur_per_gb_month
    ) * MONTHS_PER_YEAR

    api_gateway = usage.read_requests / 1e6 * aws.apigw_eur_per_million_req * MONTHS_PER_YEAR
    data_transfer = usage.data_transfer_gb * aws.data_transfer_eur_per_gb * MONTHS_PER_YEAR

    maintenance = nc.maintenance_pct_of_capex * capex_total
    sensor_replacement = nc.sensor_replacement_pct * spots * sensor_eur
    power = nc.power_eur_per_controller_year * usage.controllers

    return OpexBreakdown(
        iot=iot,
        lambda_=lambda_,
        dynamodb=dynamodb,
        api_gateway=api_gateway,
        data_transfer=data_transfer,
        maintenance=maintenance,
        sensor_replacement=sensor_replacement,
        power=power,
    )
