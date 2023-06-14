import os
import cv2
import numpy as np
import pprint
from convert import convertframe
import boto3
from tempfile import gettempdir

def detect_labels_local_file(photo,orgframe):
    client=boto3.client('rekognition')
    window = (1024,600)
    frame2 = cv2.resize(orgframe,window)
    with open(photo, 'rb') as image:
        photoimg = image.read()
        textresp = client.detect_text(Image={'Bytes': photoimg})
        labelresp = client.detect_labels(Image={'Bytes': photoimg})
    # pprint.pprint(labelresp)
    print('Detected labels in ' + photo) 
    for label in labelresp['Labels']:
        print (label['Name'] + ' : ' + str(label['Instances']))
        if label['Instances'] != None:
            for instance in  label['Instances']:
                print('BoundingBox : ' + str(instance['BoundingBox']))
                left = int(instance['BoundingBox']['Left'] * 1024)
                top = int(instance['BoundingBox']['Top'] * 600)
                width = int(instance['BoundingBox']['Width'] * 1024)
                height = int(instance['BoundingBox']['Height'] * 600)
                print(str(left) + ":" + str(top)+ ":" + str(width)+ ":" + str(height))
                cv2.rectangle(frame2,(left,top),(width+left,height+top) , color=(0, 0, 255), thickness=2) 
    
    for label in textresp['TextDetections']:
        print ('Text is : ' + str(label['DetectedText']) + '\n' +
               str(label['DetectedText']) + str(label['Geometry']['BoundingBox']))
    # pprint.pprint(textresp['TextDetections'])
    cv2.imshow('探知',frame2)
    return len(labelresp['Labels'])

def main():
    var = 0
    # VideoCapture オブジェクトを取得します
    capture = cv2.VideoCapture(0)

  
    while(True):
        ret, frame = capture.read()
        # resize the window
        window = (1024,600)
        frame1 = cv2.resize(frame,window)
        #グレイ映像の出力
        cv2.imshow('camera',frame1)

        #キー入力で終了します
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        if key & 0xFF == ord('s'):
            result = cv2.imwrite("detect.jpg",frame1)
            detect_labels_local_file("detect.jpg",frame1)
            print(result)
#        if key & 0xFF == ord('u'):
#            if var < 200:
#                var = var + 10
#        if key & 0xFF == ord('d'):
#            if var > -200:
#                var = var - 10

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    
