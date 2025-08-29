# electricity_saver_hog.py
import cv2
import RPi.GPIO as GPIO
import time

# Relay setup
RELAY_PIN = 17  # GPIO17, change if needed
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# HOG person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)  # Pi camera / USB cam

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize for speed
        frame_resized = cv2.resize(frame, (320, 240))
        boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8,8))

        if len(boxes) > 0:
            print("Person detected → Light ON")
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:
            print("No person → Light OFF")
            GPIO.output(RELAY_PIN, GPIO.LOW)

        # Show preview
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame_resized, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.imshow("Electricity Saver (HOG)", frame_resized)

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
