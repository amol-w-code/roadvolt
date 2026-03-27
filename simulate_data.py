"""
RoadVolt – Data Simulator
Sends realistic fake sensor data to FastAPI so you can test the
dashboard without hardware.

Usage:  python3 simulate_data.py
"""

import requests
import random
import time
import math

SERVER_URL = "http://127.0.0.1:8000/energy"

def generate_reading(tick: int) -> dict:
    """Generates realistic sensor values with    time-varying traffic."""

    # Traffic cycle: more vehicles at certain times
    base_traffic = 0.5 + 0.5 * math.sin(tick / 10)

    # Voltage: 9–14V from generator, higher with more traffic
    voltage = round(random.gauss(10 + base_traffic * 3, 0.4), 2)
    voltage = max(0.0, min(25.0, voltage))

    # Current: 0.2–1.0A, proportional to voltage
    current = round(random.gauss(0.3 + base_traffic * 0.5, 0.05), 3)
    current = max(0.0, min(5.0, current))

    power = round(voltage * current, 3)

    # Vehicle: 0–3 per reading window, bursts during high traffic
    if base_traffic > 0.7:
        vehicle = random.choices([0, 1, 2, 3], weights=[10, 40, 30, 20])[0]
    else:
        vehicle = random.choices([0, 1, 2, 3], weights=[50, 35, 10, 5])[0]

    # Battery: slowly charges (capped at 95%)
    battery = round(40 + (tick % 300) * 0.18, 1)
    battery = min(95.0, battery)

    return {
        "voltage": voltage,
        "current": current,
        "power":   power,
        "vehicle": vehicle,
        "battery": battery
    }


def main():
    print("╔══════════════════════════════════════╗")
    print("║  RoadVolt – Sensor Data Simulator    ║")
    print("╚══════════════════════════════════════╝")
    print(f"Sending to: {SERVER_URL}")
    print("Press Ctrl+C to stop.\n")

    tick = 0
    total_vehicles = 0
    total_energy   = 0.0

    while True:
        try:
            data = generate_reading(tick)
            resp = requests.post(SERVER_URL, json=data, timeout=5)

            if resp.status_code == 200:
                total_vehicles += data["vehicle"]
                total_energy   += data["power"]
                print(
                    f"[{tick:04d}] V={data['voltage']:5.2f}V  "
                    f"I={data['current']:5.3f}A  "
                    f"P={data['power']:6.3f}W  "
                    f"Veh={data['vehicle']}  "
                    f"Bat={data['battery']}%  "
                    f"→ ✅ stored"
                )
            else:
                print(f"[{tick:04d}] Server returned HTTP {resp.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"[{tick:04d}] ❌ Cannot reach server at {SERVER_URL}")
            print("       Make sure FastAPI is running:  uvicorn server:app --reload")

        tick += 1
        time.sleep(3)   # Send a reading every 3 seconds


if __name__ == "__main__":
    main()
