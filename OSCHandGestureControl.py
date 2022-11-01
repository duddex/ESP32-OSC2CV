import cv2
import math
import numpy as np
from pythonosc.udp_client import SimpleUDPClient


class mpHands:
    import mediapipe as mp

    def __init__(self):
        self.hands = self.mp.solutions.hands.Hands(
            model_complexity=0, min_detection_confidence=0.6, min_tracking_confidence=0.4)

    def Marks(self, frame):
        myHands = []
        handsType = []
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)
        if results.multi_hand_landmarks != None:
            for hand in results.multi_handedness:
                handType = hand.classification[0].label
                handsType.append(handType)
            for handLandMarks in results.multi_hand_landmarks:
                myHand = []
                for landMark in handLandMarks.landmark:
                    myHand.append(
                        (int(landMark.x*width), int(landMark.y*height)))
                myHands.append(myHand)
        return myHands, handsType


# Webcam Setup
width = 640
height = 480
cam = cv2.VideoCapture(0)
cam.set(3, width)
cam.set(4, height)

# Open connection to 192.168.4.1 on port 8000
# Check the output of ESP32-OSC2CV.ino to get the IP address
client = SimpleUDPClient("192.168.4.1", 8000)

# instantiate Mediapipe Helperclass
findHands = mpHands()

while cam.isOpened():
    success, image = cam.read()
    if not success:
        # Ignoring empty camera frame
        continue

    image = cv2.resize(image, (width, height))
    handData, handsType = findHands.Marks(image)
    for hand, handType in zip(handData, handsType):
        if handType == 'Left':
            handColor = (0, 0, 255)
            textPosition = 40
            oscTriggerPath = "/3/push1"
            oscValuePath = "/3/fader1"
        if handType == 'Right':
            handColor = (255, 0, 0)
            textPosition = 550
            oscTriggerPath = "/3/push2"
            oscValuePath = "/3/fader2"

        thumbTip = hand[4]
        indexFingerTip = hand[8]
        x1, y1 = thumbTip
        x2, y2 = indexFingerTip

        # Calculate the distance between thumb and index finger
        length = math.hypot(x2-x1, y2-y1)
        value = np.interp(length, [50, 200], [0, 255])
        cv2.putText(image, f'{int(value)}', (textPosition, 450),
                    cv2.FONT_HERSHEY_COMPLEX, 1, handColor, 2)

        # Mark closed thumb and index finger with a green circle and set trigger
        if length < 20:
            cv2.circle(image, indexFingerTip, 10, (0, 255, 0), cv2.FILLED)
            trigger = 1.00
        else:
            # Mark thumb and index finger with circles
            cv2.circle(image, thumbTip, 8, handColor, cv2.FILLED)
            cv2.circle(image, indexFingerTip, 8, handColor, cv2.FILLED)
            cv2.line(image, thumbTip, indexFingerTip, handColor, 2)
            trigger = 0.00

        # Send the value via OSC
        client.send_message(oscValuePath, value)
        client.send_message(oscTriggerPath, trigger)

    cv2.imshow('OSC Hand Gesture Control', image)

    # press "q" to quit
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cam.release()
