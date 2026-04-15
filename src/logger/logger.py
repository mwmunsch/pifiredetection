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

os.makedirs("logs", exist_ok=True)

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
            gas_resistance_raw = None
            pm_concentration = None

            while True:

                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if time.time() - last_packet_time > PACKET_TIMEOUT:
                    print("[WARN] No data received recently")
                    last_packet_time = time.time()

                if not line:
                    continue

                print("[RAW]", line)

                try:
                    parts = line.split(",")

                    if len(parts) < 5:
                        print("[WARN] Incomplete packet:", line)
                        continue

                    system_time = datetime.now().isoformat()

                    stm32_time = ""
                    stm_alive = 1
                    fire_flag = ""
                    confidence = ""

                    if parts[0] == "BME690_BSEC":
                        gas_resistance_raw = float(parts[9])
                        print("[BME690] Gas:", gas_resistance_raw)

                    elif parts[0] == "BMV080":
                        pm_concentration = float(parts[3])
                        print("[BMV080] PM2.5:", pm_concentration)
                    
                    else:
                        print("[WARN] Unknown packet type:", parts[0])
                        continue

                    last_packet_time = time.time()

                    if gas_resistance_raw is None or pm_concentration is None:
                        continue

                    fire_flag = 1 if (pm_concentration > 10 and gas_resistance_raw < 80000) else 0
                    confidence = min(100, (pm_concentration / 20) * 100)

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

                    gas_resistance_raw = None
                    pm_concentration = None

                except Exception as e:
                    print("[WARN] Parse error:", line)
                    print("       ", e)

    except KeyboardInterrupt:
        print("\n[INFO] Logger stopped")

