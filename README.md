# RoadVolt – Smart Speed Breaker Energy Harvesting System

> **Hackathon 2026 Project** | IoT + AI + Smart City Dashboard

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `server.py` | FastAPI backend — receives ESP32 data, stores to SQLite |
| `dashboard.py` | Streamlit smart dashboard — live metrics, gauges, AI prediction |
| `esp32_code.ino` | Arduino/ESP32 firmware — reads sensors, sends data via WiFi |
| `simulate_data.py` | Testing tool — sends fake data so dashboard works without hardware |
| `requirements.txt` | Python dependencies |

---

## ⚡ Quick Start (Software)

### Step 1 — Install dependencies
```bash
pip3 install -r requirements.txt
```

### Step 2 — Start the backend server
```bash
uvicorn server:app --reload
```
Backend runs at → http://127.0.0.1:8000  
API docs at → http://127.0.0.1:8000/docs

### Step 3 — Start the dashboard (new terminal)
```bash
python3 -m streamlit run dashboard.py
```
Dashboard runs at → http://localhost:8501

### Step 4 — (Optional) Simulate data without hardware
```bash
python3 simulate_data.py
```

---

## 🔧 ESP32 Setup

1. Open `esp32_code.ino` in Arduino IDE
2. Edit these lines with your details:
   ```cpp
   const char* WIFI_SSID     = "YOUR_WIFI_NAME";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* SERVER_URL    = "http://YOUR_LAPTOP_IP:8000/energy";
   ```
3. Find your laptop IP:
   - **Mac**: `ifconfig | grep 'inet '`
   - **Windows**: `ipconfig | findstr IPv4`
4. Install Arduino libraries: **WiFi**, **HTTPClient**, **ArduinoJson**
5. Select: Tools → Board → ESP32 Dev Module
6. Upload!

---

## 🔌 Hardware Wiring

| Sensor | ESP32 Pin |
|--------|-----------|
| Voltage Sensor (0–25V module) | GPIO 34 |
| ACS712 Current Sensor | GPIO 35 |
| IR Obstacle Sensor | GPIO 27 |
| Battery Voltage Divider | GPIO 32 |
| LED Indicator | GPIO 2 (onboard) |

---

## 🌍 SDG Alignment

- **SDG 7** — Affordable and Clean Energy
- **SDG 9** — Industry, Innovation and Infrastructure
- **SDG 11** — Sustainable Cities and Communities
- **SDG 13** — Climate Action

---

## 🗂️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/energy` | Receive ESP32 data |
| GET | `/energy` | Get all readings |
| GET | `/energy/latest` | Get most recent reading |
| GET | `/energy/stats` | Aggregated statistics |
| GET | `/traffic` | Hourly traffic breakdown |
| DELETE | `/energy/reset` | Clear all data (testing only) |
