#pragma once
// Per-board configuration template. COMMITTED.
// Copy this file to config.h (gitignored) and fill in this board's real values.

#define WIFI_SSID         "YOUR_WIFI_SSID"
#define WIFI_PASSWORD     "YOUR_WIFI_PASSWORD"

// Your account's ATS data endpoint: AWS IoT Core > Settings > Device data endpoint.
#define AWS_IOT_ENDPOINT  "xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com"

// Distinct per board — IoT Core force-disconnects duplicate client ids (esp32-a / esp32-b).
#define MQTT_CLIENT_ID    "esp32-a"
#define SENSOR_ID         "esp32-a"
#define GARAGE_ID         "garage1"
