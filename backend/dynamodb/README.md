# backend/dynamodb/

`ParkingStatus` table definition / IaC (Person A, Phase 3A.2).

Current-state-per-spot, latest-wins, idempotent. **PK `garageId` (S)**, **SK `spotId` (N)**,
on-demand capacity (keeps per-request cost measurable for OPEX). Attributes: `status`, `raw`,
`ts`, `sensorId`.
