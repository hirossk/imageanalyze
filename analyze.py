import cv2
import boto3
from tempfile import gettempdir
import PySimpleGUI as sg
from util import *

#東京リージョン
REGION = 'ap-northeast-1'
SRC_LANG = 'auto'
TRG_LANG = 'ja'

#画像解析のエンジンへの接続
rekognition=boto3.client('rekognition', region_name=REGION)
#翻訳エンジンへの接続
translate = boto3.client('translate', region_name=REGION)

    # ウィンドウレイアウトの作成
layout = [  [title],
            [image],
            [recordbutton,
             labelbutton,
            exitbutton,
            facebutton,
            textbutton],
            [slider]]

def detect_faces(orgframe):
    frame,photoimg = com_image(photo,orgframe)

    #顔からデータの取り出し
    faceresp = rekognition.detect_faces(Image={ 'Bytes': photoimg},Attributes=['ALL'])

    drawfacebox(faceresp,frame)
    cv2.imshow('detect',frame)

def detect_text(orgframe):
    frame,photoimg = com_image(photo,orgframe)
        #写真からテキストデータの取り出し
    textresp = rekognition.detect_text(Image={'Bytes': photoimg})

    drawtextbox(textresp,frame,20)

    
    #         #翻訳機能の呼び出し
    #         response = translate.translate_text(
    #             Text=label['DetectedText'],
    #             SourceLanguageCode=SRC_LANG,
    #             TargetLanguageCode=TRG_LANG
    #             )
    #         print( response )
    #         # cv2.putText(frame2,text=response['TranslatedText'],org=(left, top),  fontScale=5,color=(255,255,255))
    #         frame = putText(frame, response['TranslatedText'], (left,top+25), 20, (25, 131, 255))

    cv2.imshow('detect',frame)

def detect_labels(orgframe):
    frame,photoimg = com_image(photo,orgframe)
    #ラベルデータの取り出し
    labelresp = rekognition.detect_labels(Image={'Bytes': photoimg})

    # 解析から返ってきたデータからラベル名(Name)と確度(Confidence)を整形して出力
    top = 5
    for label in labelresp['Labels']:
        str = "{Name:20}:{Confidence:.2f}%".format(**label)
        frame = putText(frame, str, (10,top), 20, (25, 131, 255))
        top = top + 25

    cv2.imshow('detect',frame)

def main():
    window = buildwindow(layout)
    # VideoCapture オブジェクトを取得します
    capture = cv2.VideoCapture(0)
 
    while(True):
        event, values = window.read(timeout=30)
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            #終了ボタンが押された
            break
        
        #カメラから画像読み込み
        _, frame = capture.read()

        if event == 'Face':
            detect_faces(frame)
        if event == 'Label':
            detect_labels(frame)
        if event == 'Text':
            detect_text(frame)
        #画面にイメージを出力する
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  
        window['image'].update(data=imgbytes)

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    
