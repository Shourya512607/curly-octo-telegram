from flask import Flask, Response, jsonify
import cv2
import RPi.GPIO as GPIO

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
person_detected = False

def generate_frames():
    global person_detected
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (320, 240))
        boxes, _ = hog.detectMultiScale(frame_resized, winStride=(8,8))
        if len(boxes) > 0:
            person_detected = True
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:
            person_detected = False
            GPIO.output(RELAY_PIN, GPIO.LOW)
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0,255,0), 2)
        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({
        "person_detected": person_detected,
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
