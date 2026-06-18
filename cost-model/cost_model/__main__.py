"""CLI: ``python -m cost_model`` -> scale sweep + sensitivity as Markdown (+ optional CSV).

Run from the ``cost-model/`` directory. Examples::

    python -m cost_model                                  # base scenario, default assumptions
    python -m cost_model --scenario optimistic --csv out.csv
    python -m cost_model --manifest ../virtual/run.json   # drive volume from a load-gen run
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from .config import DEFAULT_ASSUMPTIONS, load_assumptions
from .report import scale_table_md, tornado_table_md, write_scale_csv
from .sensitivity import one_way_sensitivity, scale_sweep
from .usage import events_per_spot_per_day_from_manifest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cost_model", description="Drive & Decide operator cost-benefit model.")
    p.add_argument("--assumptions", default=str(DEFAULT_ASSUMPTIONS), help="path to assumptions.toml")
    p.add_argument("--scenario", default="base", choices=["pessimistic", "base", "optimistic"])
    p.add_argument("--manifest", help="load-generator run manifest JSON; drives the write-side volume")
    p.add_argument("--spots", type=int, help="spot count for the sensitivity tornado (default: middle of scale)")
    p.add_argument("--delta", type=float, default=0.30, help="+/- fraction for the tornado (default 0.30)")
    p.add_argument("--csv", help="also write the scale sweep to this CSV path")
    p.add_argument("--figures", metavar="DIR", help="render paper/slide figures (PNG+SVG) to DIR (needs matplotlib)")
    args = p.parse_args(argv)

    a = load_assumptions(args.assumptions)

    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        ev = events_per_spot_per_day_from_manifest(manifest)
        a = replace(a, load=replace(a.load, events_per_spot_per_day=ev))
        print(f"[cost-model] events/spot/day from manifest: {ev:.2f}", file=sys.stderr)

    rows = scale_sweep(a, args.scenario)
    spots = args.spots or a.scale_spot_counts[len(a.scale_spot_counts) // 2]

    print(f"# Drive & Decide — cost-benefit ({args.scenario} scenario, {a.horizon_years}y, r={a.discount_rate})\n")
    print("## Scale sweep\n")
    print(scale_table_md(rows, a.currency))
    print(f"\n## One-way sensitivity — ROI at spots={spots}, ±{args.delta:.0%}\n")
    print(tornado_table_md(one_way_sensitivity(a, spots, args.scenario, args.delta)))
    print("\n> ⚠️ All inputs are placeholders until verified — see cost-model/README.md.")

    if args.csv:
        write_scale_csv(args.csv, rows)
        print(f"[cost-model] scale sweep written to {args.csv}", file=sys.stderr)

    if args.figures:
        from .figures import render_all

        paths = render_all(a, args.figures, args.scenario, spots, args.delta)
        print(f"[cost-model] {len(paths)} figure files written to {args.figures}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
