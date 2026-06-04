# backend/lambda_aggregation/

Aggregation Lambda + API handler (Phase 3A.4–3A.5) — data-flow steps 5 & 6.

Queries `ParkingStatus` for a `garageId`, counts `occupied`, computes
`utilisation = occupied / total`, derives the traffic-light state, and returns the
aggregated JSON behind API Gateway (`GET /garages/{garageId}/utilization`).
