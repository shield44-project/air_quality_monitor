from flask import Flask, render_template, jsonify
import threading
import time
import os
import numpy as np
from datetime import datetime

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
    """Simulate Arduino data for RVCE Bengaluru Campus with realistic time-based patterns"""
    global fake_counter
    while True:
        fake_counter += 1
        
        # Get current time (IST - Indian Standard Time, UTC+5:30)
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        # RVCE Bengaluru Campus realistic patterns:
        # - Early morning (5-7): Very clean air (Good)
        # - Morning classes (8-11): Slight increase due to traffic (Good to Moderate)
        # - Lunch time (12-14): Keep Good-Moderate as requested
        # - Afternoon (15-18): Moderate activity
        # - Dinner time (19-21): Keep Good-Moderate as requested
        # - Night (22-4): Very clean air
        
        # Determine base MQ value based on time of day
        if 5 <= hour < 7:  # Early morning - very clean
            base_mq = 180
            variation = 40
        elif 7 <= hour < 8:  # Morning rush hour starts
            base_mq = 240
            variation = 50
        elif 8 <= hour < 12:  # Morning classes
            base_mq = 280
            variation = 60
        elif 12 <= hour < 14:  # LUNCH TIME - Keep Good to Moderate (250-400)
            base_mq = 300
            variation = 50  # Reduced variation to keep stable
        elif 14 <= hour < 17:  # Afternoon
            base_mq = 320
            variation = 70
        elif 17 <= hour < 19:  # Evening rush hour
            base_mq = 360
            variation = 60
        elif 19 <= hour < 21:  # DINNER TIME - Keep Good to Moderate (250-400)
            base_mq = 320
            variation = 45  # Reduced variation to keep stable
        elif 21 <= hour < 23:  # Late evening
            base_mq = 250
            variation = 50
        else:  # Night (23-5)
            base_mq = 160
            variation = 30
        
        # Add smooth oscillation for realistic variation (slower cycle)
        smooth_wave = int(variation * 0.6 * np.sin(fake_counter * 0.05))
        
        # Add random noise (smaller for stability during meal times)
        is_meal_time = (12 <= hour < 14) or (19 <= hour < 21)
        noise_range = 20 if is_meal_time else 40
        noise = np.random.randint(-noise_range, noise_range)
        
        # Calculate final value
        value = base_mq + smooth_wave + noise
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
