from picamera2 import Picamera2
from inference_sdk import InferenceHTTPClient
import time

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(2)

image_path = "test_fire.jpg"
picam2.capture_file(image_path)
picam2.stop()

client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="REPLACE_WITH_NEW_ROTATED_KEY"
)

result = client.run_workflow(
    workspace_name="mallories-workspace",
    workflow_id="find-fires",
    images={"image": image_path},
    use_cache=False
)

print(result)