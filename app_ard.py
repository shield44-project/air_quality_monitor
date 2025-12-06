from flask import Flask, render_template, jsonify
import serial
import threading
import time
import platform
import numpy as np

# Flask with FLAT template folder (no 'templates/' needed!)
app = Flask(__name__, template_folder=".")

# Global data storage (real-time)
sensor_data = {
    "mq_values": [],     # Historical MQ readings (last 60)
    "latest_mq": 0,      # Current MQ value
    "aqi": 0,            # Current AQI
    "aqi_level": "Good", # AQI category
    "aqi_color": "green" # Color for display
}

# Serial port (CHANGE THIS TO YOUR ARDUINO PORT!)
# Windows: 'COM3' | Linux: '/dev/ttyUSB0' | Mac: '/dev/cu.usbserial*'
SERIAL_PORT = 'COM3'  # <-- EDIT THIS LINE!
ser = None

def connect_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
        print(f"✅ Connected to Arduino on {SERIAL_PORT}")
    except Exception as e:
        print(f"⚠️ Serial error: {e}. Run without Arduino for FAKE DATA demo.")

def read_serial():
    """Background thread: Read Arduino MQ data continuously"""
    connect_serial()
    fake_counter = 0  # For FAKE DATA testing
    
    while True:
        try:
            if ser and ser.in_waiting > 0:
                line = ser.readline().decode().strip()
                if line.startswith("MQ:"):
                    value = int(line.split(":")[1])
                    update_data(value)
            else:
                # FAKE DATA (uncomment next 3 lines for demo without Arduino)
                # fake_counter += 1
                # value = 300 + int(200 * np.sin(fake_counter * 0.1)) + np.random.randint(-50, 50)
                # update_data(value)
                pass
        except:
            pass
        time.sleep(0.1)

def update_data(raw_mq):
    """Update data + calculate AQI (MQ-135 calibration example)"""
    global sensor_data
    sensor_data["latest_mq"] = raw_mq
    sensor_data["mq_values"].append(raw_mq)
    if len(sensor_data["mq_values"]) > 60:  # Keep last 60 readings (1 min)
        sensor_data["mq_values"].pop(0)
    
    # AQI Calculation (customize thresholds for your MQ sensor)
    if raw_mq < 200:
        aqi, level, color = 25, "Good 🟢", "green"
    elif raw_mq < 400:
        aqi, level, color = 75, "Moderate 🟡", "yellow"
    elif raw_mq < 600:
        aqi, level, color = 125, "Unhealthy (Sensitive) 🟠", "orange"
    else:
        aqi, level, color = 200, "Unhealthy 🔴", "red"
    
    sensor_data["aqi"] = aqi
    sensor_data["aqi_level"] = level
    sensor_data["aqi_color"] = color

# Start serial reading in background
threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def dashboard():
    return render_template("air_quality_dashboard.html")

@app.route("/data")
def get_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    print("🌆 Starting Pollution Absorbing Streetlight Dashboard...")
    print(f"📱 Open: http://localhost:5000")
    print(f"🔧 Edit SERIAL_PORT='{SERIAL_PORT}' in app.py for your Arduino")
    app.run(host="0.0.0.0", port=5000, debug=True)
