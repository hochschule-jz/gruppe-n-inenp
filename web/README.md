# web/

Thin web visualisation — the consumer-facing end of the pipeline. Fetches the API and
renders the garage grid + traffic light, refreshing periodically. Kept deliberately
lightweight.

**Plan phase:** 3B.3.

Reads from `GET /garages/{garageId}/utilization` (see [`backend/`](../backend/README.md)).
