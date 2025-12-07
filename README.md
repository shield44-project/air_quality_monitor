# 🌆 Pollution Absorbing Streetlight - Flat Flask Project

## 📚 Technology Stack
For a comprehensive breakdown of all frontend and backend technologies used in this project, see **[TECH_STACK.md](TECH_STACK.md)**.

**Quick Overview:**
- **Backend:** Flask 3.0.3, Python 3.x, NumPy, Pandas, PySerial
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Plotly.js 2.35.2
- **Hardware:** Arduino + MQ-135 Air Quality Sensor
- **Deployment:** Vercel (Serverless)
- **Services:** Formspree (Form handling)

## Quick Start
1. Connect Arduino + MQ sensor (A0 pin).
2. Edit `app.py`: SERIAL_PORT = 'YOUR_PORT' (e.g., 'COM3')
3. Run: `python app.py`
4. Open: http://localhost:5000

## Features
- Real-time graph (Plotly)
- AQI levels + colors
- Gas harm table + fixes
- Formspree feedback (your ID: xvgeqywp)

## Ports
- Windows: Device Manager → COM?
- Linux: `ls /dev/ttyUSB*`
- Mac: `ls /dev/cu.*`
