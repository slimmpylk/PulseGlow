# PulseLEDGlow: Heart Rate LED Controller

PulseLEDGlow is a project that integrates a Raspberry Pi, any heart rate monitor, and an SPI-controlled LED strip. The LEDs change colors dynamically based on heart rate zones, providing a visual representation of your heart rate intensity.

## Features

- Real-time heart rate monitoring via the Polar H10 (not sponsored).
- Dynamic LED lighting based on heart rate zones:
  - **Zone 1** (Very Light): 50-60% of HRmax - *Pink*
  - **Zone 2** (Light): 60-70% of HRmax - *Blue*
  - **Zone 3** (Moderate): 70-80% of HRmax - *Green*
  - **Zone 4** (Hard): 80-90% of HRmax - *Yellow*
  - **Zone 5** (Maximum): 90-100% of HRmax - *Red*
- Configurable heart rate zones via a mobile app.
- Uses `bleak` for Bluetooth communication and `neopixel_spi` for LED control.

---

## Project Components

### Hardware
- **Raspberry Pi** (with SPI enabled)
- **Polar H10 Heart Rate Monitor**
- **SPI-controlled LED strip**
- Power supply for the LED strip (if required)

### Software
- **Python 3.11+**
- Libraries:
  - `bleak`: Bluetooth communication
  - `neopixel_spi`: SPI control for LEDs
  - `flask`: Backend server for communication with the mobile app

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/PulseLEDGlow.git
   cd PulseLEDGlow
   ```

2. **Set Up the Environment:**
   - Create a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Enable SPI on the Raspberry Pi:**
   ```bash
   sudo raspi-config
   ```
   - Navigate to **Interface Options > SPI** and enable it.
   - Reboot the Raspberry Pi.

4. **Verify SPI Configuration:**
   ```bash
   ls /dev/spi*
   ```
   Ensure you see `/dev/spidev0.0` and `/dev/spidev0.1`.

---

## Configuration

### Zones Configuration
Heart rate zones are dynamically sent from the app and saved in `zones.json`. Example format:
```json
{
  "zones": [
    {"zone": 1, "range": "50-60 bpm", "intensity": "Very light"},
    {"zone": 2, "range": "60-70 bpm", "intensity": "Light"},
    {"zone": 3, "range": "70-80 bpm", "intensity": "Moderate"},
    {"zone": 4, "range": "80-90 bpm", "intensity": "Hard"},
    {"zone": 5, "range": "90-100 bpm", "intensity": "Maximum"}
  ]
}
```


## Usage

### 1. Start the Server
Run the Flask server to handle communication with the app:
```bash
python3 testingServer.py
```
- Access available endpoints:
  - `GET /devices`: Scan for Bluetooth devices.
  - `POST /connect`: Connect to the selected device.
  - `POST /zones`: Receive heart rate zones from the app.

### 2. Mobile App
- Use the app to:
  - Select the heart rate monitor.
  - Configure heart rate zones.

---

## Troubleshooting

### Common Issues

1. **No LEDs Lighting Up**:
   - Verify SPI is enabled and wired correctly.
   - Test LEDs with a simple script:
     ```python
     import board
     import neopixel_spi

     spi = board.SPI()
     pixels = neopixel_spi.NeoPixel_SPI(spi, 20)
     pixels.fill(0xFF0000)  # Red
     pixels.show()
     ```

2. **Bluetooth Connection Fails**:
   - Ensure the monitor is turned on and not connected to another device.
   - Check the Bluetooth address in `pulseGlowled.py`.

3. **Heart Rate Zones Not Updating**:
   - Verify the `zones.json` file format.
   - Ensure the app is sending valid data to the server.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

