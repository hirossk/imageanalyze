from PIL import ImageFont, ImageDraw, Image
import numpy as np
import PySimpleGUI as sg
import cv2
import json

sg.theme('Black')
font = ('Meiryo UI',11)
buttonsize = (8,1)
pad=((7,7),(2,2))
#画面部品の準備
title = sg.Text('画像解析デモ', size=(40, 1), justification='center', font='Helvetica 20')
image = sg.Image(filename='', key='image')
recordbutton = sg.Button('撮影開始',key='Record', size=buttonsize,pad=pad, font=font)
facebutton = sg.Button('顔検出', key='Face',size=buttonsize,pad=pad, font=font)
labelbutton = sg.Button('ラベル検出', key='Label',size=buttonsize,pad=pad, font=font)
textbutton = sg.Button('テキスト',key='Text', size=buttonsize,pad=pad, font=font)
celebbutton = sg.Button('有名人検出', key='Celeb',size=buttonsize,pad=pad, font=font)
transbutton = sg.Button('翻訳',key='Trans', size=buttonsize,pad=pad, font=font)
exitbutton =  sg.Button('終了',key='Exit', size=buttonsize,pad=pad, font=font)
slider = sg.Slider(key = 'Slider',enable_events=True,size=(73,10),
                   range=(0,255),resolution=1,orientation='h')


DIMW=800
DIMH=600
window = (DIMW,DIMH)
photo='detect.jpg'

#共通前処理
def com_image(photo,frame):
    
    result = cv2.imwrite(photo,frame)
    with open(photo, 'rb') as image:
        #カメラ画像を読み込む
        photoimg = image.read()
    return cv2.resize(frame,window),photoimg
#文字列描画
def putText(img, text, point, size, color):
    # 遊ゴシック
    font = ImageFont.truetype('C:\\Windows\\Fonts\\msgothic.ttc', size,index=0)

    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)

    #テキスト描画
    draw.text(point, text, fill=color, font=font,)

    #pillowからCV2で表示できる形式へ変換
    return np.array(img_pil)

def buildwindow(layout):
    # ウィンドウの表示
    window = sg.Window('画像処理・認識プログラム',
                       layout, location=(200, 200))
    return window

def getDim(boundingbox):
    left = int(boundingbox['Left'] * DIMW)
    top = int(boundingbox['Top'] * DIMH)
    width = int(boundingbox['Width'] * DIMW)
    height = int(boundingbox['Height'] * DIMH)
    return left,top,width,height

def drawfacebox(faceresp,frame):
    for label in faceresp['FaceDetails']:
        boundingbox = label['BoundingBox']
        left,top,width,height=getDim(boundingbox)
        cv2.rectangle(frame,(left,top),(width+left,height+top) , color=(0, 0, 255), thickness=2) 

def drawtextbox(textresp,frame,LENGTH):
    for label in textresp['TextDetections']:
        boundingbox = label['Geometry']['BoundingBox']
        if len(str(label['DetectedText'])) > LENGTH:
            left,top,width,height=getDim(boundingbox)
            cv2.rectangle(frame,(left,top),(width+left,height+top) , color=(0, 0, 255), thickness=2) 

def drawtexttrans(textresp,frame,color=(255,255,255)):
    pass

def outputjson(filename,contents):
    f = open(filename, 'w', encoding='UTF-8')
    json.dump(contents, f, ensure_ascii=False, 
              indent=4, sort_keys=True, separators=(',', ': '))
    pass