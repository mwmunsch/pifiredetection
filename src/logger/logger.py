"""
Simple Serial Logger
Capstone Team 8 Forest Fire Detection Drone
Author: Mallorie Wiggins

How to run:
1. have pip install pyserial
2. check stm32 port and update SERIAL_PORT variable if needed
3. run python3 logger.py
4. Should get some connection message and then data message
5. csv file will be created in logs/ folder with timestamp in name

"""

import serial
import json
import time
import csv
import os
from datetime import datetime

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
PACKET_TIMEOUT = 3

# Create log folder
os.makedirs("logs", exist_ok=True)

# Create file name
filename = f"logs/sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print("[INFO] Logging to", filename)

with open(filename, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "system_time",
        "stm32_time",
        "gas_resistance_raw",
        "pm_concentration",
        "stm_alive",
        "fire_flag",
        "confidence"
    ])

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:

            print("[INFO] Connected to STM32")

            last_packet_time = time.time()

            while True:

                line = ser.readline().decode("utf-8").strip()

                # WATCHDOG CHECK
                if time.time() - last_packet_time > PACKET_TIMEOUT:
                    print("[WARN] STM32 may be frozen (no packets)")
                    last_packet_time = time.time()

                if not line:
                    continue

                try:
                    data = json.loads(line)

                    last_packet_time = time.time()

                    system_time = datetime.now().isoformat()

                    writer.writerow([
                        system_time,
                        data.get("stm32_time", ""),
                        data.get("gas_resistance_raw", ""),
                        data.get("pm_concentration", ""),
                        data.get("stm_alive", ""),
                        data.get("fire_flag", ""),
                        data.get("confidence", "")
                    ])

                    f.flush()

                    print("[DATA]", line)

                except:
                    print("[WARN] Bad JSON:", line)

    except KeyboardInterrupt:
        print("\n[INFO] Logger stopped")