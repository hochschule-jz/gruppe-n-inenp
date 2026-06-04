# backend/iot/

AWS IoT Core configuration (Person A, Phase 3A.1).

Holds: thing + certificate notes, the least-privilege device **policy JSON**, and the
**IoT Rule SQL** that routes `parking/+/spot/+` messages to the validation Lambda.

Dev uses two distinct MQTT client IDs (`esp32-a`, `esp32-b`); the demo uses one thing /
one client ID. **Never commit private keys or `*.pem` certificate files.**
