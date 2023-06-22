#!/usr/bin/env python
import math
import cv2
import PySimpleGUI as sg
sg.theme('Black')
font = ('Meiryo UI',12)
buttonsize = (7,1)
#画面部品の準備
title = sg.Text('画像解析デモ', size=(40, 1), justification='center', font='Helvetica 20')
image = sg.Image(filename='', key='image')
recordbutton = sg.Button('撮影開始',key='Record', size=buttonsize, font=font)
facebutton = sg.Button('顔検出', key='Face',size=buttonsize, font=font)
eyebutton = sg.Button('目検出', key='Eye',size=buttonsize, font=font)
edgebutton = sg.Button('エッジ',key='Edge', size=buttonsize, font=font)
circlebutton = sg.Button('円検出', key='Circle',size=buttonsize, font=font)
rectbutton = sg.Button('四角検出',key='Rect', size=buttonsize, font=font)
exitbutton =  sg.Button('終了',key='Exit', size=buttonsize, font=font)
slider = sg.Slider(key = 'Slider',enable_events=True,size=(73,10),
                   range=(0,255),resolution=1,orientation='h')

#顔検出のカスケード準備
cascadeface = cv2.CascadeClassifier("haarcascades\\haarcascade_frontalface_alt.xml")
cascadeeye = cv2.CascadeClassifier("haarcascades\\haarcascade_eye_tree_eyeglasses.xml")
# pt0-> pt1およびpt0-> pt2からの
# ベクトル間の角度の余弦(コサイン)を算出
def angle(pt1, pt2, pt0) -> float:
    dx1 = float(pt1[0,0] - pt0[0,0])
    dy1 = float(pt1[0,1] - pt0[0,1])
    dx2 = float(pt2[0,0] - pt0[0,0])
    dy2 = float(pt2[0,1] - pt0[0,1])
    v = math.sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) )
    return (dx1*dx2 + dy1*dy2)/ v

# 画像上の四角形を検出
def findRect(bin_image, image, cond_area = 1000):
    # 輪郭取得
    contours, _ = cv2.findContours(bin_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for i, cnt in enumerate(contours):
        # 輪郭の周囲に比例する精度で輪郭を近似する
        arclen = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, arclen*0.02, True)

        #四角形の輪郭は、近似後に4つの頂点があります。
        #比較的広い領域が凸状になります。

        # 凸性の確認 
        area = abs(cv2.contourArea(approx))
        if approx.shape[0] == 4 and area > cond_area and cv2.isContourConvex(approx) :
            maxCosine = 0

            for j in range(2, 5):
                # 辺間の角度の最大コサインを算出
                cosine = abs(angle(approx[j%4], approx[j-2], approx[j-1]))
                maxCosine = max(maxCosine, cosine)

            # すべての角度の余弦定理が小さい場合
            #（すべての角度は約90度です）次に、quandrangeを書き込みます
            # 結果のシーケンスへの頂点
            if maxCosine < 0.5 :
                # 四角判定!!
                rcnt = approx.reshape(-1,2)
                cv2.polylines(image, [rcnt], True, (0,0,255), thickness=2, lineType=cv2.LINE_8)
    return image

def buildwindow(layout):
    sg.theme('Black')
    # efine the window layout

    # ウィンドウの表示
    window = sg.Window('画像処理・認識プログラム',
                       layout, location=(200, 100))
    return window