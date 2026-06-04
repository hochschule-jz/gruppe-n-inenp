# gruppe-n-inenp

**Drive & Decide** — a prototypical IoT-based Smart Parking System on a serverless AWS
architecture, used as the basis for an operator cost-benefit model. Hochschule Burgenland
(Seier & Zankl).

## Repository layout

### Papers (LaTeX)
- `Projektidee/` — initial project idea.
- `Position Paper/` — the position paper establishing the problem, approach, and method.
- `Final Paper/` — the empirical evaluation (quantitative results feed in here).

### Engineering
- `firmware/` — shared ESP32 sketch (TCRT5000 → MQTT → AWS IoT Core).
- `backend/` — AWS serverless pipeline (IoT Core, validation/aggregation Lambdas, DynamoDB, API Gateway).
- `virtual/` — virtual prototype: MQTT load generator + traffic-light logic.
- `web/` — thin garage-grid + traffic-light visualisation.
- `cost-model/` — CAPEX/OPEX/TCO/ROI/break-even + sensitivity analysis.
- `docs/` — the Phase 0 contract, measurements, demo runbook, screenshots.

Each folder has its own `README.md` with its purpose and the relevant plan phase.

## Start here
1. **`docs/contract.md`** — the locked Phase 0 contract (pin map, MQTT topic, JSON schema,
   identity model). Freeze this before any backend work begins.
2. Both people validate their two TCRT5000 sensors over serial (Phase 1), then publish over
   MQTT (Phase 2). Work then splits into `backend/` (A) and `virtual/`+`web/`+`cost-model/` (B).

## Secrets
Never commit `firmware/**/config.h`, `secrets.h`, or any `*.pem`/`*.key`/cert files — these
are gitignored. Commit the `.example` templates instead.
