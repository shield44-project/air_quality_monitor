from flask import Flask, render_template, jsonify
import threading
import time
import os
import numpy as np

# Vercel: FLAT templates + Serverless
app = Flask(__name__, template_folder=".")

# Global data (GIL-protected for single-threaded read/write pattern)
sensor_data = {
    "mq_values": [],
    "latest_mq": 0,
    "aqi": 0,
    "aqi_level": "Good",
    "aqi_color": "green",
    "gas_levels": {}
}

# FAKE DATA MODE (Vercel + Local demo)
fake_counter = 0
current_base = 350  # Starting baseline
target_base = 350   # Target baseline for smooth transitions
last_event_time = time.time()
MAX_ANALOG_VALUE = 1023  # Arduino analog input range (0-1023)

def fake_serial_reader():
    """Simulate Arduino data with constant AQI between 80-85"""
    global fake_counter, current_base, target_base, last_event_time
    
    while True:
        fake_counter += 1
        
        # Keep constant value in the range that produces AQI 80-85
        # Raw MQ value of 350 produces AQI ~82.5 (middle of desired range)
        # Range: 250 (AQI 80) to 450 (AQI 85)
        constant_value = 350
        
        # Variation (±80) to show AQI changes within full 80-85 range
        minimal_noise = np.random.uniform(-80, 80)
        
        # Final value calculation
        value = int(constant_value + minimal_noise)
        value = max(250, min(450, value))  # Clamp to keep within 80-85 AQI range (inclusive)
        
        update_data(value)
        time.sleep(1)

def calculate_gas_levels(raw_mq):
    """Calculate individual gas concentrations based on MQ-135 sensor reading.
    Simulates realistic urban campus environment values."""
    # Normalize MQ reading to 0-1 range for calculation
    mq_ratio = raw_mq / MAX_ANALOG_VALUE
    
    # Base pollution factor (campus environment: moderate baseline with variations)
    pollution_factor = max(0.3, min(2.0, mq_ratio * 2.5))
    
    # Add time-based variations (morning/evening traffic, afternoon clean air)
    hour = time.localtime().tm_hour
    time_factor = 1.0
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak traffic hours
        time_factor = 1.3
    elif 12 <= hour <= 15:  # Afternoon - cleaner air
        time_factor = 0.8
    
    # Calculate individual gas concentrations with realistic ranges
    gas_levels = {
        "co2": round(400 + (mq_ratio * 200 * time_factor) + np.random.uniform(-20, 20), 1),  # 400-650 ppm
        "co": round(0.1 + (mq_ratio * 5 * time_factor) + np.random.uniform(-0.5, 0.5), 2),  # 0.1-5 ppm
        "no2": round(0.02 + (mq_ratio * 0.15 * time_factor) + np.random.uniform(-0.01, 0.01), 3),  # 0.02-0.2 ppm
        "nh3": round(0.01 + (mq_ratio * 2 * pollution_factor) + np.random.uniform(-0.2, 0.2), 2),  # 0.01-2 ppm
        "benzene": round(0.005 + (mq_ratio * 0.05 * pollution_factor) + np.random.uniform(-0.005, 0.005), 3),  # 0.005-0.06 ppm
        "toluene": round(0.01 + (mq_ratio * 0.08 * pollution_factor) + np.random.uniform(-0.01, 0.01), 3),  # 0.01-0.09 ppm
        "alcohol": round(mq_ratio * 3 * pollution_factor + np.random.uniform(-0.3, 0.3), 2),  # 0-3 ppm
        "acetone": round(0.02 + (mq_ratio * 0.15 * pollution_factor) + np.random.uniform(-0.02, 0.02), 3),  # 0.02-0.17 ppm
        "h2s": round(mq_ratio * 0.5 * pollution_factor + np.random.uniform(-0.05, 0.05), 3),  # 0-0.5 ppm
        "smoke": round(12 + (mq_ratio * 35 * time_factor) + np.random.uniform(-3, 3), 1)  # 12-50 μg/m³
    }
    
    # Ensure values stay within realistic bounds
    gas_levels["co2"] = max(400, min(700, gas_levels["co2"]))
    gas_levels["co"] = max(0.1, min(8, gas_levels["co"]))
    gas_levels["no2"] = max(0.02, min(0.25, gas_levels["no2"]))
    gas_levels["nh3"] = max(0.01, min(3, gas_levels["nh3"]))
    gas_levels["benzene"] = max(0.005, min(0.08, gas_levels["benzene"]))
    gas_levels["toluene"] = max(0.01, min(0.12, gas_levels["toluene"]))
    gas_levels["alcohol"] = max(0, min(4, gas_levels["alcohol"]))
    gas_levels["acetone"] = max(0.02, min(0.2, gas_levels["acetone"]))
    gas_levels["h2s"] = max(0, min(0.6, gas_levels["h2s"]))
    gas_levels["smoke"] = max(10, min(60, gas_levels["smoke"]))
    
    return gas_levels

def update_data(raw_mq):
    sensor_data["latest_mq"] = raw_mq
    sensor_data["mq_values"].append(raw_mq)
    # Minimal buffer of 5 seconds for stable constant readings
    if len(sensor_data["mq_values"]) > 5:
        sensor_data["mq_values"].pop(0)
    
    # Calculate individual gas levels
    sensor_data["gas_levels"] = calculate_gas_levels(raw_mq)
    
    # AQI (thresholds with granular calculation for 80-85 range)
    if raw_mq < 250: 
        aqi, level, color = 30, "Good 🟢", "green"
    elif raw_mq < 450:
        # Linear interpolation within Moderate range: 250-450 maps to AQI 80-85
        # Formula: AQI = 80 + ((raw_mq - 250) / (450 - 250)) * 5
        aqi = int(80 + ((raw_mq - 250) / 200) * 5)
        aqi = max(80, min(85, aqi))  # Clamp to 80-85 range
        level, color = "Moderate 🟡", "yellow"
    elif raw_mq < 650: 
        aqi, level, color = 130, "Unhealthy 🟠", "orange"
    else: 
        aqi, level, color = 220, "Very Unhealthy 🔴", "red"
    
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
