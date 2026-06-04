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
