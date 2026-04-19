import cv2
import numpy as np

class FireDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Pi camera
        self.prev_gray = None

    def detect(self):
        ret, frame = self.cap.read()
        if not ret:
            return 0, 0

        # Resize for speed
        frame = cv2.resize(frame, (320, 240))

        # ---- COLOR DETECTION (HSV) ----
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Fire-like colors (tweak if needed)
        lower1 = np.array([0, 120, 150])     # red/orange
        upper1 = np.array([35, 255, 255])

        lower2 = np.array([160, 120, 150])   # deep red
        upper2 = np.array([179, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)

        fire_mask = cv2.bitwise_or(mask1, mask2)

        # ---- FLICKER DETECTION ----
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = gray
            return 0, 0

        diff = cv2.absdiff(self.prev_gray, gray)
        self.prev_gray = gray

        _, motion_mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # ---- COMBINE ----
        combined = cv2.bitwise_and(fire_mask, motion_mask)

        fire_pixels = np.sum(combined > 0)
        total_pixels = combined.size

        ratio = fire_pixels / total_pixels

        # ---- DECISION ----
        if ratio > 0.02:   # threshold (tune this)
            fire_flag = 1
        else:
            fire_flag = 0

        confidence = min(int(ratio * 5000), 100)

        return fire_flag, confidence