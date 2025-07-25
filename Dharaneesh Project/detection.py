

import numpy as np
import time
import cv2
import os
import numpy as np
from playsound import playsound
import threading
import smtplib
import imghdr
from email.message import EmailMessage

def alert(so):
    if so == True :
        threading.Thread(target=playsound, args=('alarm.wav',), daemon=True).start()
def alert2(so):
    if so == True :
        threading.Thread(target=playsound, args=('alarm2.mp3',), daemon=True).start()

def send_email(label):

    Sender_Email = "dharaneeshdharan18@gmail.com"
    Reciever_Email = "kavincharles@gmail.com"
    Password = ''

    newMessage = EmailMessage()    #creating an object of EmailMessage class
    newMessage['Subject'] = "Animal Detected" #Defining email subject
    newMessage['From'] = Sender_Email  #Defining sender email
    newMessage['To'] = Reciever_Email  #Defining reciever email
    newMessage.set_content('An animal has been detected') #Defining email body

    with open('images/' + label + '.png', 'rb') as f:
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.name[7:]

    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Sender_Email, Password)
        smtp.send_message(newMessage)


def async_email(label):
    threading.Thread(target=send_email, args=(label,), daemon=True).start()



args = {"confidence":0.5, "threshold":0.3}
flag = False

labelsPath = "./yolo-coco/coco.names"
LABELS = open(labelsPath).read().strip().split("\n")
final_classes = ['bird', 'cat', 'dog', 'sheep', 'horse', 'cow', 'elephant', 'zebra', 'bear', 'giraffe']

np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

weightsPath = os.path.abspath("./yolo-coco/yolov3-tiny.weights")
configPath = os.path.abspath("./yolo-coco/yolov3-tiny.cfg")

# print(configPath, "\n", weightsPath)

net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

vs = cv2.VideoCapture(0)
writer = None
(W, H) = (None, None)

flag=True
So = False
while True:
    # read the next frame from the file
    (grabbed, frame) = vs.read()

    # if the frame was not grabbed, then we have reached the end
    # of the stream
    if not grabbed:
        break

    # if the frame dimensions are empty, grab them
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()

    # initialize our lists of detected bounding boxes, confidences,
    # and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability)
            # of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > args["confidence"]:
               
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

               
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
        args["threshold"])


    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            
            if(LABELS[classIDs[i]] in final_classes):
                if(flag):
                    flag=False
                    alert(True)

                    async_email(LABELS[classIDs[i]])
                color = [int(c) for c in COLORS[classIDs[i]]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(LABELS[classIDs[i]],
                    confidences[i])
                cv2.putText(frame, text, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    else:
        flag=True

    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break


# release the webcam and destroy all active windows
vs.release()
cv2.destroyAllWindows()


