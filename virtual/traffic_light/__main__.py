"""Minimal manual poll for the entrance traffic light.

The traffic light is primarily a library; this entry point exists for quick
sanity checks against a deployed backend::

    python -m traffic_light --api https://abc123.execute-api.eu-central-1.amazonaws.com
    python -m traffic_light --api <url> --garage garage1 --watch --interval 5
"""

from __future__ import annotations

import argparse
import sys
import time

from .client import UtilizationError, fetch_utilization
from .thresholds import classify

_ANSI = {"green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m"}
_RESET = "\033[0m"


def _format(payload: dict) -> str:
    util = payload.get("utilization")
    light = payload.get("light") or (classify(float(util)) if util is not None else "?")
    colour = _ANSI.get(light, "")
    util_str = f"{float(util):.2f}" if util is not None else "?"
    occ = payload.get("occupied", "?")
    total = payload.get("totalSpots", "?")
    return f"util={util_str} ({occ}/{total}) {colour}{str(light).upper()}{_RESET}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="traffic_light", description=__doc__)
    parser.add_argument("--api", required=True, help="API Gateway base URL")
    parser.add_argument("--garage", default="garage1", help="garageId (default: garage1)")
    parser.add_argument("--watch", action="store_true", help="poll repeatedly")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds between polls")
    parser.add_argument("--timeout", type=float, default=5.0, help="request timeout (s)")
    args = parser.parse_args(argv)

    def poll_once() -> int:
        try:
            payload = fetch_utilization(args.api, args.garage, timeout=args.timeout)
        except UtilizationError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(_format(payload))
        return 0

    if not args.watch:
        return poll_once()

    try:
        while True:
            poll_once()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
