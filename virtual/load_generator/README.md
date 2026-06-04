# virtual/load_generator/

MQTT load generator (Person B, Phase 3B.1 + Phase 5).

A script (Python `paho-mqtt` or AWS IoT Device SDK) that connects to IoT Core with a cert
and publishes the locked topic + JSON schema for spots `1..N` following a **load profile**
(arrival/departure rates, peak/off-peak). N, rate, and duration are parameters. Publishes
**only state changes** to mirror real device behaviour.

Profiles live here as JSON (e.g. `peak.json`, `offpeak.json`). **Do not commit certs/keys.**
