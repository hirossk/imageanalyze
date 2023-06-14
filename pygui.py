#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import os
casceade_path = os.path.join(
        cv2.data.haarcascades, "haarcascades\\haarcascade_frontalface_alt.xml"
    )

cascadeface = cv2.CascadeClassifier("haarcascades\\haarcascade_frontalface_alt.xml")
cascadeeye = cv2.CascadeClassifier("haarcascades\\haarcascade_eye.xml")
cascadesmile = cv2.CascadeClassifier("haarcascades\\haarcascade_smile.xml")

def main():

    sg.theme('Black')

    # efine the window layout
    layout = [[sg.Text('OpenCV Demo', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image')],
              [sg.Button('Record',key='Record2', size=(10, 1), font='Helvetica 14'),
               sg.Button('Edge', size=(10, 1), font='Helvetica 14'),
               sg.Button('Face', size=(10, 1), font='Helvetica 14'),
               sg.Button('Eye', size=(10, 1), font='Helvetica 14'),
               sg.Button('Smile', size=(10, 1), font='Helvetica 14'), ],
              [sg.Button('Record',key='Record', size=(10, 1), font='Helvetica 14'),
               sg.Button('Edge', size=(10, 1), font='Helvetica 14'),
               sg.Button('Stop', size=(10, 1), font='Helvetica 14'),
               sg.Button('Stop', size=(10, 1), font='Helvetica 14'),
               sg.Button('Exit', size=(10, 1), font='Helvetica 14'), ]]

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

    while True:
        event, values = window.read(timeout=20)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            return
        elif event == 'Record':
            recordingflg = not recordingflg
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

        if recordingflg:
            ret, frame = cap.read()
            if edgeflg:
                frame = cv2.Canny(frame,100,200)
            if faceflg:
                face_list = cascadeface.detectMultiScale(frame)
                if len(face_list) > 0 :
                    #できたとき
                    for face in face_list :
                        x, y, w, h = face 
                        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)),
                                       (255,255,0), thickness=2) 
            if eyeflg:
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
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)


main()