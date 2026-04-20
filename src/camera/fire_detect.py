import cv2
import numpy as np

class FireDetector:
    def __init__(self):
        # using imx500
        self.cap = cv2.VideoCapture("libcamera ! video/x-raw, width=320, height=240, framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

    def detect(self):
        ret, frame = self.cap.read()
        if not ret:
            return 0, 0, None

        frame = cv2.resize(frame, (320, 240))
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

        # ---- FLICKER ----
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

            if area > 300:  # filter noise
                x, y, w, h = cv2.boundingRect(cnt)

                # draw box
                cv2.rectangle(display, (x, y), (x+w, y+h), (0, 0, 255), 2)

                fire_flag = 1
                confidence = min(int(area / 50), 100)

        # ---- SHOW WINDOW ----
        cv2.imshow("Fire Detection", display)

        # press q to quit window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return 0, 0, display

        return fire_flag, confidence, display

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()