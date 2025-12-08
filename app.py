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
    """Simulate Arduino data with realistic pollution patterns"""
    global fake_counter, current_base, target_base, last_event_time
    
    while True:
        fake_counter += 1
        current_time = time.time()
        hour = time.localtime().tm_hour
        
        # 1. Time-based baseline (daily patterns)
        time_baseline = 300  # Base clean air
        if 7 <= hour <= 9:  # Morning rush hour
            time_baseline = 450
        elif 12 <= hour <= 14:  # Lunch time (moderate)
            time_baseline = 380
        elif 17 <= hour <= 19:  # Evening rush hour
            time_baseline = 500
        elif 22 <= hour or hour <= 5:  # Night time (clean)
            time_baseline = 250
        else:  # Rest of day
            time_baseline = 350
        
        # 2. Random events (pollution spikes/dips every 20-60 seconds)
        if current_time - last_event_time > np.random.uniform(20, 60):
            event_type = np.random.choice(['spike', 'dip', 'gradual_increase', 'gradual_decrease', 'none'], 
                                         p=[0.15, 0.10, 0.15, 0.15, 0.45])
            
            if event_type == 'spike':  # Sudden pollution (e.g., vehicle passing)
                target_base = min(700, time_baseline + np.random.randint(100, 250))
            elif event_type == 'dip':  # Sudden clean air (e.g., wind gust)
                target_base = max(200, time_baseline - np.random.randint(80, 150))
            elif event_type == 'gradual_increase':
                target_base = min(650, time_baseline + np.random.randint(50, 150))
            elif event_type == 'gradual_decrease':
                target_base = max(250, time_baseline - np.random.randint(50, 120))
            else:  # Return to time-based normal
                target_base = time_baseline
            
            last_event_time = current_time
        
        # 3. Smooth transition to target (realistic gradual change)
        transition_speed = 0.05  # Slower = more realistic
        if abs(current_base - target_base) > 1:
            current_base += (target_base - current_base) * transition_speed
        else:
            current_base = target_base
        
        # 4. Natural oscillation (breathing pattern)
        oscillation = 30 * np.sin(fake_counter * 0.05)
        
        # 5. Small random noise (sensor fluctuation)
        noise = np.random.uniform(-15, 15)
        
        # 6. Occasional micro-spikes (realistic sensor behavior)
        if np.random.random() < 0.05:  # 5% chance
            noise += np.random.uniform(20, 50)
        
        # Final value calculation
        value = int(current_base + oscillation + noise)
        value = max(0, min(MAX_ANALOG_VALUE, value))  # Clamp to valid sensor range
        
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
    # Reduced buffer from 60 to 15 seconds for more real-time AQI
    if len(sensor_data["mq_values"]) > 15:
        sensor_data["mq_values"].pop(0)
    
    # Calculate individual gas levels
    sensor_data["gas_levels"] = calculate_gas_levels(raw_mq)
    
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
