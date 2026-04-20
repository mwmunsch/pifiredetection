import cv2
import numpy as np
import time
import os
from picamera2 import Picamera2

class FireDetector:
    def __init__(self):
        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (320, 240)}
        )
        self.picam2.configure(config)
        self.picam2.start()

        self.prev_gray = None

        # Create folder for images
        os.makedirs("fire_images", exist_ok=True)

        # Cooldown for saving images
        self.last_save_time = 0
        self.SAVE_COOLDOWN = 5  # seconds

    def detect(self):
        frame = self.picam2.capture_array()

        if frame is None:
            return 0, 0, None

        display = frame.copy()

        # ---- COLOR DETECTION ----
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([0, 120, 150])
        upper1 = np.array([35, 255, 255])

        lower2 = np.array([160, 120, 150])
        upper2 = np.array([179, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)

        fire_mask = cv2.bitwise_or(mask1, mask2)

        # ---- FLICKER DETECTION ----
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = gray
            return 0, 0, display

        diff = cv2.absdiff(self.prev_gray, gray)
        self.prev_gray = gray

        _, motion_mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # ---- COMBINE ----
        combined = cv2.bitwise_and(fire_mask, motion_mask)

        # ---- FIND BOUNDING BOX ----
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        fire_flag = 0
        confidence = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area > 300:
                x, y, w, h = cv2.boundingRect(cnt)

                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 0, 255), 2)

                fire_flag = 1
                confidence = min(int(area / 50), 100)

        # ---- SAVE IMAGE IF FIRE DETECTED ----
        current_time = time.time()

        if fire_flag == 1 and (current_time - self.last_save_time > self.SAVE_COOLDOWN):
            filename = f"fire_images/fire_{int(current_time)}.jpg"
            cv2.imwrite(filename, display)
            print(f"[ALERT] Fire detected! Saved: {filename} | Confidence: {confidence}%")

            self.last_save_time = current_time

        return fire_flag, confidence, display

    def cleanup(self):
        self.picam2.stop()
        cv2.destroyAllWindows()


# ---- MAIN RUN LOOP ----
if __name__ == "__main__":
    detector = FireDetector()

    try:
        while True:
            fire_flag, confidence, frame = detector.detect()

            # Optional debug print
            print(f"[DEBUG] Fire: {fire_flag}, Confidence: {confidence}")

            time.sleep(0.2)  # keeps CPU stable

    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")

    finally:
        detector.cleanup()