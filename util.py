from PIL import ImageFont, ImageDraw, Image
import numpy as np
import PySimpleGUI as sg
import cv2
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import re
import pprint

#東京リージョン
REGION = 'ap-northeast-1'
polly = boto3.client('polly', region_name=REGION)
bedrock = boto3.client('bedrock', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

sg.theme('Black')
font = ('Meiryo UI',11)
buttonsize = (8,1)
pad=((7,7),(2,2))
#画面部品の準備
title = sg.Text('画像解析デモ', size=(40, 1), justification='center', font='Helvetica 20')
image = sg.Image(filename='', key='image')
recordbutton = sg.Button('撮影開始',key='record', size=buttonsize,pad=pad, font=font)
facebutton = sg.Button('顔検出', key='face',size=buttonsize,pad=pad, font=font)
labelbutton = sg.Button('物体検出', key='label',size=buttonsize,pad=pad, font=font)
textbutton = sg.Button('テキスト',key='text', size=buttonsize,pad=pad, font=font)
celebbutton = sg.Button('有名人検出', key='celeb',size=buttonsize,pad=pad, font=font)
transbutton = sg.Button('翻訳',key='trans', size=buttonsize,pad=pad, font=font)
exitbutton =  sg.Button('終了',key='exit', size=buttonsize,pad=pad, font=font)
pollybutton =  sg.Button('音声合成',key='polly', size=buttonsize,pad=pad, font=font)
bedrockbutton =  sg.Button('AIchat',key='bedrock', size=buttonsize,pad=pad, font=font)
slider = sg.Slider(key = 'slider',enable_events=True,size=(73,10),
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
    font = ImageFont.truetype('fonts\\NotoSansCJK.ttc', size,index=0)

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

def call_polly(speed = 85,VoiceId = 'Kazuha',filename = 'message.txt',Engine = 'neural'):
    #トークNTTS Kazuha Tomoko Takumi
    #謝辞メッセージ
    with open(filename, 'r', encoding='UTF-8') as f:
        data = f.read(-1)

    #スピードの変更や空白の挿入
    text = '<speak><prosody rate="' + str(speed) + '%">'
    #空白の挿入
    data = re.sub('bt=(\d+)s','<break time="\\1s"/>',data)
    data = re.sub('VoiceId',VoiceId,data)
    text = text + data
    text = text + '</prosody></speak>'
    if Engine == '':
        Engine = 'standard'
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                            TextType='ssml',
                                            VoiceId=VoiceId,Engine=Engine)
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.mp3")
                try:
                    # Open a file for writing the output as a binary stream
                        with open(output, "wb") as file:
                            file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
    # Play the audio using the platform's default player
    if sys.platform == "win32":
        os.startfile(output)
    else:
        # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, output])

def call_bedrock():
    """
    List the available Amazon Bedrock foundation models.

    :return: The list of available bedrock foundation models.
    """
    f = open('questions.txt', 'r', encoding='UTF-8')
    data = f.read(-1)
    prompt = """Human: """ + data + """
        
    Assistant:"""
    body = json.dumps(
        {
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        }
    )
    resp = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-v2:1",
        body=body,
        contentType="application/json",
        accept="application/json",
        )
    answer = resp["body"].read().decode()

    with open('answer.txt', mode='w', encoding='UTF-8') as f:
        f.write(json.loads(answer)["completion"])
    
    call_polly(filename = 'answer.txt',VoiceId='Takumi')



