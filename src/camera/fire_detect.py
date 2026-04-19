import cv2
import numpy as np
import os


class FireDetector:
    def __init__(self):
        # Get base directory (pifiredetection/)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        cfg_path = os.path.join(BASE_DIR, "fire.cfg")
        weights_path = os.path.join(BASE_DIR, "fire.weights")
        names_path = os.path.join(BASE_DIR, "fire.names")

        print("[INFO] Loading model...")
        self.net = cv2.dnn.readNet(weights_path, cfg_path)

        with open(names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        print("[INFO] Fire detector ready")

    def detect(self, frame):
        height, width, _ = frame.shape

        # Prepare image
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416),
                                     swapRB=True, crop=False)
        self.net.setInput(blob)

        outputs = self.net.forward(self.output_layers)

        boxes = []
        confidences = []
        class_ids = []

        # Process detections
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.4:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.3)

        detections = []

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                confidence = confidences[i]

                detections.append({
                    "box": (x, y, w, h),
                    "confidence": confidence
                })

                # Draw box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, f"Fire: {confidence:.2f}",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 2)

        return frame, detections