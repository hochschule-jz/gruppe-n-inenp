#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

// Per-board config (WiFi, AWS endpoint, IDs) and device credentials
// (root CA, device cert, private key). Both headers are gitignored — copy
// from the committed config.example.h / secrets.example.h templates.
#include "config.h"
#include "secrets.h"

// ---------- Sensor-Konfiguration ----------
// Actual demo-box wiring: four TCRT5000 sensors on GPIO 4/16/18/19, one under
// each marked spot — matches docs/contract.md §0.1. All four read HIGH when a
// spot is occupied (occupiedWhenHigh=true), matching the previously tested firmware.
struct Spot {
  int spotId;
  int gpio;
  bool occupiedWhenHigh;  // does an occupied spot read HIGH on this sensor?
};

Spot SPOTS[] = {
  {1, 4, true},
  {2, 16, true},
  {3, 18, true},
  {4, 19, true}
};

const int SPOT_COUNT = sizeof(SPOTS) / sizeof(SPOTS[0]);

// Derive occupancy from a raw digitalRead, honouring each spot's polarity.
bool isOccupied(const Spot& s, int raw) {
  return (raw == HIGH) == s.occupiedWhenHigh;
}

// Letzter bekannter Zustand
bool lastOccupied[SPOT_COUNT];

WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void syncTime() {
  Serial.println("Syncing time via NTP...");

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  time_t now = time(nullptr);
  int retries = 0;

  while (now < 100000 && retries < 30) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
    retries++;
  }

  Serial.println();

  if (now < 100000) {
    Serial.println("NTP time sync failed");
  } else {
    Serial.println("Time synced");
    Serial.println(ctime(&now));
  }
}

unsigned long long epochMillis() {
  struct timeval tv;
  gettimeofday(&tv, nullptr);
  return ((unsigned long long)tv.tv_sec * 1000ULL) + (tv.tv_usec / 1000ULL);
}

void connectAWS() {
  secureClient.setCACert(AWS_ROOT_CA);
  secureClient.setCertificate(DEVICE_CERT);
  secureClient.setPrivateKey(DEVICE_PRIVATE_KEY);

  mqttClient.setServer(AWS_IOT_ENDPOINT, 8883);

  Serial.print("Connecting to AWS IoT Core");

  while (!mqttClient.connected()) {
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println();
      Serial.println("Connected to AWS IoT Core");
    } else {
      Serial.print(".");
      Serial.print(" failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void publishSpotStatus(int spotId, int raw, bool occupied) {
  char topic[80];
  snprintf(topic, sizeof(topic), "parking/%s/spot/%d", GARAGE_ID, spotId);

  StaticJsonDocument<256> doc;
  doc["sensorId"] = SENSOR_ID;
  doc["garageId"] = GARAGE_ID;
  doc["spotId"] = spotId;
  doc["ts"] = epochMillis();
  doc["raw"] = raw;
  doc["status"] = occupied ? "occupied" : "free";

  char payload[256];
  serializeJson(doc, payload);

  Serial.print("Publishing to topic: ");
  Serial.println(topic);
  Serial.print("Payload: ");
  Serial.println(payload);

  bool ok = mqttClient.publish(topic, payload);

  if (ok) {
    Serial.println("Publish successful");
  } else {
    Serial.println("Publish failed");
  }
}

void setupSensors() {
  Serial.println("Setting up sensors...");

  for (int i = 0; i < SPOT_COUNT; i++) {
    pinMode(SPOTS[i].gpio, INPUT);

    int raw = digitalRead(SPOTS[i].gpio);
    bool occupied = isOccupied(SPOTS[i], raw);

    lastOccupied[i] = occupied;

    Serial.print("Initial state Spot ");
    Serial.print(SPOTS[i].spotId);
    Serial.print(": raw=");
    Serial.print(raw);
    Serial.print(", status=");
    Serial.println(occupied ? "occupied" : "free");
  }
}

void publishInitialStates() {
  Serial.println("Publishing initial sensor states...");

  for (int i = 0; i < SPOT_COUNT; i++) {
    int raw = digitalRead(SPOTS[i].gpio);
    bool occupied = isOccupied(SPOTS[i], raw);

    publishSpotStatus(SPOTS[i].spotId, raw, occupied);
    delay(300);
  }
}

void checkSensorsAndPublishChanges() {
  for (int i = 0; i < SPOT_COUNT; i++) {
    int raw = digitalRead(SPOTS[i].gpio);
    bool occupied = isOccupied(SPOTS[i], raw);

    if (occupied != lastOccupied[i]) {
      Serial.print("Change detected on Spot ");
      Serial.print(SPOTS[i].spotId);
      Serial.print(": ");
      Serial.println(occupied ? "occupied" : "free");

      publishSpotStatus(SPOTS[i].spotId, raw, occupied);

      lastOccupied[i] = occupied;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  setupSensors();

  connectWiFi();
  syncTime();
  connectAWS();

  publishInitialStates();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
  Serial.println("WiFi disconnected, reconnecting...");
  connectWiFi();
  }

  if (!mqttClient.connected()) {
    connectAWS();
  }

  mqttClient.loop();

  checkSensorsAndPublishChanges();

  delay(50);
}
