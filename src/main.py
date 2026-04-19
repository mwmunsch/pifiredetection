from picamera2 import Picamera2
from camera.fire_detect import FireDetector
from pixhawk.gps_reader import GPSReader
from logger.logger_wrap import Logger
from sensors.stm_reader import STM32Reader

import cv2
import time

def main():
    # Camera setup
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(
        main={"format": "BGR888", "size": (640, 480)}
    ))
    picam2.start()

    detector = FireDetector()
    gps = GPSReader()
    logger = Logger()

    print("[INFO] System started")

    while True:
        system_time = time.time()

    
        frame = picam2.capture_array()
        frame, detections = detector.detect(frame)

        if detections:
            max_conf = max(d["confidence"] for d in detections)
            fire_flag = 1 if max_conf > 0.5 else 0
        else:
            max_conf = 0.0
            fire_flag = 0

        
        gps_data = gps.get_data()

        if gps_data:
            lat = gps_data["lat"]
            lon = gps_data["lon"]
            alt = gps_data["alt"]
        else:
            lat = lon = alt = 0

       
        logger.log({
            "system_time": system_time,
            "gas_resistance_raw": gas,
            "pm1_0": pm1,
            "pm2_5": pm25,
            "pm10": pm10,
            "air_quality_status": air_status,
            "gas_status": gas_status,
            "fire_flag": fire_flag,
            "confidence": max_conf,
            "lat": lat,
            "lon": lon,
            "alt": alt
        })

        
        cv2.imshow("Fire Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()