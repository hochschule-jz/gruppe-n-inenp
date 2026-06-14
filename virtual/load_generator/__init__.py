"""MQTT load generator for the Drive & Decide virtual parking garage.

Publishes the locked topic + JSON schema (see ``docs/contract.md``) for spots
``1..N``, state-changes only, following a load profile — to AWS IoT Core (or a
non-publishing dry-run sink for testing). The resulting cloud usage feeds the
Phase-5 OPEX numbers.
"""

from .message import build_payload, build_topic, to_json
from .profiles import Profile, ProfileError, load_profile
from .simulator import Event, Simulator
from .stats import RunStats

__all__ = [
    "build_topic",
    "build_payload",
    "to_json",
    "Profile",
    "ProfileError",
    "load_profile",
    "Simulator",
    "Event",
    "RunStats",
]
