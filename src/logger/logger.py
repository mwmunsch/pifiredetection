"""
Serial Logger (CSV parser version)
Capstone Team 8 Forest Fire Detection Drone
Author: Mallorie Wiggins

Reads STM32 UART output (CSV format like BMV080,... and BME690_BSEC,...)
***Had to update because they are using csv instead of json like discussed
minicom -b 115200 -D /dev/ttyAMA0 run this on the pi to see raw output from STM32
"""

import serial
import time
import csv
import os
from datetime import datetime

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

PACKET_TIMEOUT = 5
STM_TIMEOUT = 10

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

                line = ser.readline().decode("utf-8", errors="ignore").strip()

                # WATCHDOG CHECK
                if time.time() - last_packet_time > PACKET_TIMEOUT:
                    print("[WARN] No data received recently")
                    last_packet_time = time.time()

                if not line:
                    continue

                print("[RAW]", line)

                try:
                    parts = line.split(",")

                    # Safety check
                    if len(parts) < 5:
                        print("[WARN] Incomplete packet:", line)
                        continue

                    system_time = datetime.now().isoformat()

                    # Default values
                    stm32_time = ""
                    gas_resistance_raw = ""
                    pm_concentration = ""
                    stm_alive = 1
                    fire_flag = ""
                    confidence = ""

                    # Parse DATA packet
                    if parts[0] == "DATA":
                        gas_resistance_raw = float(parts[1])
                        pm_concentration = float(parts[2])
                        fire_flag = int(parts[3])
                        confidence = float(parts[4])

                        print("[DATA]", gas_resistance_raw, pm_concentration, fire_flag, confidence)

                    else:
                        print("[INFO] Unknown packet:", line)
                        continue

                    # Update last packet time
                    last_packet_time = time.time()

                    # Write to CSV
                    writer.writerow([
                        system_time,
                        stm32_time,
                        gas_resistance_raw,
                        pm_concentration,
                        stm_alive,
                        fire_flag,
                        confidence
                    ])

                    f.flush()

                except Exception as e:
                    print("[WARN] Parse error:", line)
                    print("       ", e)

    except KeyboardInterrupt:
        print("\n[INFO] Logger stopped")