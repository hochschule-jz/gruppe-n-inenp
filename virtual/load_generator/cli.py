"""Command-line driver: profile -> simulator -> publisher, with a run manifest.

The orchestration loop (:func:`run_load`) is dependency-injected (publisher,
clock, sleep) so it can be exercised with a :class:`DryRunPublisher` and a fake
clock in tests — no network, no real waiting.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path
from typing import Callable

from .message import build_payload, build_topic, to_json
from .profiles import Profile, load_profile
from .publisher import DryRunPublisher, Publisher
from .simulator import Simulator
from .stats import RunStats


def run_load(
    profile: Profile,
    publisher: Publisher,
    *,
    qos: int = 0,
    emit_initial: bool = True,
    realtime: bool = False,
    transport: str = "dry-run",
    stats: RunStats | None = None,
    base_ms: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> RunStats:
    """Drive one load run and return its statistics."""
    sim = Simulator(
        profile.spots,
        profile.arrival_rate,
        profile.departure_rate,
        profile.seed,
        warm_start=profile.warm_start,
    )
    if stats is None:
        stats = RunStats(
            profile_name=profile.name,
            spots=profile.spots,
            target_util=profile.target_util,
            dwell_mean_min=profile.dwell_mean_min,
            arrival_rate=profile.arrival_rate,
            departure_rate=profile.departure_rate,
            seed=profile.seed,
            duration_seconds=profile.duration_seconds,
            time_scale=profile.time_scale,
            transport=transport,
        )
    if base_ms is None:
        base_ms = int(time.time() * 1000)
    start_mono = monotonic()

    def ts_ms(t: float) -> int:
        return base_ms + int(round((t / profile.time_scale) * 1000))

    def emit(spot_id: int, occupied: bool, ts: int) -> None:
        payload = to_json(
            build_payload(
                spot_id=spot_id,
                occupied=occupied,
                ts_ms=ts,
                garage_id=profile.garage_id,
                sensor_id=profile.sensor_id,
            )
        )
        publisher.publish(build_topic(profile.garage_id, spot_id), payload, qos)

    # Initial snapshot: report every spot's warm-start state once, so DynamoDB
    # has a full picture and aggregated utilisation is correct immediately.
    if emit_initial:
        for spot_id, occupied in sorted(sim.initial_states.items()):
            emit(spot_id, occupied, base_ms)
            stats.record(occupied, initial=True)

    for ev in sim.events(profile.duration_seconds):
        if realtime:
            delay = (start_mono + ev.t / profile.time_scale) - monotonic()
            if delay > 0:
                sleep(delay)
        emit(ev.spot_id, ev.occupied, ts_ms(ev.t))
        stats.record(ev.occupied)

    return stats


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="load_generator",
        description="MQTT load generator for the Drive & Decide virtual garage.",
    )
    p.add_argument("--profile", required=True, help="path to a load-profile JSON")
    p.add_argument("--transport", choices=["dry-run", "aws"], default="dry-run",
                   help="dry-run prints messages; aws publishes to IoT Core (default: dry-run)")
    p.add_argument("--config", default="config.ini", help="AWS config INI (transport=aws)")
    p.add_argument("--spots", type=int, help="override profile spot count")
    p.add_argument("--seed", type=int, help="override profile seed")
    p.add_argument("--duration", type=float, metavar="MIN", help="override profile durationMin")
    p.add_argument("--time-scale", type=float, dest="time_scale",
                   help="override profile timeScale (compress simulated time)")
    p.add_argument("--qos", type=int, choices=[0, 1], default=0, help="MQTT QoS (default: 0)")
    p.add_argument("--no-initial-snapshot", action="store_false", dest="emit_initial",
                   help="do not publish the t0 snapshot of all spots")
    p.add_argument("--realtime", action=argparse.BooleanOptionalAction, default=None,
                   help="pace events to wall clock (default: on for aws, off for dry-run)")
    p.add_argument("--manifest", help="write the run manifest JSON to this path")
    p.add_argument("--quiet", action="store_true", help="suppress per-message echo (dry-run)")
    return p


def _apply_overrides(profile: Profile, args: argparse.Namespace) -> Profile:
    changes: dict = {}
    if args.spots is not None:
        changes["spots"] = args.spots
    if args.seed is not None:
        changes["seed"] = args.seed
    if args.duration is not None:
        changes["duration_min"] = args.duration
    if args.time_scale is not None:
        changes["time_scale"] = args.time_scale
    return dataclasses.replace(profile, **changes) if changes else profile


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        profile = _apply_overrides(load_profile(args.profile), args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    realtime = (args.transport == "aws") if args.realtime is None else args.realtime

    if args.transport == "aws":
        from .config import ConfigError, load_mqtt_config
        from .publisher import MqttPublisher
        try:
            cfg = load_mqtt_config(args.config)
            publisher: Publisher = MqttPublisher(
                endpoint=cfg.endpoint,
                client_id=cfg.client_id,
                cert_file=cfg.cert_file,
                key_file=cfg.key_file,
                ca_file=cfg.ca_file,
                port=cfg.port,
            )
        except (ConfigError, RuntimeError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        # Config may override the identity fields.
        if cfg.garage_id:
            profile = dataclasses.replace(profile, garage_id=cfg.garage_id)
        if cfg.sensor_id:
            profile = dataclasses.replace(profile, sensor_id=cfg.sensor_id)
    else:
        publisher = DryRunPublisher(echo=not args.quiet)

    print(
        f"[loadgen] profile={profile.name} spots={profile.spots} "
        f"targetUtil={profile.target_util} dwellMin={profile.dwell_mean_min} "
        f"transport={args.transport} realtime={realtime} qos={args.qos}",
        file=sys.stderr,
    )

    try:
        stats = run_load(
            profile, publisher,
            qos=args.qos, emit_initial=args.emit_initial,
            realtime=realtime, transport=args.transport,
        )
    except KeyboardInterrupt:
        print("\n[loadgen] interrupted", file=sys.stderr)
        return 130
    finally:
        publisher.close()

    manifest = stats.manifest()
    print(json.dumps(manifest, indent=2), file=sys.stderr)
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"[loadgen] manifest written to {args.manifest}", file=sys.stderr)
    return 0
