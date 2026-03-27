from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────
#  App Setup
# ─────────────────────────────────────────
app = FastAPI(
    title="RoadVolt API",
    description="Smart Speed Breaker Energy Harvesting System – Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  Database Setup
# ─────────────────────────────────────────
conn = sqlite3.connect("energy.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS energy_data (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    voltage   REAL    NOT NULL,
    current   REAL    NOT NULL,
    power     REAL    NOT NULL,
    vehicle   INTEGER NOT NULL DEFAULT 0,
    battery   REAL    DEFAULT 0,
    timestamp TEXT    DEFAULT (datetime('now','localtime'))
)
""")
conn.commit()

# ─────────────────────────────────────────
#  Request Schema
# ─────────────────────────────────────────
class EnergyData(BaseModel):
    voltage: float
    current: float
    power: float
    vehicle: int = 0
    battery: Optional[float] = 0.0

# ─────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────

@app.get("/")
def home():
    return {
        "project": "RoadVolt – Smart Speed Breaker Energy Harvesting System",
        "status": "Backend Running ✅",
        "version": "1.0.0",
        "endpoints": ["/energy", "/energy/latest", "/energy/stats", "/traffic", "/docs"]
    }


@app.post("/energy")
def receive_data(data: EnergyData):
    """Receives sensor data from ESP32 and stores it in the database."""
    cursor.execute(
        "INSERT INTO energy_data (voltage, current, power, vehicle, battery) VALUES (?,?,?,?,?)",
        (data.voltage, data.current, data.power, data.vehicle, data.battery)
    )
    conn.commit()
    return {
        "status": "success",
        "message": "Data stored successfully",
        "received": {
            "voltage": data.voltage,
            "current": data.current,
            "power": data.power,
            "vehicle": data.vehicle,
            "battery": data.battery,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@app.get("/energy")
def get_all_data(limit: int = 100):
    """Returns all stored energy readings (latest first)."""
    rows = cursor.execute(
        "SELECT * FROM energy_data ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    cols = ["id", "voltage", "current", "power", "vehicle", "battery", "timestamp"]
    return [dict(zip(cols, row)) for row in rows]


@app.get("/energy/latest")
def get_latest():
    """Returns the most recent single reading."""
    row = cursor.execute(
        "SELECT * FROM energy_data ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No data found")
    cols = ["id", "voltage", "current", "power", "vehicle", "battery", "timestamp"]
    return dict(zip(cols, row))


@app.get("/energy/stats")
def get_stats():
    """Returns aggregated statistics for the dashboard."""
    row = cursor.execute("""
        SELECT
            COUNT(*)            AS total_readings,
            SUM(vehicle)        AS total_vehicles,
            SUM(power)          AS total_energy_wh,
            AVG(voltage)        AS avg_voltage,
            AVG(current)        AS avg_current,
            AVG(power)          AS avg_power,
            MAX(power)          AS peak_power,
            MAX(vehicle)        AS peak_vehicle_reading,
            MIN(timestamp)      AS first_reading,
            MAX(timestamp)      AS last_reading
        FROM energy_data
    """).fetchone()
    cols = [
        "total_readings", "total_vehicles", "total_energy_wh",
        "avg_voltage", "avg_current", "avg_power",
        "peak_power", "peak_vehicle_reading",
        "first_reading", "last_reading"
    ]
    stats = dict(zip(cols, row))

    # Energy per vehicle
    if stats["total_vehicles"] and stats["total_vehicles"] > 0:
        stats["energy_per_vehicle"] = round(
            (stats["total_energy_wh"] or 0) / stats["total_vehicles"], 4
        )
    else:
        stats["energy_per_vehicle"] = 0

    # Efficiency score (0–100)
    if stats["avg_power"] and stats["peak_power"] and stats["peak_power"] > 0:
        stats["efficiency_score"] = round(
            (stats["avg_power"] / stats["peak_power"]) * 100, 1
        )
    else:
        stats["efficiency_score"] = 0

    return stats


@app.get("/traffic")
def get_traffic():
    """Returns hourly traffic breakdown."""
    rows = cursor.execute("""
        SELECT
            strftime('%H:00', timestamp) AS hour,
            SUM(vehicle)                 AS vehicles,
            AVG(power)                   AS avg_power
        FROM energy_data
        GROUP BY strftime('%H', timestamp)
        ORDER BY hour
    """).fetchall()
    return [{"hour": r[0], "vehicles": r[1], "avg_power": round(r[2] or 0, 2)} for r in rows]


@app.delete("/energy/reset")
def reset_data():
    """Clears all data (use only for testing)."""
    cursor.execute("DELETE FROM energy_data")
    conn.commit()
    return {"status": "success", "message": "All data cleared"}
