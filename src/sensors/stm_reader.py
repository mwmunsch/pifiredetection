import serial

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

class STM32Reader:
    def __init__(self):
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

        # last known values (important because sensors come on separate lines)
        self.data = {
            "gas_resistance_raw": 0,
            "pm1_0": 0,
            "pm2_5": 0,
            "pm10": 0,
            "air_quality_status": "UNKNOWN",
            "gas_status": "UNKNOWN"
        }

    def get_data(self):
        try:
            line = self.ser.readline().decode(errors="ignore").strip()

            print("[STM RAW]", line)

            if not line:
                return self.data

            parts = line.split(",")

            # ---- BMV080 (PM SENSOR) ----
            if parts[0] == "BMV080":
                # Format:
                # BMV080,time,pm1,pm2_5,pm10,air_status
                self.data["pm1_0"] = float(parts[2])
                self.data["pm2_5"] = float(parts[3])
                self.data["pm10"] = float(parts[4])

                # 0 = BAD, 1 = GOOD (adjust if needed)
                self.data["air_quality_status"] = "GOOD" if parts[5] == "1" else "BAD"

            # ---- BME690 (GAS SENSOR) ----
            elif parts[0] == "BME690_BSEC":
                # gas resistance is usually near the end
                self.data["gas_resistance_raw"] = float(parts[9])

                # simple status logic (you can tune later)
                if self.data["gas_resistance_raw"] > 50000:
                    self.data["gas_status"] = "GOOD"
                else:
                    self.data["gas_status"] = "BAD"

            return self.data

        except Exception as e:
            print("[STM ERROR]", e)
            return self.data