# firmware/

Shared ESP32 firmware (PlatformIO project) for reading the TCRT5000 occupancy sensors
and publishing state changes over MQTT to AWS IoT Core.

**Plan phases:** 0, 1, 2, 6.
**Toolchain:** PlatformIO (VS Code extension). This folder is the PlatformIO project root.

## Layout
- `platformio.ini` — board, framework, libraries, serial baud.
- `src/main.cpp` — main firmware (WiFi + TLS + MQTT + event-driven publish loop).
- `include/` — shared headers (added during Phase 0–2):
  - `spots.h` — the `SPOTS[]` array (`{spotId, gpio, occupiedWhenHigh}`). **Merging two
    2-sensor boards into the 4-sensor demo board = extending this array from 2 to 4 entries.**
  - `config.example.h` — committed template (WiFi, AWS endpoint, client ID, sensor ID, garage ID).
  - `config.h` — **gitignored**, real per-board values. Copy from the example.
  - `secrets.example.h` — committed template for device cert / key / root CA references.
- `.pio/` — build output, **gitignored**.

## Build & upload (PlatformIO)
- Build: PlatformIO toolbar ✓, or `pio run`.
- Upload to the board: → (Upload), or `pio run -t upload`.
- Serial monitor: 🔌, or `pio device monitor` (115200 baud).

## Contract (locked in Phase 0 — see `docs/contract.md`)
- Pin map: spot 1→GPIO32, 2→GPIO33, 3→GPIO25, 4→GPIO26 (see `docs/contract.md`).
- Topic: `parking/<garageId>/spot/<spotId>` (e.g. `parking/garage1/spot/3`).
- Power TCRT5000 modules from **3V3**, not 5V (DO pulls up to VCC; 5V over-drives the GPIO).
