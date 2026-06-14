"""Run statistics + manifest — the reproducible record a measurement run leaves.

The manifest is the artifact that feeds the Phase-5 OPEX table: it pins the
exact parameters and derived rates of the run and counts the messages produced.
Because the pipeline is event-driven and one message triggers one validation
Lambda invocation and one DynamoDB write, the total message count is also the
IoT-inbound-message / Lambda-invocation / DynamoDB-write count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunStats:
    profile_name: str
    spots: int
    target_util: float
    dwell_mean_min: float
    arrival_rate: float
    departure_rate: float
    seed: int
    duration_seconds: float
    time_scale: float
    transport: str = "dry-run"

    initial_messages: int = 0
    transition_messages: int = 0
    occupied_messages: int = 0
    free_messages: int = 0
    _initial_occupied: int = field(default=0, repr=False)

    def record(self, occupied: bool, *, initial: bool = False) -> None:
        if initial:
            self.initial_messages += 1
            if occupied:
                self._initial_occupied += 1
        else:
            self.transition_messages += 1
        if occupied:
            self.occupied_messages += 1
        else:
            self.free_messages += 1

    @property
    def total_messages(self) -> int:
        return self.initial_messages + self.transition_messages

    @property
    def send_seconds(self) -> float:
        return self.duration_seconds / self.time_scale

    @property
    def messages_per_second(self) -> float:
        """Throughput over the real send window (drives IoT/Lambda/DDB load)."""
        return self.total_messages / self.send_seconds if self.send_seconds else 0.0

    @property
    def initial_util(self) -> float:
        return self._initial_occupied / self.initial_messages if self.initial_messages else 0.0

    def manifest(self) -> dict[str, Any]:
        return {
            "profile": self.profile_name,
            "transport": self.transport,
            "spots": self.spots,
            "targetUtil": self.target_util,
            "dwellMeanMin": self.dwell_mean_min,
            "arrivalRatePerSpotPerSec": self.arrival_rate,
            "departureRatePerSpotPerSec": self.departure_rate,
            "seed": self.seed,
            "durationSeconds": self.duration_seconds,
            "timeScale": self.time_scale,
            "sendSeconds": self.send_seconds,
            "initialSnapshotMessages": self.initial_messages,
            "initialSnapshotUtil": round(self.initial_util, 4),
            "transitionMessages": self.transition_messages,
            "occupiedMessages": self.occupied_messages,
            "freeMessages": self.free_messages,
            "totalMessages": self.total_messages,
            "messagesPerSecond": round(self.messages_per_second, 4),
            # One message == one IoT inbound message == one validation Lambda
            # invocation == one DynamoDB write.
            "awsUsageEstimate": {
                "iotMessages": self.total_messages,
                "validationLambdaInvocations": self.total_messages,
                "dynamodbWrites": self.total_messages,
            },
        }
