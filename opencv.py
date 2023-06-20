import cv2
import numpy as np
import pprint
import boto3
from tempfile import gettempdir
import PySimpleGUI as sg
REGION = 'us-east-1'
SRC_LANG = 'en'
TRG_LANG = 'ja'

def buildwindow():
    sg.theme('Black')
    font = ('Meiryo UI',13)
    buttonsize = (7,1)
    # efine the window layout
    layout = [[sg.Text('画像解析デモ', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image')],
              [sg.Button('撮影開始',key='Record', size=buttonsize, font=font),
            #    sg.Button('Edge',key='Edge', size=buttonsize, font=font),
                sg.Button('Face', key='Face',size=buttonsize, font=font),
            #    sg.Button('Eye', key='Eye',size=buttonsize, font=font),
                # sg.Button('Circle', key='Circle',size=buttonsize, font=font),
                # sg.Button('Square',key='Square', size=buttonsize, font=font),
               sg.Button('Exit',key='Exit', size=buttonsize, font=font),  ],
               [
                #    sg.Slider(key = 'Slider',enable_events=True,size=(73,10),
                #           range=(0,255),resolution=1,orientation='h')
                          ]]

    # ウィンドウの表示
    window = sg.Window('画像処理・認識プログラム',
                       layout, location=(200, 200))
    return window

def detect_labels_local_file(photo,orgframe,findlabel):
    client=boto3.client('rekognition', region_name=REGION)

    translate = boto3.client('translate', region_name=REGION)

    window = (1024,600)
    frame2 = cv2.resize(orgframe,window)
    # with open(photo, 'rb') as image:
    #     photoimg = image.read()
    #     textresp = client.detect_text(Image={'Bytes': photoimg})
    #     labelresp = client.detect_labels(Image={'Bytes': photoimg})

    # print('Detected labels in ' + photo) 
    # for label in labelresp['Labels']:
    #     print (label['Name'] + ' : ' + str(label['Instances']))
    #     if label['Instances'] != None and label['Name'] == findlabel:
    #         for instance in  label['Instances']:
    #             print('BoundingBox : ' + str(instance['BoundingBox']))
    #             left = int(instance['BoundingBox']['Left'] * 1024)
    #             top = int(instance['BoundingBox']['Top'] * 600)
    #             width = int(instance['BoundingBox']['Width'] * 1024)
    #             height = int(instance['BoundingBox']['Height'] * 600)
    #             print(str(left) + ":" + str(top)+ ":" + str(width)+ ":" + str(height))
    #             cv2.rectangle(frame2,(left,top),(width+left,height+top) , color=(0, 0, 255), thickness=2) 
    
    # for label in textresp['TextDetections']:
    #     print ('Text is : ' + str(label['DetectedText']) + '\n' +
    #            str(label['DetectedText']) + str(label['Geometry']['BoundingBox']))
    #     boundingbox = label['Geometry']['BoundingBox']
    #     if len(str(label['DetectedText'])) > 20:
    #         left = int(boundingbox['Left'] * 1024)
    #         top = int(boundingbox['Top'] * 600)
    #         width = int(boundingbox['Width'] * 1024)
    #         height = int(boundingbox['Height'] * 600)
    #         cv2.rectangle(frame2,(left,top),(width+left,height+top) , color=(0, 0, 255), thickness=2) 
    #         response = translate.translate_text(
    #             Text=label['DetectedText'],
    #             SourceLanguageCode='auto''',
    #             TargetLanguageCode=TRG_LANG
    #             )
    #         print( response )
    #         cv2.putText(frame2,text=response['TranslatedText'],org=(left, top),  fontScale=5,color=(255,255,255))
    cv2.putText(frame2,text='test',org=(30 ,30), fontFace=cv2.font, fontScale=5,color=(255,255,255))
    #         print( response )
    cv2.imshow('detect',frame2)
    # return len(labelresp['Labels'])

def main():
    window = buildwindow()
    # VideoCapture オブジェクトを取得します
    capture = cv2.VideoCapture(0)
 
    while(True):
        event, values = window.read(timeout=100)
        
        if event == sg.WIN_CLOSED:
            #終了ボタンが押された
            return
        ret, frame = capture.read()

        if event == 'Face':
            result = cv2.imwrite("detect.jpg",frame)
            detect_labels_local_file("detect.jpg",frame, event)
            print(result)

        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    
