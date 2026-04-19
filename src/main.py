import time
from datetime import datetime

from camera.fire_detect import FireDetector
from pixhawk.gps_reader import GPSReader
from sensors.stm_reader import STM32Reader
from logger.logger_wrap import Logger

print("[INFO] Starting system...")

fire_detector = FireDetector()
gps = GPSReader()
stm = STM32Reader()
logger = Logger()

while True:
    try:
        # ---- FIRE DETECTION ----
        fire_flag, confidence = fire_detector.detect()

        # ---- GPS ----
        gps_data = gps.get_position()

        # ---- STM32 SENSOR DATA ----
        stm_data = stm.get_data()

        # ---- BUILD DATA PACKET ----
        log_data = {
            "system_time": datetime.now().isoformat(),

            "gas_resistance_raw": stm_data.get("gas_resistance_raw"),
            "pm1_0": stm_data.get("pm1_0"),
            "pm2_5": stm_data.get("pm2_5"),
            "pm10": stm_data.get("pm10"),
            "air_quality_status": stm_data.get("air_quality_status"),
            "gas_status": stm_data.get("gas_status"),

            "fire_flag": fire_flag,
            "confidence": confidence,

            "lat": gps_data.get("lat"),
            "lon": gps_data.get("lon"),
            "alt": gps_data.get("alt")
        }

        logger.log(log_data)

        print("[DATA]", log_data)

        time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping system")
        break

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(1)