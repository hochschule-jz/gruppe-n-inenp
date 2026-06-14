# virtual/

The virtual prototype: a software load generator that drives the same MQTT path at
scale (no extra hardware), plus the entrance traffic light driven by aggregated occupancy.

**Plan phase:** 3B (and Phase 5 for load-at-scale measurements).

## Layout
- `load_generator/` — MQTT load generator + named load profiles (e.g. `peak.json`,
  `offpeak.json`). Publishes the **identical topic + JSON schema** for spots `1..N`
  (N up to 200–500), state-changes only, to produce realistic load and the cloud-usage
  numbers OPEX needs.
- `traffic_light/` — consumes the aggregation output and drives green/yellow/red from the
  same thresholds as the backend (green < 0.70, yellow 0.70–0.90, red > 0.90).

## Tooling
Both are Python 3.11+ packages run with `python -m` and tested with `pytest`. Each has its
own `requirements.txt`. From this folder:

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows; .venv/bin/activate on *nix
pip install -r load_generator/requirements.txt -r traffic_light/requirements.txt
pytest        # runs both packages' tests (config in pytest.ini)
```

`load_generator` needs `paho-mqtt` (for `--transport aws`); `traffic_light` is
standard-library only.
