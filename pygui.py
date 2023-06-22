#!/usr/bin/env python
import PySimpleGUI as sg
import numpy as np
import cv2
from parts import *

# 画面レイアウトの作成
layout = [[title],
          [image],
          #ここにボタンを追加する
          ]

def main():
    # 画面の生成
    window = buildwindow(layout)
    # 入力を待ってループする
    cap = cv2.VideoCapture(0)
    
    # 各ボタンのオンオフを確認するフラグ
    recordingflg = False
    edgeflg = False
    faceflg = False
    eyeflg = False
    circleflg = False
    rectflg = False
    # スライダーの初期値
    gamma = 0

    while True:
        event, values = window.read(timeout=100)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            #終了ボタンが押された
            return
        if event == 'Record':
            #撮影ボタンが押された
            recordingflg = not recordingflg
            # 押されたときに白黒反転させる
            window['Record'].update(text='撮影中' if recordingflg else '撮影開始',
                                    button_color='white on black' if recordingflg else 'black on white')
            if recordingflg == False:
                #カメラによる撮影を終了する
                img = np.full((1, 1), 0)
                imgbytes = cv2.imencode('.png', img)[1].tobytes()
                window['image'].update(data=imgbytes)
                #カメラによる撮影の停止
                cap.release()
            else:
                #カメラによる撮影を開始
                if cap.isOpened() == False:
                    cap = cv2.VideoCapture(0)
        # 各種検出機能のオンオフ


        #四角形の検出


        if event == 'Circle':
            circleflg = not circleflg
            if circleflg == False:
                cv2.destroyWindow('circle')

        if event == 'Edge':
            edgeflg = not edgeflg

        if event == 'Slider':
            gamma = int(values['Slider'])

        if recordingflg:
            _, frame = cap.read()
            if edgeflg:
                frame = cv2.Canny(frame,100,200)
            if faceflg:
                face_list = cascadeface.detectMultiScale(frame)
                if len(face_list) > 0 :
                    #顔の検出ができたとき
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
                                            param1=90,param2=65,minRadius=50,maxRadius=200)
                
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0,:]:
                        # 円が判定できたときに円を書く
                        cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
            if rectflg:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, bw = cv2.threshold(gray, gamma, 255, cv2.THRESH_BINARY |cv2.THRESH_BINARY_INV)
                frame = findRect(bw, frame)
                # 四角を判定するための２値化した画面を描画する
                cv2.imshow('rect',bw)

            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)

if __name__ == "__main__":
    main()
  
