# backend/

AWS serverless pipeline: device connectivity → validation → storage → aggregation → API.
Built once; serves the two dev boards or the single demo board identically because it
keys on `spotId`.

**Plan phase:** 3A.
**Status:** implemented and deployed as IaC. The whole backend is defined in
[`template.yaml`](template.yaml) (Lambda code inline), which makes it reproducible (the
paper requires it) and the deploy repeatable. The deploy + post-deploy runbook is in
[`DEPLOY.md`](DEPLOY.md).

## Data flow

```text
sensor/publisher → MQTT topic → IoT Rule → Validation Lambda → DynamoDB
                                                                   ↓
                          API Gateway  ←  Aggregation Lambda  ──────┘
```

1. a sensor (or the virtual load generator) detects a spot's state change,
2. it publishes a contract message to `parking/<garageId>/spot/<spotId>`,
3. AWS IoT Core receives it,
4. the **IoT Rule** routes it to the **validation Lambda**, which checks schema/range and
   writes the current state to DynamoDB,
5. the **aggregation Lambda** queries the table and computes the utilisation + light, and
6. **API Gateway** exposes that aggregate to consumers (web view, navigation, the virtual
   traffic light).

## Components (all defined in `template.yaml`)

| Resource | Role | Phase |
|----------|------|-------|
| IoT policy `drive-decide-iot-publish-policy` | least-privilege: `Connect` + `Publish` to `parking/*/spot/*` only — **no Subscribe/Receive** (so consumers read the REST API, not MQTT) | 3A.1 |
| IoT Rule `drive_decide_parking_status_rule` | `SELECT *, topic(4) AS spotIdFromTopic FROM 'parking/+/spot/+'` → validation Lambda | 3A.1 |
| `ParkingStatus` table | current-state-per-spot, latest-wins, idempotent. PK `garageId` (S), SK `spotId` (N), on-demand (keeps per-request cost measurable for OPEX). Attrs `status`, `raw`, `ts`, `sensorId` | 3A.2 |
| `drive-decide-validation` Lambda | status ∈ {occupied, free} + spot range `1..TotalSpots`, then idempotent `update_item` (data-flow step 4) | 3A.3 |
| `drive-decide-aggregation` Lambda | counts `occupied`, `utilisation = occupied / TotalSpots`, derives light, returns aggregated JSON (steps 5 & 6) | 3A.4–3A.5 |
| HTTP API `drive-decide-api` | `GET /garages/{garageId}/utilization` → `{ garageId, totalSpots, occupied, free, utilization, light, spots[] }` (CORS `*` for the web view) | 3A.5 |

## Deploy (Learner Lab, us-east-1)

```bash
aws cloudformation deploy \
  --region us-east-1 \
  --stack-name drive-and-decide \
  --template-file backend/template.yaml \
  --parameter-overrides TotalSpots=4 \
  --capabilities CAPABILITY_NAMED_IAM
```

Lambda code is kept **inline in the template** (no separate source files), so the template
stays a single, self-contained artifact that deploys without an S3 bucket — convenient in
the Learner Lab. A single `TotalSpots` parameter (default `4`) drives both the validation
range and the aggregation denominator — `4` for the physical demo, `200/400/500` for the
virtual load-generator scale runs (see [`DEPLOY.md`](DEPLOY.md) §2).

## Traffic-light thresholds (shared with virtual/ and web/)
green < 0.70, yellow 0.70–0.90, red > 0.90 — documented and tunable. The aggregation Lambda's
response fields (`utilization`, `light`) are what [`virtual/traffic_light/`](../virtual/traffic_light/)
consumes; they match the contract §0.6.
