from picamera2 import Picamera2
import time
import cv2
import requests

API_KEY = "REPLACE_WITH_NEW_ROTATED_KEY"

# Your model endpoint
MODEL_URL = "https://detect.roboflow.com/find-fires/1"

# Setup camera
picam2 = Picamera2()
picam2.start()

print("Fire detection running...")

while True:
    # Capture image
    frame = picam2.capture_array()
    cv2.imwrite("frame.jpg", frame)

    # Send to Roboflow
    with open("frame.jpg", "rb") as f:
        response = requests.post(
            MODEL_URL,
            params={"api_key": API_KEY},
            files={"file": f}
        )

    result = response.json()
    print(result)

    # Check for fire
    if "predictions" in result and len(result["predictions"]) > 0:
        print("🔥 FIRE DETECTED 🔥")

    time.sleep(3)