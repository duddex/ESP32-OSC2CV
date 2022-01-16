import cv2
import mediapipe as mp
import math
import numpy as np
from pythonosc.udp_client import SimpleUDPClient

# Mediapipe Solutions APIs
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Webcam Setup
wCam, hCam = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wCam)
cam.set(4, hCam)

# Open connection to 192.168.200.66 on port 8000
client = SimpleUDPClient("192.168.200.66", 8000)

# Store values of trigger (index finger and thumb closed)
trigger = 0.00
oldTrigger = 0.00

# Mediapipe Hand Landmark Model
with mp_hands.Hands() as hands:
    while cam.isOpened():
        success, image = cam.read()

        if not success:
            #print("Ignoring empty camera frame.")
            continue # If loading a video, use 'break' instead of 'continue'

        # To improve performance, optionally mark the image as not writeable to pass by reference
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # Using the "multi_hand_landmarks" method for finding the position of the hand landmarks
        lmList = []
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        # Assigning variables for thumb and index finger position
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Marking thumb and index finger with red circles
            cv2.circle(image, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(image, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 200), 1)
            cv2.circle(image, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

            # Calculate the distance between thumb and index finger
            length = math.hypot(x2-x1, y2-y1)

            # Mark closed thumb and index finger with a green circle and set trigger
            if length < 50:
                cv2.circle(image, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
                trigger = 1.00
            else:
                trigger = 0.00

            # Only send the trigger, if the value has changed
            if oldTrigger != trigger:
                client.send_message("/1/push", trigger)
                oldTrigger = trigger

            # Map the distance between thumb and index finger
            # to matching values for drawing the "volume" bar
            # and for sending the value via OSC
            barValue = np.interp(length, [50, 220], [400, 150])
            value = np.interp(length, [50, 220], [0, 255])

            # Draw "volume" bar
            cv2.rectangle(image, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(image, (50, int(barValue)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(image, f'{int(value)}', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

            # Send the value via OSC
            client.send_message("/3/fader1", value)

        cv2.imshow('OSC Hand Gesture Control', image)

        # Press "q" to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cam.release()
