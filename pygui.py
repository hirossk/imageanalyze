#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import os
casceade_path = os.path.join(
        cv2.data.haarcascades, "haarcascades\\haarcascade_frontalface_alt.xml"
    )

cascadeface = cv2.CascadeClassifier("haarcascades\\haarcascade_frontalface_alt.xml")
cascadeeye = cv2.CascadeClassifier("haarcascades\\haarcascade_eye_tree_eyeglasses.xml")
cascadesmile = cv2.CascadeClassifier("haarcascades\\haarcascade_smile.xml")

def main():

    sg.theme('Black')

    # efine the window layout
    layout = [[sg.Text('画像解析デモ', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image')],
              [sg.Button('撮影開始',key='Record', size=(8, 1), font='Helvetica 14'),
               sg.Button('Edge', size=(8, 1), font='Helvetica 14'),
               sg.Button('Face', size=(8, 1), font='Helvetica 14'),
               sg.Button('Eye', size=(8, 1), font='Helvetica 14'),
               sg.Button('Circle', size=(8, 1), font='Helvetica 14'),
               sg.Button('Exit', size=(8, 1), font='Helvetica 14'),  ],]

    # ウィンドウの表示
    window = sg.Window('画像処理・認識プログラム',
                       layout, location=(200, 200))

    # 入力を待ってループする
    cap = cv2.VideoCapture(0)
    
    recordingflg = False
    edgeflg = False
    faceflg = False
    eyeflg = False
    smileflg = False
    circleflg = False

    while True:
        event, values = window.read(timeout=100)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            return
        elif event == 'Record':
            recordingflg = not recordingflg
            window['Record'].update(text='撮影中' if recordingflg else '撮影開始',button_color='white on black' if recordingflg else 'black on white')
        elif event == 'Stop':
            recordingflg = False
            img = np.full((1, 1), 0)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)
        elif event == 'Edge':
            edgeflg = not edgeflg
        elif event == 'Face':
            faceflg = not faceflg
        elif event == 'Eye':
            eyeflg = not eyeflg
        elif event == 'Smile':
            smileflg = not smileflg
        elif event == 'Circle':
            circleflg = not circleflg
        if recordingflg:
            ret, frame = cap.read()
            if edgeflg:
                frame = cv2.Canny(frame,100,200)
            elif faceflg:
                face_list = cascadeface.detectMultiScale(frame)
                if len(face_list) > 0 :
                    #できたとき
                    for face in face_list :
                        x, y, w, h = face 
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (255,255,0), thickness=2) 
            elif eyeflg:
                eye_list = cascadeeye.detectMultiScale(frame)
                if len(eye_list) > 0 :
                    #できたとき
                    for eye in eye_list :
                        x, y, w, h = eye 
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (255,128,255), thickness=2) 
            if smileflg:
                smile_list = cascadesmile.detectMultiScale(frame)
                if len(smile_list) > 0 :
                    #できたとき
                    for smile in smile_list :
                        x, y, w, h = smile
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (128,128,255), thickness=2) 
                        
            if circleflg:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 5)
                
                
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,dp=1,minDist=70,
                                            param1=100,param2=80,minRadius=50,maxRadius=300)
                
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    
                    for i in circles[0,:]:
                        # draw the outer circle
                        cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
                
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)


main()