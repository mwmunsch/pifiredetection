import time
from datetime import datetime

from camera.fire_detect import FireDetector
from pixhawk.gps_reader import GPSReader
from sensors.stm_reader import STM32Reader
from logger.logger_wrap import Logger

print("[INFO] Starting system...")

fire_detector = FireDetector()

try:
    gps = GPSReader()
    print("[INFO] GPS initialized")
except Exception as e:
    print("[WARN] GPS initialization failed:", e)
    gps = None

stm = STM32Reader()
logger = Logger()

# ---- FIRE STATE TRACKING ----
last_fire_state = 0
last_alert_time = 0
ALERT_COOLDOWN = 5  # seconds

# ---- FIRE PERSISTENCE ----
fire_counter = 0
FIRE_THRESHOLD = 3  # consecutive frames required

try:
    while True:
        # ---- FIRE DETECTION ----
        fire_flag, confidence, display = fire_detector.detect()

        # ---- FIRE PERSISTENCE LOGIC ----
        if fire_flag == 1:
            fire_counter += 1
        else:
            fire_counter = 0

        confirmed_fire = fire_counter >= FIRE_THRESHOLD

        print(f"[DEBUG] raw={fire_flag} counter={fire_counter} confirmed={confirmed_fire}")

        # ---- GPS ----
        gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0}

        if gps:
            try:
                data = gps.get_position()
                if data:
                    gps_data = data
            except Exception as e:
                print("[WARN] GPS read failed:", e)

        # ---- SEND ALERT (ONLY ON CONFIRMED FIRE) ----
        current_time = time.time()

        if confirmed_fire:
            if (last_fire_state == 0) or (current_time - last_alert_time > ALERT_COOLDOWN):
                if gps:
                    try:
                        gps.send_fire_alert(
                            gps_data.get("lat", 0.0),
                            gps_data.get("lon", 0.0),
                            confidence
                        )
                        print("[ALERT] Fire alert sent")
                    except Exception as e:
                        print("[WARN] Failed to send fire alert:", e)

                last_alert_time = current_time

        
        last_fire_state = confirmed_fire

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

            # LOG BOTH RAW + CONFIRMED (VERY useful)
            "fire_flag": fire_flag,
            "confirmed_fire": int(confirmed_fire),
            "confidence": confidence,

            "lat": gps_data.get("lat"),
            "lon": gps_data.get("lon"),
            "alt": gps_data.get("alt")
        }

        # ---- LOG ----
        logger.log(log_data)

        print("[DATA]", log_data)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[INFO] Stopping system")

finally:
    fire_detector.cleanup()