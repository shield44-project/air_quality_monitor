from flask import Flask, render_template, jsonify
import threading
import time
import os
import numpy as np

# Vercel: FLAT templates + Serverless
app = Flask(__name__, template_folder=".")

# Global data (thread-safe)
sensor_data = {
    "mq_values": [],
    "latest_mq": 0,
    "aqi": 0,
    "aqi_level": "Good",
    "aqi_color": "green"
}

# FAKE DATA MODE (Vercel + Local demo)
fake_counter = 0

def fake_serial_reader():
    """Simulate Arduino data (oscillating pollution levels)"""
    global fake_counter
    while True:
        fake_counter += 1
        # Realistic simulation: 200-700 MQ values + noise
        value = 350 + int(250 * np.sin(fake_counter * 0.08)) + np.random.randint(-80, 80)
        value = max(0, min(1023, value))  # Clamp 0-1023
        update_data(value)
        time.sleep(1)

def update_data(raw_mq):
    sensor_data["latest_mq"] = raw_mq
    sensor_data["mq_values"].append(raw_mq)
    if len(sensor_data["mq_values"]) > 60:
        sensor_data["mq_values"].pop(0)
    
    # AQI (thresholds)
    if raw_mq < 250: aqi, level, color = 30, "Good 🟢", "green"
    elif raw_mq < 450: aqi, level, color = 80, "Moderate 🟡", "yellow"
    elif raw_mq < 650: aqi, level, color = 130, "Unhealthy 🟠", "orange"
    else: aqi, level, color = 220, "Very Unhealthy 🔴", "red"
    
    sensor_data["aqi"] = aqi
    sensor_data["aqi_level"] = level
    sensor_data["aqi_color"] = color

# Start fake data thread
threading.Thread(target=fake_serial_reader, daemon=True).start()

@app.route("/")
def dashboard():
    return render_template("air_quality_dashboard.html")

@app.route("/data")
def get_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
