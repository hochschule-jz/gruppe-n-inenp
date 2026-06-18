"""Drive & Decide — operator cost-benefit model.

Implements the method fixed in the Final Paper (``methodology.tex`` §Kosten-Nutzen-Analyse):
operator perspective, 5-year horizon, CAPEX vs. OPEX, four benefit pathways and the four
KPIs (TCO, ROI, amortisation, break-even). The package is deliberately shaped like
``virtual/load_generator/``: pure, typed, reproducible, and dependency-free at its core
(stdlib ``tomllib`` for the assumptions, no third-party packages needed to compute).

Pipeline fit::

    profiles -> load_generator -> run manifest (awsUsageEstimate)
             -> cost_model: usage -> capex/opex/benefits -> kpis/sensitivity
             -> tables/figures -> Final Paper evaluation.tex + presentation slides 11-14
"""

from .config import load_assumptions
from .model import evaluate

__all__ = ["load_assumptions", "evaluate"]
