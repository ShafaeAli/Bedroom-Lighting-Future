# Credit to karansjc1 for the pretrained emotion detection h5 model: https://github.com/karansjc1/emotion-detection

from keras.models import load_model
# from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
import cv2
import numpy as np
import tensorflow as tf
####################################################################
import requests
#import json

import time

import os

import urllib.request

from pytictoc import TicToc
import csv
import datetime
import http.client
import urllib

import gspread

import numpy as np

###############################################################################
HEADER = ['TIME','Angry','Happy','Neutral','Sad','Surprise']

token = "REMOVED FOR PRIVACY"

headers = {
    "Authorization": "Bearer %s" % token,
}
###############################################################################
brightness_val=1
colour_vals=['red','yellow','white','blue','pink']
#################################################################################
def lifx_colour_update(emotion):
    #print("emotion")
    light_col = combined_dict[emotion]
    if emotion != "Neutral":
        payload = {
            "power": "on",
            "brightness":brightness_val,
            "color":light_col
}
        #print(light_col)
        response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)
    return
#################################################################################
gc = gspread.oauth()
now_start = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#################################################################################
# https://towardsdatascience.com/a-guide-to-face-detection-in-python-3eab0f6b9fc1
# This is built in to capture faces
face_classifier=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

model = load_model('EmotionDetectionModel.h5')
#model = load_model('myface3_actual.h5')

class_labels=['Angry','Happy','Neutral','Sad','Surprise']

label=[]
#############################################################################
combined_zip=zip(class_labels,colour_vals)
combined_dict=dict(combined_zip)
prediction_list=[]
#############################################################################
t = TicToc()
ip_list = ['REMOVED FOR PRIVACY']
#############################################################################
def average_values(prediction_list):
    #print(prediction_list)
    prediction_list_avg=np.mean(prediction_list, axis=0)
    #print(prediction_list_avg)
    time_date = datetime.datetime.now(datetime.timezone.utc)
    return time_date, prediction_list_avg

#############################################################################
# Returns a value if the camera is open or not, otherwise just used to start camera
cap=cv2.VideoCapture(0)
if not cap.isOpened():
    print("camera isn't plugged in!")
    exit()

t.tic()

with open(now_start + 'emotion.csv','w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(HEADER)

    while True:
        #capature frames and returns boolean value if it is true
        #returns numpy array from frame,  [ 80  83  84] [ 83  86  87] [ 85  88  89]]]
        ret,frame=cap.read()
        if(not ret):
            print("camera still isn't working, check drivers")
            break

        labels=[]
        #converts the frame into colour to gray
        gray_img=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        #the face classifier xml is used to detect grayscale image of my face [[276 107 168 168]]
        #essentially used to find my face and then rectangles can be drawn from it
        #parameters are an input array image, scaleFactor and minNeighbours
        #### setting minneighbours higher should reduce false positives - I chagned it from 5 to 8 as it was
        #### detecting my shirt
        #####scale factor is a tradeoff between detection accuracy and speed.
        #####Haar-like features are robust to small variation in scale, so dont need to make it small,
        #####Just a waste of time to do that. Therefore default is 1.3 and not smaller
        ##### source https://stackoverflow.com/questions/51132674/meaning-of-parameters-of-detectmultiscalea-b-c
        #Haar is good because it is a square detection mode
        faces=face_classifier.detectMultiScale(gray_img,1.3,8)

        #4 coordiantes of end points from face detection
        for (x,y,w,h) in faces:
            #draws a rectangle, takes the frame, gray image is passed to the model
            #provide a start point, then end point
            #then give rectangle colour in RGB
            #thickness of rectangle
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,255),2)

            #region of interest
            #anything passed to the model will be handled in gray
            #just need to cut the face out of the image using coordiantes of face detected
            roi_gray=gray_img[y:y+h,x:x+w]
            #resize image to ensure it is correct
            #48x48 image size for model trained, colour channel is gray
            roi_gray=cv2.resize(roi_gray,(48,48),interpolation=cv2.INTER_AREA)

            #image pixels = tf.keras.preprocessing.image.img_to_array(roi_gray)
            #image_pixels=np.epand_dims(image_pixels,axis=0)

            if np.sum([roi_gray])!=0:
                roi=roi_gray.astype('float')/255.0
                roi=img_to_array(roi)
                roi=np.expand_dims(roi,axis=0)

                #these are the predictions for each of the labels
                #prediction based on h5 model
                prediction=model.predict(roi)[0]
                #return the index of the variable with the highest probability
                #assigns the highest value based on the class labels defined at the start
                label=class_labels[prediction.argmax()]
                #positions label on edge of face box
                label_position=(x,y)
                #places the label on the frame
                #font scale, colour and thickness
                cv2.putText(frame,label,label_position,cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)

        resize_image = cv2.resize(frame,(1000,700))
        #cv2.imshow('Emotion',roi_gray)
        cv2.imshow('Emotion',resize_image)

        blank_image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
        #cv2.imshow('Emotion',blank_image)
        ###############################################################################################
        #instant saving at same rate of FPS
        # angry=prediction[0]
        # happy=prediction[1]
        # neutral=prediction[2]
        # sad=prediction[3]
        # suprise=prediction[4]  
        # time_date = datetime.datetime.now(datetime.timezone.utc)
        #csv_writer.writerow([time_date, angry, happy, neutral, sad, suprise])

        prediction_list.append(prediction)
        # averaging last 30 values then writing those to CSV, saves on amount of data 
        if len(prediction_list) >= 30:
            prediction_array = np.array(prediction_list)
            time_date, prediction_list_avg=average_values(prediction_array)
            prediction_list = []
            angry = prediction_list_avg[0]
            happy = prediction_list_avg[1]
            neutral = prediction_list_avg[2]
            sad = prediction_list_avg[3]
            suprise = prediction_list_avg[4]
            csv_writer.writerow([time_date, angry, happy, neutral, sad, suprise])

        #print(prediction_list)
        
        if label != "Neutral":
           lifx_colour_update(label)

########################################################################################################
        elapsed = t.tocvalue()
        if elapsed > 120:
            for ip in ip_list:
                response = os.popen(f"ping {ip}").read()
                if "Received = 4" in response:
                    print(f"UP {ip} Ping Successful")
                    t.toc(restart=True)
                else:
                    print(f"DOWN {ip} Ping Unsuccessful")
                    cap.release()
                    cv2.destroyAllWindows()
                    break
######################################################################################################
        #when q is pressed it breaks the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
######################################################################################################
# apiKey = 'REMOVED FOR PRIVACY' 
# csvResults=""
# with open((today + 'emotion.csv'), 'r') as readFile:
#     reader = csv.DictReader(readFile)   
#     for row in reader: #for each row in the CSV
#         print(row['TIME'], row['Angry']) #See the rows in CSV file
#         TIME = row['TIME']
#         field1 = row['Angry']
#         field2 = row['Happy']
#         field3 = row['Neutral']
#         field4 = row['Sad']
#         field5 = row['Surprise']
#         csvResults += (f"{TIME}, {field1}, {field2},{field3},{field4},{field5}|") #This will append each row to a string
# csvParams = urllib.parse.urlencode({'write_api_key': apiKey,'time_format': "absolute", 'updates': csvResults})
# csvHeaders = {"Content-Type": "application/x-www-form-urlencoded"}
# csvConn = http.client.HTTPConnection("api.thingspeak.com:80")
# print("Attempting to write CSV to ThingSpeak")
# csvConn.request("POST", "/channels/REMOVED/bulk_update.csv", csvParams, csvHeaders)
# csvResponse = csvConn.getresponse()
# print("Upload status: ", csvResponse.status, csvResponse.reason)
# print("CSV upload successful!")
####################################################################################################
end = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
sh = gc.create(now_start + '_TO_' + end)
content = open(now_start + 'emotion.csv', 'r').read()
gc.import_csv(sh.id, content)
####################################################################################################
cap.release()
cv2.destroyAllWindows()
#very important to release the capture to release resources
#print(data)

