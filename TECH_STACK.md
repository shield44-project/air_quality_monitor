# Technology Stack Documentation

## 📋 Overview
This document provides a comprehensive breakdown of all frontend and backend technologies, libraries, frameworks, and services used in the Air Quality Monitor project.

---

## 🖥️ Backend Technologies

### Core Framework
- **Flask 3.0.3**
  - Python web framework for building the web application
  - Handles routing, template rendering, and API endpoints
  - Template folder configured as flat structure (template_folder=".")
  - Used for:
    - Serving the dashboard HTML (`/` route)
    - Providing real-time sensor data API (`/data` route)

### Python Libraries

#### Data Processing & Computation
- **NumPy 2.1.1**
  - Used for mathematical calculations and random number generation
  - Implements sinusoidal patterns for realistic sensor data simulation
  - Used in `fake_serial_reader()` and `calculate_gas_levels()` functions

- **Pandas 2.2.3**
  - Listed in requirements but not actively used in current code
  - Likely for future data analysis features

- **Plotly 5.24.1**
  - Python graphing library (backend support)
  - Listed in requirements for potential server-side graph generation

#### Hardware Communication
- **PySerial 3.5**
  - Serial communication library for Arduino integration
  - Used in `app_ard.py` for real-time sensor data reading
  - Reads MQ-135 sensor values via USB serial connection
  - Marked as optional (disabled on Vercel deployment)

### Threading & Concurrency
- **Python Threading Module** (built-in)
  - Creates daemon thread for continuous sensor data simulation
  - Runs `fake_serial_reader()` in background without blocking Flask server
  - Thread-safe global data structure for sensor readings

### Environment & Configuration
- **Python OS Module** (built-in)
  - Reads PORT environment variable for flexible deployment
  - Default port: 5000, configurable via `PORT` environment variable

---

## 🎨 Frontend Technologies

### Core Web Technologies
- **HTML5**
  - Semantic markup for dashboard structure
  - Modern DOCTYPE and meta tags for responsive design
  - Single-page application (SPA) architecture

- **CSS3**
  - Custom styling with modern features:
    - Linear gradients (`linear-gradient(135deg, #667eea 0%, #764ba2 100%)`)
    - Backdrop filters (`backdrop-filter: blur(10px)`)
    - Flexbox and responsive design
    - Media queries for mobile responsiveness (max-width: 768px)
    - RGBA colors for transparency effects
    - CSS transitions and transforms for animations

- **Vanilla JavaScript (ES6+)**
  - No frameworks - pure JavaScript implementation
  - Fetch API for AJAX requests
  - Async/await pattern for data fetching
  - DOM manipulation for real-time updates
  - setInterval for 1-second polling

### Frontend Libraries

#### Data Visualization
- **Plotly.js 2.35.2** (CDN)
  - JavaScript charting library loaded from CDN
  - Creates interactive real-time line graphs
  - Displays MQ sensor value trends over time (last 15 seconds)
  - Features:
    - Scatter plot with lines and markers
    - Dynamic color changes based on AQI level
    - Custom axis labels and titles
    - Transparent background integration

### UI/UX Features
- **Responsive Design**
  - Mobile-first approach with media queries
  - Adaptive table layout (stacks on mobile devices)
  - Data-label attributes for mobile-friendly tables
  - Viewport meta tag for proper mobile rendering

- **Real-Time Updates**
  - Auto-refresh every 1 second via JavaScript setInterval
  - Fetch API calls to `/data` endpoint
  - Dynamic DOM updates without page reload
  - Live AQI color coding (green, yellow, orange, red)

---

## 🔧 Third-Party Services

### Form Handling
- **Formspree** (formspree.io/f/xvgeqywp)
  - External form submission service
  - Handles "Report Issues" form submissions
  - No backend form processing required
  - Email notifications for admin

---

## ☁️ Deployment & Hosting

### Cloud Platform
- **Vercel**
  - Serverless deployment platform
  - Configuration file: `vercel.json`
  - Python runtime: `@vercel/python`
  - Environment variables:
    - `FLASK_ENV=production`
  - Routing: All requests routed to `app.py`

### Configuration Files
- **vercel.json**
  - Vercel deployment configuration
  - Defines build settings and routes
  - Specifies Python runtime version

- **requirements.txt**
  - Python dependency management
  - Lists all required packages with versions
  - Used by Vercel for automatic dependency installation

---

## 🤖 Hardware & Embedded Systems

### Microcontroller
- **Arduino**
  - Reads analog sensor data from MQ-135
  - Serial communication at 9600 baud rate
  - Sends data in format: `MQ:VALUE`
  - Code file: `arduino_mq_sensor.ino`

### Sensors
- **MQ-135 Air Quality Sensor**
  - Analog gas sensor connected to A0 pin
  - Detects 10 different gases:
    1. CO₂ (Carbon Dioxide)
    2. CO (Carbon Monoxide)
    3. NO₂ (Nitrogen Dioxide)
    4. NH₃ (Ammonia)
    5. Benzene (C₆H₆)
    6. Toluene (C₇H₈)
    7. Alcohol (Ethanol)
    8. Acetone (C₃H₆O)
    9. H₂S (Hydrogen Sulfide)
    10. Smoke/PM2.5 particles
  - Output range: 0-1023 (10-bit ADC)

---

## 📊 Data Flow Architecture

### Data Pipeline
```
[MQ-135 Sensor] → [Arduino A0 Pin] → [Serial USB] → [Python PySerial] 
                                                           ↓
                                         [Flask Backend Processing]
                                                           ↓
                                         [JSON API Endpoint /data]
                                                           ↓
                                         [Frontend Fetch API]
                                                           ↓
                                         [Plotly.js Visualization + DOM Updates]
```

### Simulation Mode (Vercel/Demo)
```
[NumPy Random Generation] → [Sinusoidal Pattern] → [Flask Backend]
                                                           ↓
                                         [JSON API Endpoint /data]
                                                           ↓
                                         [Frontend Fetch API]
                                                           ↓
                                         [Plotly.js Visualization + DOM Updates]
```

---

## 🔄 API Endpoints

### Routes
1. **`GET /`**
   - Returns: HTML dashboard (air_quality_dashboard.html)
   - Method: Flask render_template()

2. **`GET /data`**
   - Returns: JSON sensor data
   - Structure:
     ```json
     {
       "mq_values": [array of last 15 readings],
       "latest_mq": int,
       "aqi": int,
       "aqi_level": string,
       "aqi_color": string,
       "gas_levels": {
         "co2": float,
         "co": float,
         "no2": float,
         "nh3": float,
         "benzene": float,
         "toluene": float,
         "alcohol": float,
         "acetone": float,
         "h2s": float,
         "smoke": float
       }
     }
     ```

---

## 🎯 Algorithms & Logic

### AQI Calculation
- Threshold-based mapping:
  - **Good (🟢)**: MQ < 250 → AQI = 30
  - **Moderate (🟡)**: 250 ≤ MQ < 450 → AQI = 80
  - **Unhealthy (🟠)**: 450 ≤ MQ < 650 → AQI = 130
  - **Very Unhealthy (🔴)**: MQ ≥ 650 → AQI = 220

### Gas Level Simulation
- Normalized MQ ratio (0-1 range)
- Pollution factor calculation (0.3-2.0 range)
- Time-based variations:
  - Peak traffic hours (7-9 AM, 5-7 PM): 1.3x multiplier
  - Clean air hours (12-3 PM): 0.8x multiplier
- Random noise addition for realism
- Clamping to realistic bounds for each gas type

### Data Buffer Management
- Rolling buffer of 15 seconds (last 15 MQ readings)
- Pop oldest value when buffer exceeds 15 entries
- Thread-safe updates using Python global dictionary

---

## 📦 File Structure

```
air_quality_monitor/
├── app.py                        # Main Flask application (Vercel/demo mode)
├── app_ard.py                    # Alternative Flask app with Arduino serial
├── air_quality_dashboard.html    # Frontend dashboard (HTML+CSS+JS)
├── arduino_mq_sensor.ino         # Arduino sensor code
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel deployment config
└── README.md                     # Project documentation
```

---

## 🔒 Security Considerations

### Current Implementation
- No authentication/authorization
- Public API endpoints
- Form submission handled by external service (Formspree)
- No sensitive data storage
- Client-side only validation

---

## 🚀 Development vs Production

### Development Mode (`app_ard.py`)
- Real Arduino sensor integration via PySerial
- Debug mode enabled
- Local serial port configuration required
- Hot reload enabled

### Production Mode (`app.py`)
- Simulated sensor data (no hardware required)
- Vercel serverless deployment
- Environment-based PORT configuration
- Threading for continuous data generation
- PySerial disabled/optional

---

## 📈 Performance Characteristics

### Update Frequency
- Backend: 1-second sensor reading intervals
- Frontend: 1-second polling via Fetch API
- Buffer: 15-second rolling window
- Graph refresh: Real-time with each update

### Resource Usage
- Minimal server load (single-threaded simulation)
- Lightweight frontend (no heavy frameworks)
- CDN-hosted libraries (reduced server bandwidth)
- Serverless architecture (scales automatically)

---

## 🔧 Browser Compatibility

### Required Features
- Fetch API (modern browsers)
- ES6 JavaScript (arrow functions, template literals)
- CSS3 transforms and animations
- Plotly.js browser support
- Viewport meta tag support

### Supported Browsers
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## 📝 Summary

### Backend Stack
- **Framework**: Flask 3.0.3
- **Language**: Python 3.x
- **Libraries**: NumPy, Pandas, Plotly, PySerial
- **Deployment**: Vercel (serverless)

### Frontend Stack
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **Visualization**: Plotly.js 2.35.2 (CDN)
- **Architecture**: Single-page application with AJAX polling
- **Styling**: Custom CSS with gradients and responsive design

### Integration Points
- Arduino via Serial (PySerial)
- Formspree for form handling
- Vercel for hosting
- CDN for frontend libraries

### Data Processing
- Real-time sensor simulation
- Mathematical modeling with NumPy
- Time-based environmental variations
- Rolling buffer data management
