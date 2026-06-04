# backend/api/

API Gateway definition (Phase 3A.5) — data-flow step 6.

HTTP API, Lambda-proxy to the aggregation handler. Exposes aggregated values to consumers
(web view, third-party navigation):

`GET /garages/{garageId}/utilization` → `{ garageId, totalSpots, occupied, free, utilization,
light, spots[] }`.
