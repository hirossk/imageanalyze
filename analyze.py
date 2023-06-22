import cv2
import boto3
import PySimpleGUI as sg
from util import *
from pprint import pprint

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
            #各種ボタンの追加
            [recordbutton,
             exitbutton,
             labelbutton,
             facebutton,
             celebbutton,
             textbutton,
             transbutton]
            ]

frame = (DIMW,DIMH)

def detect_faces():
    imgframe,photoimg = com_image(photo,frame)

    #顔に関するデータの取り出し
    faceresp = rekognition.detect_faces(Image={ 'Bytes': photoimg},Attributes=['ALL'])

    drawfacebox(faceresp,imgframe)
    #顔から年齢を推定してみましょう
    #outputjson("face.json",faceresp)
    #text = str(faceresp['FaceDetails'][0][''])
    #print(text)
    #imgframe = putText(imgframe,text, (0,20), 25,(0,255,0))
    #cv2.imshow('detect',imgframe)


def detect_text():
    imgframe,photoimg = com_image(photo,frame)
        #写真からテキストデータの取り出し
    textresp = rekognition.detect_text(Image={'Bytes': photoimg})

    drawtextbox(textresp,imgframe,20)
    cv2.imshow('detect',imgframe)

    return textresp,imgframe


def trans_text():
    textresp,imgframe = detect_text()
    
    #文字列（テキストが見つかった時）
    for label in textresp['TextDetections']:
        boundingbox = label['Geometry']['BoundingBox']
        if len(str(label['DetectedText'])) > 20:
            #翻訳機能の呼び出し
            response = translate.translate_text(
                Text=label['DetectedText'],
                SourceLanguageCode=SRC_LANG,
                TargetLanguageCode=TRG_LANG
                )
            left,top,_,_=getDim(boundingbox)
            imgframe = putText(imgframe, response['TranslatedText'], (left,top+25), 25, (25, 131, 255))

    cv2.imshow('detect',imgframe)

def detect_labels():
    imgframe,photoimg = com_image(photo,frame)
    #ラベルデータの取り出し
    labelresp = rekognition.detect_labels(Image={'Bytes': photoimg})

    # 解析から返ってきたデータからラベル名(Name)と確度(Confidence)を整形して出力
    top = 5
    for label in labelresp['Labels']:
        str = "{Name:20}:{Confidence:.2f}%".format(**label)
        imgframe = putText(imgframe, str, (10,top), 25, (25, 131, 255))
        top = top + 25

    cv2.imshow('detect',imgframe)

def detect_celeb():
    imgframe,photoimg = com_image(photo,frame)
    #ラベルデータの取り出し
    celebresp = rekognition.recognize_celebrities(Image={'Bytes': photoimg})

    for celeb in celebresp['CelebrityFaces']:
        print("Celebrity")
        pprint(celeb)
    for face in celebresp['UnrecognizedFaces']:
        print("Face")
        pprint(face)

    # 解析から返ってきたデータからラベル名(Name)と確度(Confidence)を整形して出力
    # top = 5
    # for label in labelresp['Labels']:
    #     str = "{Name:20}:{Confidence:.2f}%".format(**label)
    #     imgframe = putText(imgframe, str, (10,top), 25, (25, 131, 255))
    #     top = top + 25

    # cv2.imshow('detect',imgframe)

def main():
    global frame
    recordingflg=False
    window = buildwindow(layout)
    # VideoCapture オブジェクトを取得します

 
    while(True):
        event, _ = window.read(timeout=30)
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            #終了ボタンが押された
            break
        
        #各種機能の追加
        if event == 'Face':
            detect_faces()
        if event == 'Label':
            detect_labels()
        if event == 'Text':
            detect_text()
        if event == 'Trans':
            trans_text()
        if event == 'Celeb':
            detect_celeb()

        if event == 'Record':
            #カメラから画像読み込み
            recordingflg = not recordingflg
            window['Record'].update(text='撮影中' if recordingflg else '撮影開始',
                        button_color='white on red' if recordingflg else 'black on white')
            if recordingflg == True:
                    capture = cv2.VideoCapture(0)
            else:
                #カメラによる撮影を終了する
                frame = np.full((1, 1), 0)
                capture.release()
        if recordingflg == True:
            _, frame = capture.read()
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  
        window['image'].update(data=imgbytes)

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    
