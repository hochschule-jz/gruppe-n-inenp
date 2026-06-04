# backend/lambda_validation/

Validation Lambda (Phase 3A.3) — data-flow step 4.

Checks status ∈ {occupied, free} and spot range, then performs an idempotent
`update_item` into the `ParkingStatus` table keyed by `(garageId, spotId)`.
Invoked by the IoT Rule.
