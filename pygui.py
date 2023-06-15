#!/usr/bin/env python
import PySimpleGUI as sg
import numpy as np
import os
import cv2
from pyutil import findSquares
from pyutil import buildwindow
casceade_path = os.path.join(
        cv2.data.haarcascades, "haarcascades\\haarcascade_frontalface_alt.xml"
    )
cascadeface = cv2.CascadeClassifier("haarcascades\\haarcascade_frontalface_alt.xml")
cascadeeye = cv2.CascadeClassifier("haarcascades\\haarcascade_eye_tree_eyeglasses.xml")
#フラグのリセット


def main():

    window = buildwindow()
    # 入力を待ってループする
    cap = cv2.VideoCapture(0)
    
    recordingflg = False
    edgeflg = False
    faceflg = False
    eyeflg = False
    circleflg = False
    squareflg = False
    gamma = 0

    while True:
        event, values = window.read(timeout=100)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            #終了ボタンが押された
            return
        elif event == 'Record':
            #撮影ボタンが押された
            recordingflg = not recordingflg
            window['Record'].update(text='撮影中' if recordingflg else '撮影開始',
                                    button_color='white on black' if recordingflg else 'black on white')
            if recordingflg == False:
                #カメラによる撮影を終了する
                img = np.full((1, 1), 0)
                imgbytes = cv2.imencode('.png', img)[1].tobytes()
                window['image'].update(data=imgbytes)
                cap.release()
            else:
                #カメラによる撮影を開始したとき
                if cap.isOpened() == False:
                    cap = cv2.VideoCapture(0)

        # elif event == 'Edge':
        #     edgeflg = not edgeflg
        # elif event == 'Face':
        #     faceflg = not faceflg
        # elif event == 'Eye':
        #     eyeflg = not eyeflg
        # elif event == 'Circle':
        #     circleflg = not circleflg
            # if circleflg == False:
            #     cv2.destroyWindow('circle')
        # elif event == 'Square':
        #     squareflg = not squareflg
            # if squareflg == False:
            #     cv2.destroyWindow('square')
        # elif event == 'Slider':
        #     gamma = int(values['Slider'])

        if recordingflg:
            ret, frame = cap.read()
            if edgeflg:
                frame = cv2.Canny(frame,100,200)
            if faceflg:
                face_list = cascadeface.detectMultiScale(frame)
                if len(face_list) > 0 :
                    #顔検出ができたとき
                    for face in face_list :
                        x, y, w, h = face 
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (255,255,0), thickness=2) 
            if eyeflg:
                eye_list = cascadeeye.detectMultiScale(frame)
                if len(eye_list) > 0 :
                    #目の検出ができたとき
                    for eye in eye_list :
                        x, y, w, h = eye 
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (255,128,255), thickness=2) 
                        
            if circleflg:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 5)
                cv2.imshow('circle',gray)
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,dp=1,minDist=80,
                                            param1=70,param2=50,minRadius=50,maxRadius=200)
                
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    print(circles)
                    for i in circles[0,:]:
                        # draw the outer circle
                        cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
            if squareflg:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, bw = cv2.threshold(gray, gamma, 255, cv2.THRESH_BINARY |cv2.THRESH_BINARY_INV)
                frame = findSquares(bw, frame)
                cv2.imshow('square',bw)

            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)

main()