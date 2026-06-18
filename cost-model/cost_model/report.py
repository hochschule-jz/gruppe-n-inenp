"""Render the model output as Markdown tables + a CSV export.

Stdlib only, so the figures/tables for the paper and the slides are produced from the same
single run as the numbers — no manual copying.
"""

from __future__ import annotations

import csv
import math

from .sensitivity import ScaleRow, TornadoRow


def _eur(x: float) -> str:
    return f"{x:,.0f}"


def _pp(x: float) -> str:
    return "n/a" if math.isinf(x) else f"{x:.2f}"


def _months(x: float) -> str:
    return "never" if math.isinf(x) else f"{x:.0f}"


def _pct(x: float) -> str:
    return "n/a" if math.isinf(x) else f"{x * 100:,.0f}%"


def scale_table_md(rows: list[ScaleRow], currency: str = "EUR") -> str:
    header = (
        f"| Spots | CAPEX ({currency}) | OPEX/yr ({currency}) | TCO 5y ({currency}) "
        f"| Break-even Δpp | ROI | Payback (mo) |"
    )
    sep = "|---:|---:|---:|---:|---:|---:|---:|"
    body = "\n".join(
        f"| {r.spots} | {_eur(r.capex_total)} | {_eur(r.opex_annual)} | {_eur(r.tco)} "
        f"| {_pp(r.breakeven_uplift_pp)} | {_pct(r.roi)} | {_months(r.payback_months)} |"
        for r in rows
    )
    return "\n".join([header, sep, body])


def tornado_table_md(rows: list[TornadoRow]) -> str:
    header = "| Lever | low value | high value | ROI low | ROI high | swing (ROI pp) |"
    sep = "|---|---:|---:|---:|---:|---:|"
    body = "\n".join(
        f"| {r.lever} | {r.low_value:,.2f} | {r.high_value:,.2f} "
        f"| {_pct(r.low_roi)} | {_pct(r.high_roi)} | {r.swing * 100:,.0f} |"
        for r in rows
    )
    return "\n".join([header, sep, body])


def write_scale_csv(path: str, rows: list[ScaleRow]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["spots", "capex_total", "opex_annual", "tco_5y", "breakeven_uplift_pp", "roi", "payback_months"]
        )
        for r in rows:
            payback = "" if math.isinf(r.payback_months) else round(r.payback_months, 1)
            w.writerow(
                [
                    r.spots,
                    round(r.capex_total, 2),
                    round(r.opex_annual, 2),
                    round(r.tco, 2),
                    round(r.breakeven_uplift_pp, 4),
                    round(r.roi, 4),
                    payback,
                ]
            )
