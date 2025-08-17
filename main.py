import cv2 as cv
import numpy as np
import os
from cvzone.HandTrackingModule import HandDetector

width= 1100
height=600

cap=cv.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)
folder='Hand gesture controlled slide presentation\Presentation'

# stores the images path as a list from the folder
pathImg=sorted(os.listdir(folder))
print(pathImg)

imgNumber=0
gestureThreshold=300

# for slide to move one by one when gesture is shown
isButtonPressed=False
buttonCount=0
buttonDelay=25

# for drawing
drawings=[[]]
drawingsIndex=0
drawingsStart=False 

detector= HandDetector(detectionCon=0.8,maxHands=1)

while True:
    success,frame= cap.read()
    if not success:
        break
    
    frame =cv.flip(frame,1)
    
    # convert to images from their paths
    slides=os.path.join(folder,pathImg[imgNumber])
    img=cv.imread(slides)
    img=cv.resize(img,(width,height))

    # find hand landmarks
    hands,frame =detector.findHands(frame)
    cv.line(frame,(0,gestureThreshold),(1280,gestureThreshold),(0,255,0),10)
    
    if hands and (not isButtonPressed):
        hand= hands[0]
        fingers= detector.fingersUp(hand)
        cx,cy= hand['center']
        lmList = hand['lmList']

        # confrain the range for easy drawing
        xCor = int(np.interp(lmList[8][0],[width//2,w],[0,width]))
        yCor = int(np.interp(lmList[8][1],[150, height-150],[0,height]))
        indexFinger= xCor,yCor

        if cy<=gestureThreshold:
            drawingsStart=False

            # gesture to move to the previous slide
            if fingers==[1,0,0,0,0]:
                drawingsStart=False 
                print('left')
                if imgNumber>0:
                    isButtonPressed=True
                    # to remove drawings when moved to previous slide
                    drawings=[[]]
                    drawingsIndex=0
                    imgNumber-=1
            
            # gesture to move to the next slide
            if fingers==[0,0,0,0,1]:
                drawingsStart=False 
                print('right')
                if imgNumber<len(pathImg)-1:
                    isButtonPressed=True
                    # to remove drawings when moved to next slide
                    drawings=[[]]
                    drawingsIndex=0
                    imgNumber+=1
            
        # gesture for showing pointer
        if fingers==[0,1,1,0,0]:
            print('show pointer')
            cv.circle(img,(indexFinger),12,(0,0,255),cv.FILLED)
        
        # gesture for drawing the pointer
        if fingers==[0,1,0,0,0]:
            print('Draw')
            if not drawingsStart:
                drawingsStart=True
                drawingsIndex+=1
                drawings.append([])
            cv.circle(img,(indexFinger),12,(0,0,255),cv.FILLED)
            drawings[drawingsIndex].append(indexFinger)
        else:
            drawingsStart=False

        # gesture to erase the recent drawing
        if fingers==[0,1,1,1,0]:
            print('Erase')
            if drawings:
                if drawingsIndex >=0:
                    isButtonPressed=True
                    drawings.pop(-1)
                    drawingsIndex-=1

    
    # display the images one by one ( button pressed iterations)
    if isButtonPressed:
        buttonCount+=1
        if buttonCount > buttonDelay:
            buttonCount=0
            isButtonPressed=False

    # to display all the drawings from drawings list
    for i in range(len(drawings)):
        for j in range(len(drawings[i])):
            if j!=0:
                cv.line(img,drawings[i][j-1],drawings[i][j],(0,0,200),12)


    # adding the webcam image on the slides
    frameOverlap= cv.resize(frame,(180,120))
    h,w,_= img.shape
    img[0:120,w-180:w]=frameOverlap

    cv.imshow("image",frame)
    cv.imshow("Slides",img)
    key=cv.waitKey(1)
    if key==ord('q'):
        break

cap.release()
cv.destroyAllWindows()