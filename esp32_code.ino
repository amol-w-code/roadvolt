/*
 * ============================================================
 *  RoadVolt – Smart Speed Breaker Energy Harvesting System
 *  ESP32 Firmware
 *  Connect: Voltage Sensor → GPIO34 (A6)
 *           ACS712 Current → GPIO35 (A7)
 *           IR Sensor      → GPIO27 (D27)
 *           LED Indicator  → GPIO2  (onboard)
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ─────────────────────────────────────────
//  Configuration  (EDIT THESE)
// ─────────────────────────────────────────
const char* WIFI_SSID       = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL      = "http://192.168.1.XX:8000/energy";
// Replace 192.168.1.XX with your laptop IP.
// On Mac, find it with: ifconfig | grep 'inet '
// On Windows: ipconfig | findstr IPv4

// ─────────────────────────────────────────
//  Pin Definitions
// ─────────────────────────────────────────
#define VOLTAGE_PIN   34    // Analog – Voltage sensor signal
#define CURRENT_PIN   35    // Analog – ACS712 output
#define IR_PIN        27    // Digital – IR obstacle sensor
#define LED_PIN        2    // Onboard LED (indicator)
#define BATTERY_PIN   32    // Analog – Battery voltage divider

// ─────────────────────────────────────────
//  Sensor Calibration Constants
// ─────────────────────────────────────────
// Voltage sensor (0–25V module, 5:1 divider, 12-bit ADC on 3.3V ref)
#define ADC_RESOLUTION    4095.0
#define ADC_VREF          3.3
#define VOLTAGE_DIVIDER   5.0     // Module divides by 5

// ACS712-5A: sensitivity 185 mV/A, offset ~2.5V
#define ACS712_SENSITIVITY  0.185   // Volts per Amp (5A model)
#define ACS712_OFFSET       2.5     // Volts at zero current

// ─────────────────────────────────────────
//  State Variables
// ─────────────────────────────────────────
int   vehicleCount   = 0;
float batteryLevel   = 0.0;
bool  irLastState    = HIGH;        // Debounce tracking
unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 5000;  // Send every 5 seconds

// ─────────────────────────────────────────
//  Setup
// ─────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(IR_PIN,  INPUT);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("\n╔══════════════════════════════╗");
  Serial.println("║   RoadVolt – ESP32 Firmware  ║");
  Serial.println("╚══════════════════════════════╝");

  connectWiFi();
}

// ─────────────────────────────────────────
//  Main Loop
// ─────────────────────────────────────────
void loop() {

  // Detect vehicle (IR sensor LOW = object detected)
  bool irCurrent = digitalRead(IR_PIN);
  if (irCurrent == LOW && irLastState == HIGH) {
    vehicleCount++;
    Serial.print("🚗 Vehicle detected! Count: ");
    Serial.println(vehicleCount);
    blinkLED(2);
    delay(800);   // Debounce delay
  }
  irLastState = irCurrent;

  // Send data every SEND_INTERVAL ms
  if (millis() - lastSend >= SEND_INTERVAL) {
    float voltage = readVoltage();
    float current = readCurrent();
    float power   = voltage * current;
    batteryLevel  = readBatteryLevel();

    printReadings(voltage, current, power, batteryLevel);

    if (WiFi.status() == WL_CONNECTED) {
      sendData(voltage, current, power, vehicleCount, batteryLevel);
      vehicleCount = 0;   // Reset count after sending
    } else {
      Serial.println("⚠️  WiFi disconnected – reconnecting...");
      connectWiFi();
    }

    lastSend = millis();
  }
}

// ─────────────────────────────────────────
//  Sensor Reading Functions
// ─────────────────────────────────────────

float readVoltage() {
  // Average 20 samples for stability
  long sum = 0;
  for (int i = 0; i < 20; i++) {
    sum += analogRead(VOLTAGE_PIN);
    delay(2);
  }
  float raw  = sum / 20.0;
  float vADC = (raw / ADC_RESOLUTION) * ADC_VREF;
  float vOut = vADC * VOLTAGE_DIVIDER;   // Scale back to real voltage
  return max(0.0f, vOut);
}

float readCurrent() {
  // Average 30 samples for AC ripple rejection
  long sum = 0;
  for (int i = 0; i < 30; i++) {
    sum += analogRead(CURRENT_PIN);
    delay(1);
  }
  float raw   = sum / 30.0;
  float vSens = (raw / ADC_RESOLUTION) * ADC_VREF;
  float current = (vSens - ACS712_OFFSET) / ACS712_SENSITIVITY;
  return max(0.0f, current);
}

float readBatteryLevel() {
  // Assumes battery max 12.6V, connected through voltage divider to ADC
  // Divider: 10kΩ + 3.3kΩ → reading 0–3.3V for 0–12.9V battery
  float raw  = analogRead(BATTERY_PIN);
  float vADC = (raw / ADC_RESOLUTION) * ADC_VREF;
  float vBat = vADC * ((10.0 + 3.3) / 3.3);  // Scale by divider ratio
  float pct  = ((vBat - 9.0) / (12.6 - 9.0)) * 100.0;
  return constrain(pct, 0.0f, 100.0f);
}

// ─────────────────────────────────────────
//  Data Sending
// ─────────────────────────────────────────
void sendData(float voltage, float current, float power,
              int vehicle, float battery) {

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Build JSON using ArduinoJson
  StaticJsonDocument<256> doc;
  doc["voltage"] = round(voltage  * 100) / 100.0;
  doc["current"] = round(current  * 1000) / 1000.0;
  doc["power"]   = round(power    * 100) / 100.0;
  doc["vehicle"] = vehicle;
  doc["battery"] = round(battery  * 10) / 10.0;

  String json;
  serializeJson(doc, json);

  int code = http.POST(json);

  if (code == 200) {
    Serial.println("✅ Data sent to server");
    blinkLED(1);
  } else {
    Serial.print("❌ Server error: HTTP ");
    Serial.println(code);
  }

  http.end();
}

// ─────────────────────────────────────────
//  WiFi Connection
// ─────────────────────────────────────────
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    blinkLED(5);
  } else {
    Serial.println("\n❌ WiFi connection failed. Will retry...");
  }
}

// ─────────────────────────────────────────
//  Utility
// ─────────────────────────────────────────
void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(120);
    digitalWrite(LED_PIN, LOW);
    delay(120);
  }
}

void printReadings(float v, float c, float p, float bat) {
  Serial.println("──────────────────────────");
  Serial.print("⚡ Voltage  : "); Serial.print(v,   2); Serial.println(" V");
  Serial.print("🔌 Current  : "); Serial.print(c,   3); Serial.println(" A");
  Serial.print("💡 Power    : "); Serial.print(p,   2); Serial.println(" W");
  Serial.print("🔋 Battery  : "); Serial.print(bat, 1); Serial.println(" %");
  Serial.print("🚗 Vehicles : "); Serial.println(vehicleCount);
  Serial.println("──────────────────────────");
}
