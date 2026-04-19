import time
from datetime import datetime

from camera.fire_detect import FireDetector
from pixhawk.gps_reader import GPSReader
from sensors.stm_reader import STM32Reader
from logger.logger_wrap import Logger

print("[INFO] Starting system...")

fire_detector = FireDetector()

#added this because if gps fails whole program will fail
try:
    gps = GPSReader()
except:
    print("[WARN] GPS initialization failed, using dummy data")
    gps = None

stm = STM32Reader()
logger = Logger()

while True:
    try:
        # ---- FIRE DETECTION ----
        fire_flag, confidence, display = fire_detector.detect()

        # ---- GPS ----
        if gps:
            gps_data = gps.get_position()
        else:
            gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0}

        if fire_flag == 1 and gps:
            gps.send_fire_alert(gps_data["lat"], gps_data["lon"], confidence)

        if fire_flag == 1 and gps and gps_data:
            gps.send_fire_alert(
                gps_data.get("lat", 0.0),
                gps_data.get("lon", 0.0),
                confidence
            )
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

        fire_detector.cleanup()

        break

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(1)