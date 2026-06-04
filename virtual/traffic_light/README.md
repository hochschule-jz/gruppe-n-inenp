# virtual/traffic_light/

Traffic-light logic (Phase 3B.2).

Consumes the aggregation output (polls `GET .../utilization` or subscribes to an aggregate
topic) and drives green/yellow/red using the same thresholds as the backend
(green < 0.70, yellow 0.70–0.90, red > 0.90).
