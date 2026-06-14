# virtual/traffic_light/

Traffic-light logic (Phase 3B.2).

A **library-only** component: it exposes the canonical green/yellow/red
classification and a thin helper that polls the backend utilisation API. The
rich garage-grid + light visualisation lives in [`web/`](../../web/); this
package is the shared logic those consumers build on.

## Thresholds (canonical)

`thresholds.py` is the single Python source of truth for the traffic-light
thresholds and mirrors [`docs/contract.md`](../../docs/contract.md) §0.6. It must
stay equal to the backend aggregation Lambda and the web view — change the
contract first, then this file.

`utilisation = occupied / totalSpots`

| Light | Utilisation |
|-------|-------------|
| 🟢 green | `< 0.70` |
| 🟡 yellow | `0.70 – 0.90` (inclusive) |
| 🔴 red | `> 0.90` |

## Data source

It consumes the API the backend already exposes
(`GET /garages/{garageId}/utilization`, see [`backend/`](../../backend/README.md)),
which returns both `utilization` and a server-computed `light`. **No new AWS
configuration is required.** `current_light()` trusts the backend's `light` but
re-derives it locally to catch threshold drift between backend and prototype.

## Usage (library)

```python
from traffic_light import classify, current_light

classify(0.82)                       # -> "yellow"
current_light("https://<api-base>", "garage1")   # polls the API -> "green"|"yellow"|"red"
```

## Manual poll (sanity check)

```bash
python -m traffic_light --api https://<api-id>.execute-api.<region>.amazonaws.com --garage garage1
python -m traffic_light --api <url> --watch --interval 5     # poll repeatedly
```

## Develop & test

```bash
cd virtual
python -m venv .venv && . .venv/Scripts/activate   # Windows; use .venv/bin/activate on *nix
pip install -r traffic_light/requirements.txt
pytest traffic_light
```

No runtime dependencies (standard-library `urllib` only).
