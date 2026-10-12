from ultralytics import YOLO
import cv2
import requests
from urllib.parse import quote

# =====================================================
# Model Path
# =====================================================

MODEL_PATH = "models/best.pt"
# =====================================================
# Camera Settings
# =====================================================

#CAMERA_SOURCE = "http://192.168.1.161:81/stream"
CAMERA_INDEX = 0
CONFIDENCE = 0.55

# =====================================================
# Blynk Settings
# =====================================================

BLYNK_TOKEN = ""
BLYNK_SERVER = "https://blynk.cloud"

AI_CLASS_PIN = "V10"
AI_CONFIDENCE_PIN = "V11"
CAMERA_STATUS_PIN = "V12"




if not BLYNK_TOKEN:
    return

# =====================================================
# Blynk Write Function
# =====================================================

def blynk_write(pin, value):
    encoded_value = quote(str(value))
    url = f"{BLYNK_SERVER}/external/api/update?token={BLYNK_TOKEN}&{pin}={encoded_value}"

    try:
        response = requests.get(url, timeout=3)

        if response.status_code != 200:
            print(f"Blynk error on {pin}: {response.status_code} | {response.text}")

    except Exception as e:
        print(f"Blynk connection error on {pin}: {e}")

# =====================================================
# Load YOLO Model
# =====================================================

model = YOLO(MODEL_PATH)

# =====================================================
# Open Laptop Camera
# =====================================================

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("Camera not opened. Try CAMERA_INDEX = 1")
    blynk_write(CAMERA_STATUS_PIN, "Offline")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Live detection started")
print("Press Q to exit")

blynk_write(CAMERA_STATUS_PIN, "Online")

last_class = ""

# =====================================================
# Main Loop
# =====================================================

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        blynk_write(CAMERA_STATUS_PIN, "Offline")
        break

    # Run YOLO detection
    results = model(frame, conf=CONFIDENCE, verbose=False)

    current_class = "No Detection"
    current_confidence = 0.0

    # Get highest confidence detection
    if len(results[0].boxes) > 0:
        best_box = None
        best_conf = 0.0

        for box in results[0].boxes:
            conf = float(box.conf[0])

            if conf > best_conf:
                best_conf = conf
                best_box = box

        if best_box is not None:
            class_id = int(best_box.cls[0])
            current_class = model.names[class_id]
            current_confidence = best_conf

    # Send to Blynk only when class changes
    if current_class != last_class:
        print(f"Detected: {current_class} ({current_confidence:.2f})")

        blynk_write(AI_CLASS_PIN, current_class)
        blynk_write(AI_CONFIDENCE_PIN, round(current_confidence * 100, 1))
        blynk_write(CAMERA_STATUS_PIN, "Online")

        last_class = current_class

    # Draw YOLO boxes
    frame_with_boxes = results[0].plot()

    # Display class and confidence on video
    cv2.putText(
        frame_with_boxes,
        f"Class: {current_class}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frame_with_boxes,
        f"Confidence: {current_confidence:.2f}",
        (20, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.imshow("Bottle Detection Live", frame_with_boxes)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# =====================================================
# Shutdown
# =====================================================

blynk_write(CAMERA_STATUS_PIN, "Stopped")

cap.release()
cv2.destroyAllWindows()