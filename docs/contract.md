# Drive & Decide — Phase 0 Contract

**Status:** locked. This is the shared contract that lets both people build independently
and merge without rework. Backend code depends on the exact message shape and topic, so
**these decisions are frozen before any backend work begins.** Change them only by mutual
agreement, and update this file when you do.

---

## 0.1 Pin map

Fixed, non-overlapping GPIOs so all four sensors fit one board for the demo. GPIO
32/33/25/26 are input-capable and free of boot-strapping/flash conflicts.

| Spot | GPIO | Dev board |
|------|------|-----------|
| 1 | GPIO 32 | A |
| 2 | GPIO 33 | A |
| 3 | GPIO 25 | B |
| 4 | GPIO 26 | B |

> GPIO 25/26 are ADC2/DAC pins — fine as **digital** inputs (what we use). Do not
> `analogRead` them while WiFi is active (ADC2 is unavailable during WiFi). We use
> `digitalRead`, so this is a non-issue.

---

## 0.2 MQTT topic scheme

```
parking/<garageId>/spot/<spotId>      e.g. parking/garage1/spot/3
```

- `garageId = garage1` for the demo.
- The spot ID appears in **both** the topic (for routing/wildcards) and the payload
  (authoritative for storage).
- Backend subscribes/routes with the wildcard `parking/+/spot/+`.

---

## 0.3 Message format (JSON)

Mirrors the paper's "sensor ID, spot ID, timestamp, raw value, derived status".

```json
{
  "sensorId": "esp32-a",
  "garageId": "garage1",
  "spotId": 3,
  "ts": 1735680000000,
  "raw": 1,
  "status": "occupied"
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `sensorId` | string | identifies the publishing board (free during dev; one value for the demo) |
| `garageId` | string | `garage1` for the demo |
| `spotId` | number | 1–4; authoritative for storage |
| `ts` | number | epoch **milliseconds** (from NTP/`time()`) |
| `raw` | number | the digital read (0/1) for the TCRT5000 |
| `status` | string | `"occupied"` or `"free"` |

Published **only on state change** (event-driven), to mirror real device behaviour and to
keep cloud-usage costs measurable.

---

## 0.4 Shared firmware skeleton

Both people write identical code except their two `SPOTS[]` entries and their per-board
`config.h`. **Merging two 2-sensor boards into the 4-sensor demo board = extending this
array from 2 to 4 entries. Nothing else changes.**

```cpp
// include/spots.h — the shared skeleton.
struct Spot { int spotId; int gpio; bool occupiedWhenHigh; };

Spot SPOTS[] = {
  { 1, 32, true },   // board A (dev)
  { 2, 33, true },
  // board B (dev):  { 3, 25, true }, { 4, 26, true }
  // DEMO board:     all four entries present
};
const int SPOT_COUNT = sizeof(SPOTS) / sizeof(SPOTS[0]);
```

`occupiedWhenHigh` is set per spot from the polarity recorded in Phase 1 (does "occupied"
read HIGH or LOW on that sensor?).

```cpp
// the SINGLE shared publish function — identical on every board
void publishSpot(const Spot& s, int raw, bool occupied) {
  char topic[64];
  snprintf(topic, sizeof(topic), "parking/%s/spot/%d", GARAGE_ID, s.spotId);
  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"sensorId\":\"%s\",\"garageId\":\"%s\",\"spotId\":%d,"
    "\"ts\":%llu,\"raw\":%d,\"status\":\"%s\"}",
    SENSOR_ID, GARAGE_ID, s.spotId, epochMillis(), raw, occupied ? "occupied" : "free");
  client.publish(topic, payload);
  Serial.println(payload);   // also visible on serial for validation
}
```

---

## 0.5 Identity & AWS endpoint model

**We each run our own AWS account** (separate IoT Core, Lambda, DynamoDB, API Gateway).
This is fine for development — what keeps the two accounts mergeable is that **0.1–0.4 are
identical on both sides.**

- **Per board (dev):** `config.h` holds *your own* account's `-ats` IoT endpoint plus a
  **distinct MQTT client ID** (`esp32-a`, `esp32-b`). Distinct client IDs matter because
  IoT Core force-disconnects duplicate client IDs.
- **For the demo:** pick **one** account. The single 4-sensor board uses **one thing / one
  client ID** and publishes all four spots to that account's endpoint. Because the backend
  keys on `spotId`, storage is unaffected by which identity published — but this only works
  if both backends were built to this contract.
- **Cost data (Phase 5):** measure one account as the "official" set, or compare both.

Never commit `config.h`, `secrets.h`, private keys, or `*.pem` files — use the `.example`
templates.

---

## 0.6 Shared constants (lock once, reference everywhere)

The traffic-light thresholds are used by the backend aggregation, the virtual traffic
light, and the web view — they must agree. Documented and tunable, changed only here.

| Light | Utilisation |
|-------|-------------|
| 🟢 green | `< 0.70` |
| 🟡 yellow | `0.70 – 0.90` |
| 🔴 red | `> 0.90` |

`utilisation = occupied / totalSpots`.
