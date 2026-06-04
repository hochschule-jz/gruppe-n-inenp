# backend/

AWS serverless pipeline: device connectivity → validation → storage → aggregation → API.
Built once; serves the two dev boards or the single demo board identically because it
keys on `spotId`.

**Plan phase:** 3A.

## Layout
- `iot/` — IoT Core thing/cert notes, least-privilege policy JSON, IoT Rule SQL
  (`SELECT *, topic(4) AS spotIdFromTopic FROM 'parking/+/spot/+'`).
- `lambda_validation/` — validation handler (schema/range/plausibility, then write to DynamoDB).
- `lambda_aggregation/` — aggregation handler (utilisation rate + traffic-light state) and the
  API handler behind API Gateway.
- `dynamodb/` — `ParkingStatus` table definition / IaC (PK `garageId` S, SK `spotId` N, on-demand).
- `api/` — API Gateway definition (OpenAPI or IaC). `GET /garages/{garageId}/utilization`.
- `infra/` — optional SAM / CDK / Terraform templates tying the above together.

## Traffic-light thresholds (shared with virtual/ and web/)
green < 0.70, yellow 0.70–0.90, red > 0.90 — documented and tunable.
