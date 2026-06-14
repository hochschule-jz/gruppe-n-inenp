"""Canonical traffic-light thresholds for Drive & Decide.

This module is the single source of truth in Python for the green/yellow/red
classification. It mirrors ``docs/contract.md`` section 0.6 and MUST stay equal
to the backend aggregation Lambda and the ``web/`` view. Change the thresholds
only in the contract first, then here.

Contract boundaries (utilisation = occupied / totalSpots):

    util  < 0.70          -> green
    0.70 <= util <= 0.90  -> yellow
    util  > 0.90          -> red
"""

from __future__ import annotations

from typing import Literal

Light = Literal["green", "yellow", "red"]

#: Utilisation strictly below this is green.
GREEN_MAX = 0.70
#: Utilisation up to and including this (and >= GREEN_MAX) is yellow; above is red.
YELLOW_MAX = 0.90


def classify(utilisation: float) -> Light:
    """Map a utilisation ratio in ``[0, 1]`` to a traffic-light state.

    Boundaries match the contract exactly: 0.70 is yellow (not green) and 0.90
    is yellow (not red).
    """
    if not 0.0 <= utilisation <= 1.0:
        raise ValueError(f"utilisation must be in [0, 1], got {utilisation!r}")
    if utilisation < GREEN_MAX:
        return "green"
    if utilisation <= YELLOW_MAX:
        return "yellow"
    return "red"
