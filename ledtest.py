import time
import board
import neopixel_spi
from bleak import BleakClient
import asyncio

# Polar H10 configuration
POLAR_H10_ADDRESS = "A0:9E:1A:BA:D5:9F"  # Replace with your Polar H10 address
HEART_RATE_CHAR = "00002a37-0000-1000-8000-00805f9b34fb"

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

# Map heart rate to zone
def get_zone_from_heart_rate(hr):
    if hr <= 60:
        return 1  # Zone 1: Pink
    elif hr <= 65:
        return 2  # Zone 2: Blue
    elif hr <= 70:
        return 3  # Zone 3: Green
    elif hr <= 75:
        return 4  # Zone 4: Yellow
    else:
        return 5  # Zone 5: Red

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
def update_leds_for_heart_rate(hr):
    zone = get_zone_from_heart_rate(hr)
    color = COLORS[zone]
    color = apply_brightness(color, BRIGHTNESS)
    pixels.fill(color)
    pixels.show()

# Main async function to read heart rate and control LEDs
async def monitor_heart_rate():
    print(f"Connecting to Polar H10 at {POLAR_H10_ADDRESS}...")
    async with BleakClient(POLAR_H10_ADDRESS, timeout=30.0) as client:
        if await client.is_connected():
            print(f"Connected to Polar H10!")

            # Callback to handle heart rate data
            def handle_heart_rate(sender, data):
                heart_rate = data[1]
                print(f"Heart Rate: {heart_rate} bpm")
                update_leds_for_heart_rate(heart_rate)

            # Start notifications for heart rate
            await client.start_notify(HEART_RATE_CHAR, handle_heart_rate)
            print("Monitoring heart rate...")

            try:
                # Keep running until interrupted
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("Stopping heart rate monitoring...")
                await client.stop_notify(HEART_RATE_CHAR)
                pixels.fill(0x000000)  # Turn off LEDs
                pixels.show()

# Run the script
asyncio.run(monitor_heart_rate())
