from os.path import dirname, join
import numpy as np
import tkinter
from PIL import ImageTk,Image
import cv2
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from socket import timeout
from time import sleep
import serial

vid = cv2.VideoCapture(0)

window = tkinter.Tk()
window.title("Motor Cycle Monitor")
window.geometry('880x480')

Image_Label = tkinter.Label(window)
Image_Label.place(x=0,y=0)

MC_satate = tkinter.StringVar()
MC_state_lable = tkinter.Label(window,textvariable=MC_satate,font=("Arial",25),justify="left")
MC_state_lable.place(x=655,y=10)

#creating dnn network for face detection
protoPath = join(dirname(__file__), "deploy.prototxt.txt")
modelPath = join(dirname(__file__), "res10_300x300_ssd_iter_140000.caffemodel")
helmeth5 = join(dirname(__file__), "helmet.h5")
network = cv2.dnn.readNetFromCaffe(protoPath,modelPath)
model=keras.models.load_model(helmeth5)

toggle = 0
ACK = 0x3F
NACK = 0xC0
ACK = ACK.to_bytes(1,'big')
NACK = NACK.to_bytes(1,'big')
SerialConn = False
THROTTEL = "OFF"
HELMET = "OFF"
ENGINE = "OFF"
GEAR = 0
KEY = "OFF"
run = True

while run:

    if SerialConn == False:
        SerialConn = True
        try:
            ArduinoSerial = serial.Serial(port='COM4',baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=0.5)
        except:
            SerialConn = False
        if SerialConn: print(SerialConn)
    
    ret,frame = vid.read()
    if ret:
        (h,w)=frame.shape[:2]#getting height and width od the captured frame
        blob=cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),1, (300,300),(104.0,177.0,123.0))
        network.setInput(blob)
        detections=network.forward()
        for i in range(0, detections.shape[2]):
            confidence=detections[0,0,i,2]
            if confidence > 0.7:
                box=detections[0,0,i,3:7]*np.array([w,h,w,h])
                (startX,startY,endX,endY)=box.astype(int)

                Y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(frame,(startX-100,startY-100),(endX+50,endY+50),(0,0,255),2)
                temp = frame[startY-100:endY+100,startX-100:endX+100]
                temp=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                temp=cv2.resize(temp,(224,224))
                temp=preprocess_input(temp)
                temp=np.expand_dims(temp,axis=0)
                pred_val=model.predict(temp)
                #print(pred_val)
                pred_val=np.ravel(pred_val).item()

                if pred_val < 0.7 :
                    HELMET = "OFF"
                    text = 'NO-HELMET'+ str(pred_val)
                    cv2.rectangle(frame,(startX-100,startY-100),(endX+50,endY+50),(0,0,255),2)
                    cv2.putText(frame,text,(startX,Y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
                    if (SerialConn == True) and (toggle != "NACK") :
                        print("NACK")
                        toggle = "NACK"
                        ArduinoSerial.write(NACK)
                else:
                    HELMET = "ON"
                    text = 'HELMET'+ str(pred_val)
                    cv2.rectangle(frame,(startX-100,startY-100),(endX+50,endY+50),(0,255,0),2)
                    cv2.putText(frame,text,(startX,Y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
                    if (SerialConn == True) and (toggle != "ACK") :
                        print("ACK")
                        toggle = "ACK"
                        ArduinoSerial.write(ACK)
    
    if SerialConn == True:
        byte = ArduinoSerial.read()
        try:
            byte = int.from_bytes(byte,"big")
        except:
            byte=0x00
    
        THROTTEL = "OFF"
        ENGINE = "OFF"
        KEY = "OFF"

        if byte & 0x80:
            THROTTEL = "ON"
        if byte & 0x40:
            ENGINE = "ON"
        if byte & 0x20:
            KEY = "ON"
        
        GEAR = 0x0F & byte
    
    try:
        txt = "Throttle: {}\n\nHelmet: {}\n\nEngine: {}\n\nGear: {}\n\nKey: {}".format(THROTTEL,HELMET,ENGINE,GEAR,KEY)
        MC_satate.set(txt)
        Image_temp = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        Image_temp = ImageTk.PhotoImage(Image.fromarray(Image_temp))
        Image_Label['image'] = Image_temp
        window.update()
    except:
        run = False
    
ArduinoSerial.close()
vid.release()
cv2.destroyAllWindows()

#                x x x x  x x x x
#                ^ ^ ^    ^ ^ ^ ^
#     Throttel___| | |    |_|_|_|___Gear count
#         Engine___| |
#              Key___|
