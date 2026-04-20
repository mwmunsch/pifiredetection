import time
from datetime import datetime

from camera.fire_detect import FireDetector
from pixhawk.gps_reader import GPSReader
from sensors.stm_reader import STM32Reader
from logger.logger_wrap import Logger

print("[INFO] Starting system...")

fire_detector = FireDetector()

# Try to initialize GPS, but continue even if it fails
try:
    gps = GPSReader()
    print("[INFO] GPS initialized")
except Exception as e:
    print("[WARN] GPS initialization failed:", e)
    gps = None

stm = STM32Reader()
logger = Logger()

try:
    while True:
        # ---- FIRE DETECTION ----
        fire_flag, confidence, display = fire_detector.detect()

        # ---- GPS ----
        gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0}

        if gps:
            try:
                data = gps.get_position()
                if data:
                    gps_data = data
            except Exception as e:
                print("[WARN] GPS read failed:", e)

        # ---- SEND ALERT (ONLY ONCE) ----
        if fire_flag == 1 and gps:
            try:
                gps.send_fire_alert(
                    gps_data.get("lat", 0.0),
                    gps_data.get("lon", 0.0),
                    confidence
                )
            except Exception as e:
                print("[WARN] Failed to send fire alert:", e)

        # ---- STM32 SENSOR DATA ----
        try:
            stm_data = stm.get_data()
            if stm_data is None:
                stm_data = {}
        except Exception as e:
            print("[WARN] STM read failed:", e)
            stm_data = {}

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

        # ---- LOG ----
        logger.log(log_data)

        print("[DATA]", log_data)

        # small delay so CPU + camera stay stable
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[INFO] Stopping system")

finally:
    fire_detector.cleanup()