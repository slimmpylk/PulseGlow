import argparse
import time
import json
import board
import neopixel_spi
from bleak import BleakClient
import asyncio
import requests

# Parse arguments for device address
parser = argparse.ArgumentParser(description="LED Heart Rate Monitor")
parser.add_argument('--address', required=True, help="Bluetooth address of the heart rate monitor")
args = parser.parse_args()

# Load heart rate zones from the configuration file
def load_zones():
    try:
        with open('zones.json', 'r') as f:
            zones = json.load(f)['zones']
            print(f"Loaded zones: {zones}")  # Debugging output
            return zones
    except FileNotFoundError:
        print("Zones configuration file not found. Using default zones.")
        return []
    except Exception as e:
        print(f"Error loading zones: {e}")
        return []


# LED configuration
spi = board.SPI()  # SPI for GPIO19 (MOSI)
NUM_LEDS = 20
BRIGHTNESS = 0.05  # Adjust brightness as needed
pixels = neopixel_spi.NeoPixel_SPI(spi, NUM_LEDS)

# Define colors for heart rate zones
COLORS = {
    1: 0xFFC0CB,  # Pink
    2: 0x0000FF,  # Blue
    3: 0x00FF00,  # Green
    4: 0xFFFF00,  # Yellow
    5: 0xFF0000   # Red
}

# Map heart rate to zone based on zones received
def get_zone_from_heart_rate(hr, zones):
    for zone_data in zones:
        try:
            # Ensure zone_data is a dictionary
            if not isinstance(zone_data, dict):
                print(f"Invalid zone data format: {zone_data}")
                continue

            # Clean the range string and split into lower and upper bounds
            range_cleaned = zone_data['range'].replace('–', '-').replace(' bpm', '')
            range_lower, range_upper = map(int, range_cleaned.split('-'))
            
            # Check if the heart rate falls within the range
            if range_lower <= hr <= range_upper:
                return zone_data['zone']
        except (ValueError, KeyError) as e:
            print(f"Error processing zone data: {zone_data}, Error: {e}")
    return 1  # Default to Zone 1




# Function to apply brightness to a color
def apply_brightness(color, brightness):
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    r = int(r * brightness)
    g = int(g * brightness)
    b = int(b * brightness)
    return (r << 16) | (g << 8) | b

# Function to light up LEDs for a given heart rate
def update_leds_for_heart_rate(hr, zones):
    print(f"Updating LEDs for HR: {hr}, Zones: {zones}")  # Debugging output
    zone = get_zone_from_heart_rate(hr, zones)
    color = COLORS.get(zone, 0x000000)  # Default to off if zone is invalid
    color = apply_brightness(color, BRIGHTNESS)
    print(f"Setting LEDs to Zone {zone} with color {color:#06X}")  # Debugging output
    pixels.fill(color)
    pixels.show()


# Main async function to read heart rate and control LEDs
async def monitor_heart_rate():
    print(f"Connecting to device at {args.address}...")
    zones = load_zones()  # Load zones from file
    async with BleakClient(args.address, timeout=30.0) as client:
        if await client.is_connected():
            print(f"Connected to device!")

            # Callback to handle heart rate data
            def handle_heart_rate(sender, data):
                heart_rate = data[1]
                print(f"Heart Rate: {heart_rate} bpm")
                update_leds_for_heart_rate(heart_rate, zones)

            # Start notifications for heart rate
            await client.start_notify("00002a37-0000-1000-8000-00805f9b34fb", handle_heart_rate)
            print("Monitoring heart rate...")

            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("Stopping heart rate monitoring...")
                await client.stop_notify("00002a37-0000-1000-8000-00805f9b34fb")
                pixels.fill(0x000000)  # Turn off LEDs
                pixels.show()

# Run the script
asyncio.run(monitor_heart_rate())
