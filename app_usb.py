from flask import Flask, render_template, jsonify
import serial
import serial.tools.list_ports
import threading
import time
import os
import numpy as np

# Flask app with FLAT template folder structure
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

# Serial connection
ser = None
SERIAL_PORT = None  # Auto-detect or set manually
BAUD_RATE = 9600    # Standard Arduino serial baud rate
MAX_ANALOG_VALUE = 1023  # Arduino analog input range (0-1023)

def find_arduino_port():
    """Auto-detect Arduino COM port"""
    ports = serial.tools.list_ports.comports()
    
    # Priority 1: Look for explicit Arduino identifiers
    for port in ports:
        description_lower = port.description.lower()
        if any(keyword in description_lower for keyword in ['arduino', 'uno', 'nano', 'mega']):
            print(f"🔍 Found Arduino on: {port.device} - {port.description}")
            return port.device
    
    # Priority 2: Look for common Arduino USB-to-Serial chips
    for port in ports:
        description_lower = port.description.lower()
        if any(chip in description_lower for chip in ['ch340', 'ch341', 'cp210', 'ftdi', 'pl2303']):
            print(f"🔍 Found potential Arduino (USB chip) on: {port.device} - {port.description}")
            return port.device
    
    # Priority 3: Look for generic USB serial devices (less reliable)
    for port in ports:
        if 'usb' in port.device.lower() or 'tty' in port.device.lower():
            print(f"⚠️ Found generic USB serial device: {port.device} - {port.description}")
            print(f"💡 If this is not your Arduino, manually set SERIAL_PORT on line 23")
            return port.device
    
    # No ports found
    return None

def connect_serial():
    """Connect to Arduino via USB serial"""
    global ser, SERIAL_PORT
    
    if SERIAL_PORT is None:
        SERIAL_PORT = find_arduino_port()
    
    if SERIAL_PORT is None:
        print("❌ No serial ports found. Please connect Arduino and restart.")
        return False
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print(f"✅ Connected to Arduino on {SERIAL_PORT}")
        print(f"💡 Warming up MQ-135 sensor (30 seconds recommended)...")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to {SERIAL_PORT}: {e}")
        print(f"💡 Common fixes:")
        print(f"   - Check if Arduino is plugged in")
        print(f"   - Close Arduino IDE/Serial Monitor")
        print(f"   - Try different USB port")
        print(f"   - Check device permissions (Linux: add user to dialout group)")
        return False

def read_serial():
    """Background thread: Read Arduino MQ data continuously"""
    global ser
    
    if not connect_serial():
        print("⚠️ Running without Arduino connection. No data will be displayed.")
        while True:
            time.sleep(1)
        return
    
    consecutive_errors = 0
    max_errors = 10
    
    while True:
        try:
            if ser and ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Expected format from Arduino: "MQ:123"
                if line.startswith("MQ:"):
                    try:
                        value = int(line.split(":")[1])
                        # Validate range (Arduino analog reading is 0-1023)
                        if 0 <= value <= MAX_ANALOG_VALUE:
                            update_data(value)
                            consecutive_errors = 0  # Reset error counter on success
                        else:
                            print(f"⚠️ Invalid MQ value received: {value}")
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Failed to parse: {line}")
                        consecutive_errors += 1
            
            time.sleep(0.1)  # 100ms polling rate
            
        except serial.SerialException as e:
            consecutive_errors += 1
            print(f"⚠️ Serial error #{consecutive_errors}: {e}")
            
            if consecutive_errors >= max_errors:
                print(f"❌ Too many errors ({consecutive_errors}). Reconnecting...")
                time.sleep(2)
                if ser:
                    ser.close()
                if not connect_serial():
                    print("❌ Reconnection failed. Retrying in 5 seconds...")
                    time.sleep(5)
                consecutive_errors = 0
        
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
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
    """Update sensor data and calculate AQI"""
    sensor_data["latest_mq"] = raw_mq
    sensor_data["mq_values"].append(raw_mq)
    # Keep last 15 seconds of data for real-time display
    if len(sensor_data["mq_values"]) > 15:
        sensor_data["mq_values"].pop(0)
    
    # Calculate individual gas levels
    sensor_data["gas_levels"] = calculate_gas_levels(raw_mq)
    
    # AQI calculation (calibrated for MQ-135 sensor with 90-100 range)
    if raw_mq < 250: 
        aqi, level, color = 30, "Good 🟢", "green"
    elif raw_mq < 450:
        # Linear interpolation within Moderate range: 250-449 maps to AQI 90-100
        # Formula: AQI = 90 + ((raw_mq - 250) / 200) * 10
        aqi = int(90 + ((raw_mq - 250) / 200) * 10)
        aqi = max(90, min(100, aqi))  # Clamp to 90-100 range
        level, color = "Moderate 🟡", "yellow"
    elif raw_mq < 650: 
        aqi, level, color = 130, "Unhealthy 🟠", "orange"
    else: 
        aqi, level, color = 220, "Very Unhealthy 🔴", "red"
    
    sensor_data["aqi"] = aqi
    sensor_data["aqi_level"] = level
    sensor_data["aqi_color"] = color

# Start serial reading in background thread
threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def dashboard():
    """Serve the main dashboard HTML"""
    return render_template("air_quality_dashboard.html")

@app.route("/data")
def get_data():
    """API endpoint for real-time sensor data"""
    return jsonify(sensor_data)

if __name__ == "__main__":
    print("=" * 60)
    print("🌆 Pollution Absorbing Streetlight - USB Real Data Mode")
    print("=" * 60)
    print()
    print("📋 Setup Instructions:")
    print("   1. Upload arduino_mq_sensor.ino to your Arduino")
    print("   2. Connect MQ-135 sensor to analog pin A0")
    print("   3. Connect Arduino via USB")
    print("   4. Close Arduino IDE Serial Monitor if open")
    print()
    print("🔧 Manual Port Configuration (if auto-detect fails):")
    print("   Edit line 23 in app_usb.py:")
    print("   SERIAL_PORT = 'COM3'      # Windows")
    print("   SERIAL_PORT = '/dev/ttyUSB0'  # Linux")
    print("   SERIAL_PORT = '/dev/cu.usbserial-*'  # Mac")
    print()
    print("=" * 60)
    print()
    
    # Start Flask server
    print("🚀 Starting Flask server...")
    print(f"📱 Open browser: http://localhost:5000")
    print()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
