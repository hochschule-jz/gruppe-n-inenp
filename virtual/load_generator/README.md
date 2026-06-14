# virtual/load_generator/

MQTT load generator (Phase 3B.1 + Phase 5).

Drives the **identical** locked topic + JSON schema (see
[`docs/contract.md`](../../docs/contract.md)) for spots `1..N` (N up to 200–500),
**state-changes only**, following a named **load profile** — published to AWS
IoT Core. This produces realistic load at scale without hardware, and the
resulting IoT Core / Lambda / DynamoDB usage feeds the Phase-5 OPEX numbers.

## How it works

A pure, deterministic **simulator** is cleanly separated from the MQTT **I/O**:

- **`simulator.py`** — each spot is an independent two-state process
  `free --arrival(λ)--> occupied --departure(μ)--> free`. The steady-state
  occupancy is `λ/(λ+μ)`, so a profile's *target utilisation* + *mean dwell*
  fix the rates and the realised occupancy lands on target. Emits **only state
  changes**; fully reproducible per `seed`; no network, no wall clock.
- **`message.py`** — single source of truth for the topic + contract payload.
- **`publisher.py`** — `DryRunPublisher` (prints/counts, no network) or
  `MqttPublisher` (paho-mqtt mutual TLS to IoT Core, port 8883).
- **`profiles.py`** / **`stats.py`** — load/validate profiles; emit a run
  manifest (params, derived rates, message counts) as the Phase-5 record.

## Load profiles

JSON files specified in human terms; rates are derived from them.

```json
{ "name": "peak", "spots": 350, "targetUtil": 0.88, "dwellMeanMin": 90,
  "durationMin": 60, "timeScale": 1.0, "warmStart": true, "seed": 42 }
```

| Field | Meaning |
|-------|---------|
| `spots` | number of spots `1..N` |
| `targetUtil` | steady-state utilisation in `[0, 1)` |
| `dwellMeanMin` | mean parking duration (minutes) |
| `durationMin` | simulated run length (minutes) |
| `timeScale` | compress simulated time (e.g. `60` ⇒ a 60-min profile sends in 1 min) |
| `warmStart` | start each spot at the steady-state occupancy (default true) |
| `seed` | RNG seed for reproducibility |
| `garageId` / `sensorId` | optional contract-field overrides |

Bundled: [`peak.json`](peak.json), [`offpeak.json`](offpeak.json).

## Usage

```bash
cd virtual
python -m venv .venv && . .venv/Scripts/activate   # Windows; .venv/bin/activate on *nix
pip install -r load_generator/requirements.txt

# Dry-run: print messages + manifest, no network, no AWS cost:
python -m load_generator --profile load_generator/peak.json --duration 1 --quiet

# Publish to AWS IoT Core (needs config.ini + device cert — see below):
python -m load_generator --profile load_generator/peak.json --transport aws --manifest run.json
```

Useful flags: `--transport {dry-run,aws}`, `--spots/--seed/--duration/--time-scale`
(override the profile), `--qos {0,1}` (default 0, matching the firmware),
`--no-initial-snapshot`, `--realtime/--no-realtime`, `--manifest PATH`.

### Initial snapshot
By default the generator publishes every spot's state once at t0 (so DynamoDB
has a full picture immediately), then only state changes. This adds N messages —
the manifest reports them separately. Disable with `--no-initial-snapshot`.

## AWS connection (transport=aws)

Copy [`config.example.ini`](config.example.ini) to `config.ini` and fill in your
account's ATS endpoint, a **distinct** `clientId` (IoT Core force-disconnects
duplicates — contract §0.5), and the paths to your device cert/key + Amazon Root
CA. The device IoT policy must allow publishing to `parking/garage1/spot/*`
(already provisioned by the backend setup). **Never commit `config.ini` or the
cert/key files** — they are gitignored.

## Test

```bash
pip install -r load_generator/requirements.txt
pytest load_generator      # or: pytest   (runs both virtual packages)
```
