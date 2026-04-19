import csv
import os
from datetime import datetime

class Logger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)

        self.filename = f"logs/sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        print("[INFO] Logging to", self.filename)

        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "system_time",
            "gas_resistance_raw",
            "pm1_0",
            "pm2_5",
            "pm10",
            "air_quality_status",
            "gas_status",
            "fire_flag",
            "confidence",
            "lat",
            "lon",
            "alt"
        ])

    def log(self, data):
        self.writer.writerow([
            data.get("system_time"),
            data.get("gas"),
            data.get("pm1"),
            data.get("pm25"),
            data.get("pm10"),
            data.get("air_status"),
            data.get("gas_status"),
            data.get("fire_flag"),
            data.get("confidence"),
            data.get("lat"),
            data.get("lon"),
            data.get("alt")
        ])

        self.file.flush()