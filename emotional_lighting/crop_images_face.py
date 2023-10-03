import cv2
import os

counter=0
directory = r'C:\REMOVED FOR PRIVACY'
foldername = "Happy/"
for filename in os.listdir(directory):
    print(filename)
    # Read the input image
    img = cv2.imread(foldername + filename)
    # Convert into grayscale
    #print(filename)
    #print(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Load the cascade
    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Detect faces
    #improved the parameters because before it was detecting random objects
    #now it's mainly detecting my face
    faces = face_classifier.detectMultiScale(gray_img, 1.9, 8)
    #this is the same code as the facial detection, except I am applying it to existing images
    # Draw rectangle around the faces and crop the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
        roi_gray = gray_img[y:y + h, x:x + w]
        roi_gray=cv2.resize(roi_gray,(48,48),interpolation=cv2.INTER_AREA)
        #cv2.imshow("face",roi_gray)
        cv2.imwrite(foldername + str(counter) + '.jpg', roi_gray)  
    # Display the output
    #cv2.imwrite('detcted.jpg', img)
    #resize_image = cv2.resize(img,(1000,700))
    #cv2.imshow('img', resize_image)
    #cv2.waitKey()
    counter+=1