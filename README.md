# 🌆 Pollution Absorbing Streetlight - Flat Flask Project

## 🚀 Quick Start Guide

### Option 1: Real Arduino Data (USB Connection)
**Use `app_usb.py` for real MQ-135 sensor readings:**

1. **Hardware Setup:**
   - Connect MQ-135 sensor to Arduino analog pin A0
   - Upload `arduino_mq_sensor.ino` to your Arduino
   - Connect Arduino to your computer via USB

2. **Run the App:**
   ```bash
   python app_usb.py
   ```
   - Auto-detects Arduino port (Windows/Linux/Mac)
   - If detection fails, edit line 23: `SERIAL_PORT = 'COM3'` (or `/dev/ttyUSB0`)

3. **Open Dashboard:**
   - Visit: http://localhost:5000
   - Real-time data updates every second

### Option 2: Demo Mode (Simulated Data)
**Use `app.py` for realistic fake data (no Arduino needed):**

1. **Run the App:**
   ```bash
   python app.py
   ```
   - Simulates realistic pollution patterns
   - Time-based variations (rush hours, clean periods)
   - Random events (spikes, gradual changes)

2. **Open Dashboard:**
   - Visit: http://localhost:5000
   - Perfect for demos and testing

## ✨ Features
- **Real-time graph** (Plotly) - Last 15 seconds of data
- **AQI levels** with color-coded status (Good 🟢, Moderate 🟡, Unhealthy 🟠, Very Unhealthy 🔴)
- **10 Gas measurements** - CO₂, CO, NO₂, NH₃, Benzene, Toluene, Alcohol, Acetone, H₂S, Smoke/PM2.5
- **Gas harm table** with health risks and streetlight solutions
- **Mobile responsive** design
- **Formspree feedback** form (ID: xvgeqywp)

## 🔧 Serial Port Detection

### Finding Your Arduino Port:
- **Windows:** Device Manager → Ports (COM & LPT) → COM?
- **Linux:** `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
- **Mac:** `ls /dev/cu.*`

### Troubleshooting:
- Close Arduino IDE Serial Monitor before running the app
- Check USB cable connection
- Linux users: Add user to `dialout` group: `sudo usermod -a -G dialout $USER`
- Verify Arduino is running `arduino_mq_sensor.ino`

## 📁 File Structure
- `app.py` - Demo mode with realistic simulated data
- `app_usb.py` - Real Arduino USB data mode (⭐ NEW)
- `app_ard.py` - Legacy Arduino reader (use app_usb.py instead)
- `arduino_mq_sensor.ino` - Arduino sketch for MQ-135 sensor
- `air_quality_dashboard.html` - Web dashboard UI
- `requirements.txt` - Python dependencies
