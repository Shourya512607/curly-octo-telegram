from flask import Flask, Response, jsonify
import cv2
import RPi.GPIO as GPIO
import threading
import time

# Flask
app = Flask(__name__)

# Relay setup
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# HOG person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Thread-safe person detection
person_detected = False
lock = threading.Lock()

def generate_frames():
    global person_detected
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize for faster detection
        frame_resized = cv2.resize(frame, (320, 240))

        boxes, _ = hog.detectMultiScale(frame_resized, winStride=(8,8))
        with lock:
            if len(boxes) > 0:
                person_detected = True
                GPIO.output(RELAY_PIN, GPIO.HIGH)
            else:
                person_detected = False
                GPIO.output(RELAY_PIN, GPIO.LOW)

        # Draw rectangles
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0,255,0), 2)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Small sleep to reduce CPU usage
        time.sleep(0.03)  # ~30 FPS

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    with lock:
        detected = person_detected
    return jsonify({
        "person_detected": detected,
        "relay": "ON" if GPIO.input(RELAY_PIN) else "OFF"
    })

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        GPIO.cleanup()
