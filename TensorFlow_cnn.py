# electricity_saver_tf.py
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import RPi.GPIO as GPIO

# Relay setup
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# Load TFLite model
interpreter = tflite.Interpreter(model_path="mobilenet_ssd_v2_coco.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        img = cv2.resize(frame, (300, 300))
        input_data = np.expand_dims(img, axis=0).astype(np.uint8)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # bounding boxes
        classes = interpreter.get_tensor(output_details[1]['index'])[0]  # class IDs
        scores = interpreter.get_tensor(output_details[2]['index'])[0]  # confidence

        person_detected = False
        for i, score in enumerate(scores):
            if score > 0.5 and int(classes[i]) == 0:  # class 0 = person
                person_detected = True
                ymin, xmin, ymax, xmax = boxes[i]
                (h, w) = frame.shape[:2]
                cv2.rectangle(frame, (int(xmin*w), int(ymin*h)), (int(xmax*w), int(ymax*h)), (0,255,0), 2)

        if person_detected:
            print("Person detected → Light ON")
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:
            print("No person → Light OFF")
            GPIO.output(RELAY_PIN, GPIO.LOW)

        cv2.imshow("Electricity Saver (TF)", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
