from flask import Flask, jsonify, request
from bleak import BleakScanner, BleakClient, BleakError
import asyncio
import threading
import subprocess
import json

app = Flask(__name__)
lock = threading.Lock()  # Prevent concurrent scans
loop = asyncio.new_event_loop()  # Create a new event loop for async tasks
asyncio.set_event_loop(loop)

# Global variables
connected_device = None  # To store the connected device globally
heart_rate_zones = {}  # Heart rate zones data
led_process = None  # To store the subprocess running `ledtest.py`

@app.route('/devices', methods=['GET'])
def list_bluetooth_devices():
    if lock.locked():
        return jsonify({"error": "A scan is already in progress. Try again later."}), 429

    try:
        lock.acquire()
        devices = asyncio.run_coroutine_threadsafe(scan_bluetooth_devices(), loop).result()
        return jsonify(devices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        lock.release()


async def scan_bluetooth_devices():
    print("Scanning for Bluetooth devices...")
    devices = []
    try:
        scanner = BleakScanner()
        discovered_devices = await scanner.discover()
        for d in discovered_devices:
            devices.append({
                "address": d.address,
                "name": d.name or "Unknown",
                "rssi": d.details["RSSI"] if "RSSI" in d.details else None
            })
    except Exception as e:
        print(f"Error during scan: {e}")
    print(f"Found {len(devices)} devices.")
    return devices


@app.route('/connect', methods=['POST'])
def connect_to_device():
    global connected_device, led_process

    if lock.locked():
        return jsonify({"error": "A connection is already in progress."}), 429

    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({"error": "Device address is required."}), 400

    try:
        lock.acquire()
        # Attempt to connect to the device
        asyncio.run_coroutine_threadsafe(connect(address), loop).result()

        # Stop any existing `ledtest.py` process
        if led_process:
            led_process.terminate()

        # Start `ledtest.py` with the selected Bluetooth address
        led_process = subprocess.Popen(
            ['python3', 'pulseGlowled.py', '--address', address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Started LED monitoring script for {address}.")
        return jsonify({"status": f"Connected to {address} and started LED monitoring."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        lock.release()


async def connect(address):
    global connected_device
    print(f"Attempting to connect to {address}...")
    try:
        client = BleakClient(address)
        await client.connect()
        connected_device = client
        print(f"Connected to {address}")
    except BleakError as e:
        print(f"Connection failed: {e}")
        raise e


@app.route('/zones', methods=['POST'])
def set_zones():
    global heart_rate_zones
    data = request.get_json()

    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid data format"}), 400

    try:
        heart_rate_zones = data  # Store the zones
        print(f"Received heart rate zones: {heart_rate_zones}")

        # Save zones to a file for the ledtest.py script
        with open('zones.json', 'w') as f:
            json.dump(heart_rate_zones, f)

        return jsonify({"status": "Zones received successfully!"})
    except Exception as e:
       return jsonify({"error": str(e)}), 500


def start_server():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Server is running at http://192.168.1.26:5000")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        if led_process:
            led_process.terminate()  # Stop the LED script on shutdown
    finally:
        loop.stop()
        loop.close()
