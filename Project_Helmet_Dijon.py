import os
import numpy as np
import cv2
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

model=keras.models.load_model('helmet.h5')

shoulder_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
my_vid = cv2.VideoCapture('test.mp4')
while True:
    ret,frame = my_vid.read()
    if ret:
        frame = cv2.resize(frame,(400,700))
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        shoulder = shoulder_cascade.detectMultiScale( gray,1.1,6)
        for (x,y,w,h) in shoulder:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            temp = frame[y:y+h,x:x+w]
            temp=cv2.cvtColor(temp,cv2.COLOR_BGR2RGB)
            temp=cv2.resize(temp,(224,224))
            temp=preprocess_input(temp)
            temp=np.expand_dims(temp,axis=0)
            pred_val=model.predict(temp)
            print(pred_val)
            pred_val=np.ravel(pred_val).item()

            if pred_val < 0.7 :
                text = 'NO-HELMET'+ str(pred_val)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                cv2.putText(frame,text,(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            else:
                text = 'HELMET'+ str(pred_val)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(frame,text,(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv2.imshow('image',frame)
        cv2.waitKey(200)
        if cv2.waitKey(1) == ord('e'):
            break
    else:
        my_vid.set(cv2.CAP_PROP_POS_FRAMES,0)

cv2.destroyAllWindows()
