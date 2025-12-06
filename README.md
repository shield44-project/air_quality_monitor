# 🌆 Pollution Absorbing Streetlight - Flat Flask Project

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

Fake data auto-enabled if no Arduino.
