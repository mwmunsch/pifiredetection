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

os.makedirs("logs", exist_ok=True)

filename = f"logs/sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print("[INFO] Logging to", filename)

with open(filename, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "system_time",
        "gas_resistance_raw",
        "pm1_0",
        "pm2_5",
        "pm10",
        "air_quality_status",
        "gas_status",
        "fire_flag",
        "confidence"
    ])

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:

            print("[INFO] Connected to STM32")

            last_packet_time = time.time()

            gas_resistance_raw = None
            pm1 = None
            pm25 = None
            pm10 = None

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

                    system_time = datetime.now().isoformat()

                    if parts[0] == "BMV080" and len(parts) >= 6:
                        pm1 = float(parts[2])
                        pm25 = float(parts[3])
                        pm10 = float(parts[4])

                        if pm25 <= 12:
                            air_status = "GOOD"
                        elif pm25 <= 35:
                            air_status = "MODERATE"
                        else:
                            air_status = "BAD"

                        print(f"[BMV080] PM1.0:{pm1} PM2.5:{pm25} PM10:{pm10} Air:{air_status}")

                    elif parts[0] == "BME690_BSEC" and len(parts) >= 10:
                        gas_resistance_raw = float(parts[9])

                        if gas_resistance_raw > 50000:
                            gas_status = "GOOD"
                        elif gas_resistance_raw > 30000:
                            gas_status = "MODERATE"
                        else:
                            gas_status = "BAD"

                        print(f"[BME690] Gas:{gas_resistance_raw} Air:{gas_status}")

                    else:
                        continue

                    last_packet_time = time.time()

                    if gas_resistance_raw is None or pm25 is None:
                        continue

                    fire_flag = 1 if (pm25 > 10 and gas_resistance_raw < 80000) else 0
                    confidence = min(100, (pm25 / 20) * 100)

                    writer.writerow([
                        system_time,
                        gas_resistance_raw,
                        pm1,
                        pm25,
                        pm10,
                        air_status,
                        gas_status,
                        fire_flag,
                        confidence
                    ])

                    f.flush()

                    gas_resistance_raw = None
                    pm1 = None
                    pm25 = None
                    pm10 = None

                except Exception as e:
                    print("[WARN] Parse error:", line)
                    print(e)

    except KeyboardInterrupt:
        print("\n[INFO] Logger stopped")