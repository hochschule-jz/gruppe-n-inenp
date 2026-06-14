"""Virtual entrance traffic light for Drive & Decide.

Library-only: it exposes the canonical green/yellow/red logic and a thin helper
that polls the backend utilisation API. The rich grid + light visualisation
lives in ``web/``.
"""

from .client import UtilizationError, current_light, fetch_utilization
from .thresholds import GREEN_MAX, YELLOW_MAX, Light, classify

__all__ = [
    "GREEN_MAX",
    "YELLOW_MAX",
    "Light",
    "classify",
    "fetch_utilization",
    "current_light",
    "UtilizationError",
]
